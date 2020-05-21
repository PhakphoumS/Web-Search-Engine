
import requests
import os
import json
from bs4 import BeautifulSoup

pages = os.listdir("Pages/")
pages.remove(".ipynb_checkpoints")

def inLink(page):
    score = 0.0
    linkCollection = json.load(open('linkCollection.json', 'r'))
    for p in linkCollection.keys():
        count = 0
        if(page in set(linkCollection[p])):
            count += 1
            score = score + count/len(linkCollection[p])
            
    return score

def retrieveLinks(pages):
    linkCollection = dict()
    for page in pages:
        linkCollection[str(page)] = []

    for page in pages:
        f = open("Pages/" + str(page),'rb').read()
        soup = BeautifulSoup(f,'html.parser')
        linklist = soup.findAll('a')


        for link in linklist:
            text = link.get('href')
            linkCollection[str(page)].append(text)
    json.dump(linkCollection, open('linkCollection.json', 'w'))

    return
    
