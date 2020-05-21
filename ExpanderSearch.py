
import io
from sys import argv
import json
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import math
from operator import itemgetter
import queryExpander as qExpand

#loading the collection file
docs = json.load(open('urlWord.json', 'r'))
script, query = argv

#calling the intelligent feature(query expander)
queryLine = query.replace(" ","_")
SynQ = []
try:
    SynQ = qExpand.queryExpander(queryLine)
    for word in SynQ:
        query = query +" "+ word
except:
    pass

pattern = '([a-z]*[-]?[a-z]+|[A-Z][a-z]+|[A-Z]+)'
tokenizer = RegexpTokenizer(pattern) 
tokenized_query = tokenizer.tokenize(query)

stop_words = open('stopwords.txt').read()

stemmer = PorterStemmer()
Stemmed_query = []

for word in tokenized_query:
    stemmed = stemmer.stem(word.lower())
    Stemmed_query.append(stemmed)

PQuery = []
for word in Stemmed_query:
    if word not in stop_words:
        PQuery.append(word)
    else: 
        print("stemmed word error")

query_words = []
for word in PQuery:
    query_words.append(word)

#loading the necessary .json files to compute cosine-similarities
doclen = json.load(open('doclen.json', 'r'))
idf = json.load(open('idf.json', 'r'))
tf = json.load(open('tf.json', 'r'))

#nomalizing queriex 
urlWord_klen = len(docs.keys())
total = 0.0
for wq in set(PQuery):
    if wq in idf.keys(): 
        x = PQuery.count(wq)*math.log(urlWord_klen / idf.get(wq))
        total = total + math.pow(x,2)
query_len = math.sqrt(total)

#the function takes doc as inpute and compute cosine sim bwn doc and given query
#and returns value of cosine sim
def cossim(d):
    num = 0.0
    simimarity = 0
    urlWord_klen = 2806
    for wq in PQuery: 
        if wq in docs[d]: # num_occ_wq*log(tot_doc/doc_cont_wq)*num_occ_wd*log(tot_doc/doc_cont_wq)
            num = num + PQuery.count(wq)* math.log(urlWord_klen / idf[wq])* tf[wq].get(d)* math.log(urlWord_klen / idf[wq])
    simimarity = num / (query_len * doclen[d])
    return simimarity

similarities = dict()

#given the query, the function returns the docs 
# that have the words which appears in query
def docRetrieval(): 
    docs_list = set([])
    x = []
    for word in PQuery:
        if word in tf.keys():
            x = set(tf[word].keys())
            docs_list = docs_list.union(x)
            x = []
    return set(docs_list)

TFScores = 0.0
for d in docRetrieval():
    similarities[str(d)] = cossim(d)
    TFScores += cossim(d)

#Intelligent feature(search)
linkCount = json.load(open('linkCount.json', 'r'))
scores = dict()
rankScore = 0.0
finalSim = 0.0
for page in similarities.keys():
    finalSim += similarities[page]
for page in linkCount.keys():
    rankScore += linkCount[page]
for page in similarities.keys():
    if(linkCount[page] != 0.0):
        scores[page] = 1.5* similarities[page]/finalSim + 0.7 *(linkCount[page]/rankScore)    
    else:
        scores[page] = similarities[page]/finalSim

FinalRank = sorted(scores.items(), key = itemgetter(1), reverse = True)

# ssecond window for results output
from tkinter import *
from tkinter.ttk import *
import subprocess, webbrowser
def populate(frame):
    button = []
    counter = 0

    for row in range(20):
        if(row < len(FinalRank)):
            button.append(Button(frame, 
                        text=FinalRank[row][0], 
                        command=lambda aurl=FinalRank[row][0]:OpenUrl(aurl)))
        try:
            button[row].pack()
            counter+=1
        except IndexError as error:
            pass

        Label(frame, text="%s" % row, width=3, borderwidth="1", 
                 relief="solid")

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

def OpenUrl(url):
    webbrowser.open_new(url)
    
window = Tk()
window.title("Results from expanded query search")
canvas = Canvas(window, borderwidth=0)
frame = Frame(canvas)
vsb = Scrollbar(window, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((4,4), window=frame, anchor="nw")
frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

populate(frame)

window.mainloop()
