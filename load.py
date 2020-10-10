from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from sentence_transformers import SentenceTransformer

SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
AutoTokenizer.from_pretrained("twmkn9/albert-base-v2-squad2")
AutoModelForQuestionAnswering.from_pretrained("twmkn9/albert-base-v2-squad2")