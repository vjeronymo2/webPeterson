# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 18:10:11 2020

@author: Amanco
"""
import numpy as np
import pickle
import glob
from scipy.spatial.distance import cdist
from itertools import accumulate, chain
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from sentence_transformers import SentenceTransformer
import torch
import re
from skimage.util import view_as_windows
import os

# Function to load pickle files
def loadPickle(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)
        file.close()
    return data

class semantic:
    def __init__(self):
        ''' PRE-LOAD NECESSARY DATA '''
        self.__sentence_model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
        self.__tokenizer = AutoTokenizer.from_pretrained("twmkn9/albert-base-v2-squad2")
        self.__model = AutoModelForQuestionAnswering.from_pretrained("twmkn9/albert-base-v2-squad2")


        # Read url file
        with open(os.path.join('data','urls.txt'), 'r') as file:
            self.urls = file.read().splitlines()
            file.close()
        with open(os.path.join('data','titles.txt'), 'r') as file:
            self.titles = file.read().splitlines()
            file.close()
        
        # Load pickle files into variables
        names = [os.path.join('data','punctuated.pkl'), os.path.join('data','punctuated_embed.pkl'), os.path.join('data','subs.pkl')]
        self.__punctuateds, self.__sentence_embeddings_p, self.__subs = tuple(map(loadPickle, names))
        
        ''' END OF PRE-LOAD NECESSARY DATA '''
        

    def similarity(self, query):
        queries_embeddings = self.__sentence_model.encode([query])
        distances = cdist(queries_embeddings, self.__sentence_embeddings_p, "cosine")
        self.matches = np.argsort(distances, axis=1)[0,:8]
        
        return [{'url': self.urls[i], 'title': self.titles[i]} for i in self.matches]
    
    def ask(self, question):
        # This will add CLK and SEP tokens to the question
        punctuated = self.__punctuateds[self.matches[0]]
        tokenized_question = self.__tokenizer.encode(question, add_special_tokens=False)
        self.__tokenized_text = self.__tokenizer.encode(punctuated, add_special_tokens=False) 
        # The chunksize will depend on the number of tokens of your question
        chunk_size = 512 -3 -len(tokenized_question)  
        print('Chunk size of', chunk_size)
        lastdot, firstdot = 0, -1
        chunks = []
        dot = self.__tokenizer.encode('Hello.', add_special_tokens=False)[-1]
        
        for i in range(len(self.__tokenized_text)):
            if self.__tokenized_text[i] == dot:    #9 is a dot
                if i-firstdot>chunk_size:
                    chunks.append(self.__tokenized_text[firstdot+1:lastdot+1])
                    firstdot = lastdot
                lastdot = i
        if lastdot != firstdot:
            chunks.append(self.__tokenized_text[firstdot+1:])
        outputs = []
        chunk_indexes = list(accumulate([0]+[len(i) for i in chunks][:-1]))
        #print(token_type_ids_list)
        for chunk, chunk_index in zip(chunks, chunk_indexes):
            input_dict = self.__tokenizer.encode_plus(tokenized_question, chunk,
                        return_tensors='pt', truncation='longest_first',
                        add_special_tokens=True)
            start_scores, end_scores = self.__model(**input_dict)
            start_scores[0,:len(tokenized_question)+2] = -10
            start_scores[0,-1] = -10
            start_index = torch.argmax(start_scores).item()
            end_scores[0,:start_index] = -10    #This will force argmax(end_scores) to have index higher than argmax(start_scores), hence, start_index < end_index
            end_scores[0,-1] = -10
            end_index = torch.argmax(end_scores).item()
            score = start_scores[0, start_index].item() + end_scores[0, end_index].item()
            input_ids = input_dict['input_ids'].flatten().tolist()
            # Find sentence which the answer is contained in
            if dot in input_ids[:start_index]:
                # Find index of before dot, if there is any
                before_dot = len(input_ids) -1 -input_ids[::-1].index(dot, len(input_ids) -1 -start_index)
            else:
                before_dot = len(tokenized_question)+2
            after_dot = input_ids.index(dot, end_index)
            sentence = self.__tokenizer.decode(input_ids[before_dot +1 : after_dot + 1])
            answer = self.__tokenizer.decode(input_ids[start_index : end_index + 1])
            
            output = {'global_index': start_index + chunk_index -len(tokenized_question) - 2,
              'sentence': sentence, 'answer': answer, 'score': score}
            outputs.append(output)
        outputs = sorted(outputs, key=lambda k: k['score'], reverse=True)[:3]
        timestamps = self.getTimestamp(outputs)
        for timestamp, output in zip(timestamps, outputs):
            output['timestamp'] = (timestamp.hour * 60 + timestamp.minute) * 60 + timestamp.second
        return outputs
    
    def getTimestamp(self, outputs):
        segments = self.__subs[self.matches[0]]
        global_indexes = [output['global_index'] for output in outputs]
        global_index_no_punct = []
        window_size = 10
        tokenized_text_no_punct = np.array(self.__tokenizer.encode(re.sub("[^\w\d'\s]+",'',
                                      self.__tokenizer.decode(self.__tokenized_text)),
                                      add_special_tokens=False))
        for index in np.array(global_indexes):
            # nearby variable is a sequence of words near the answer index
            if index < len(self.__tokenized_text)/2:
                nearby = self.__tokenized_text[index: index + window_size+1]
            else:
                nearby = self.__tokenized_text[index - window_size: index+1]
            nearby = self.__tokenizer.encode(re.sub("[^\w\d'\s]+",'',self.__tokenizer.decode(nearby)),
                     add_special_tokens=False)
            nearby = [i for i in nearby if i != 13]
            # Find where this order of words are located in the
            # https://stackoverflow.com/questions/45816229/how-to-get-the-index-of-a-list-items-in-another-list
            mask = tokenized_text_no_punct[:-len(nearby)+1]==nearby[0]
            mask[mask] = (view_as_windows(tokenized_text_no_punct,len(nearby))[mask]==
                          nearby).all(1)
            start = int(np.flatnonzero(mask)[:,None])
            if index >= len(self.__tokenized_text)/2:
                start = start + len(nearby) -1
            global_index_no_punct.append(start)
        # Find which segment of the subtitle, the whole text correspond to
        text2segment = [[num for i in self.__tokenizer.encode(re.sub("[^\w\d'\s]+",'',
               segment['text']), add_special_tokens=False)] for num, segment in
               enumerate(segments)]
        text2segment = list(chain.from_iterable(text2segment))
        seg_indexes = [text2segment[i] for i in global_index_no_punct]
        timestamp = [segments[i]['start'] for i in seg_indexes] 
        return timestamp
            # assert len(text2segment) == len(tokenized_text_no_punct)
    