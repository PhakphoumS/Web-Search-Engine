
import io
import math
import json
import math

docs = json.load(open('urlWord.json', 'r'))

#Calculating tf, idf, document length
word_collection = []
for k in docs.keys():
    for word in docs[k]:
        word_collection.append(word)

tf = dict() 
for word in word_collection:
    tf[word] = dict()
    for d in docs.keys(): 
        tf[word][d] = 0

#frequency
for k in docs.keys(): 
    for word in docs[k]:
        tf[word][k] = tf[word][k] + 1

#if docs does not appear in word, do not include them
for word in tf.keys(): 
    for d in docs.keys():
        if tf[word].get(d) == 0:
            tf[word].pop(d)
json.dump(tf, open('tf.json', 'w'))

#calculte the no. of doc where the word appears in key
idf = dict()
for word in tf.keys():
    idf[word] = len(tf[word].items())
json.dump(idf, open('idf.json', 'w'))


#standard normalizaion of doc where the key is the no.
doclen = dict()
collection_len = len(docs.keys())
for d in docs.keys():
    total = 0.0
    for wd in set(docs[d]):
            x = tf[wd].get(d)* math.log(collection_len / idf.get(wd))
            total = total + math.pow(x,2)
    doclen[d] = math.sqrt(total)
json.dump(doclen, open('doclen.json', 'w'))
