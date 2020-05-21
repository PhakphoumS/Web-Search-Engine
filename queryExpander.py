
import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn
#from gensim.models import Word2Vec as wv
#from nltk.tokenize import sent_tokenize, word_tokenize 
#import warnings 
#warnings.filterwarnings(action = 'ignore') 
#import gensim 
#from gensim.models import Word2Vec 

import re
import spacy
nlp = spacy.load('en_core_web_lg')
import itertools

def queryExpander(query):
    SynQ = []
    join = []
    query_word = query.split('_')
    ns = range(1, len(query_word)) 
    for n in ns:
        for idxs in itertools.combinations(ns, n):
            for x, y in zip((0,) + idxs, idxs + (None,)):
                join = '_'.join(query_word[x:y])
    
    for x in join:
        for word in x:
            syn_query = []
            synonyms = []
            if wn.synsets(word):
                #creating synnonums list for each word 
                #and using the feature similarty from spacy to compute sim
                for i in range(len(wn.synsets(word)[0].lemmas())):
                    synonyms.append(wn.synsets(word)[0].lemmas()[i].name())
                docEm = nlp(word.replace('_',' '))
                for x in synonyms:
                    x = x.replace('_',' ')
                    doc2 = nlp(x)
                    if(docEm.similarity(doc2) > 0.80):
                        if(x.lower() != word):
                            syn_query.append(x.lower())
            SynQ = SynQ + syn_query

    return set(SynQ)  
    