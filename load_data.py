# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 11:23:43 2020

@author: Amanco
"""
import numpy as np
import pickle
import glob
from scipy.spatial.distance import cdist
from itertools import accumulate, chain
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from sentence_transformers import SentenceTransformer

# Function to load pickle files
def loadPickle(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)
        file.close()
    return data
def loadData():
    ''' PRE-LOAD NECESSARY DATA '''
    sentence_model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
    tokenizer = AutoTokenizer.from_pretrained("twmkn9/albert-base-v2-squad2")
    model = AutoModelForQuestionAnswering.from_pretrained("twmkn9/albert-base-v2-squad2")
    
    
    # Read url file
    with open('data/urls.txt', 'r') as file:
        urls = file.read().splitlines()
        file.close()
    with open('data/titles.txt', 'r') as file:
        titles = file.read().splitlines()
        file.close()
    
    # Load pickle files into variables
    names = ['data/punctuated.pkl', 'data/punctuated_embed.pkl', 'data/subs.pkl']
    punctuateds, sentence_embeddings_p, subs = tuple(map(loadPickle, names))
    
    ''' END OF PRE-LOAD NECESSARY DATA '''
    return (titles, urls, subs, punctuateds, sentence_embeddings_p)