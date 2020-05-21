
from tqdm import tqdm
import re
import io
import os
import requests
import json
import urllib.request
from urllib.parse import urljoin
from urllib.request import urlopen
from urllib import parse
from bs4 import BeautifulSoup
import urlparse
import requests
from PyPDF2 import PdfFileReader
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer as stemmer
import linkMarker

#file extension that are to be avoided
avoid = ('.doc','.docx','.ppt','.zip','.rar','.taz','.tar','.ico','.gz','.gif',
          '.mpg','.jpg','.png','.jpeg','.avi','.bin','.exe','=0','=','#',
          '.mov','.rss','.pptx','.c','.h','.rdf','.js','.css','*','pif',
          '.ps','.php','.asp','.cer','.txt')

visited_s = []
visited = []
text = ""


###############
#web scraping##
###############
def scraping(URL):
    url = URL
    status_code = requests.get(url)
    text_plain = status_code.text
    soup = BeautifulSoup(text_plain, 'html.parser')
    linklist = soup.findAll('a')
    for link in linklist:
        text = link.get('href')
        text = urljoin(URL,str(text)) 
        #checking edges cases
        if(re.search("#([a-z]*[-]?[0-9]*)*",str(text)) != None):
            continue
        if(str(text).endswith("None")):
            text = text[-4]
        if(str(text).endswith("/")):
            text = str(text)[:-1]
        if((type(text)!= type(None)) and (str(text) not in visited_s) and (str(text) not in visited) and re.match("http[s]?://www\.?[a-z]*\.uic\.edu",text)!= None) and (re.search("dispatch",text)== None) and not str(text).endswith(avoid):
            print(text)
            if(re.search("https",str(text))):
                new = str(text).replace("https","http")
            elif(re.search("http",str(text))):
                new = str(text).replace("http","https")
            visited.append(new)
            visited_s.append(text)
            file.write(text)
            file.write("\n")
    return

file = open('crawled.txt','w')
file.write("https://www.cs.uic.edu")
file.write("\n")
visited_s.append("https://www.cs.uic.edu")
visited.append("http://www.cs.uic.edu")

#file.write("https://www.bioe.uic.edu")
#file.write("\n")
#visited_s.append("https://www.bioe.uic.edu")
#visited.append("http://www.bioe.uic.edu")

start = 0
for x in tqdm(range(start, 3000)):
    if(len(visited_s) >= 3000):
        break
    try:
        scraping(visited_s[x])
        start = x
    except Exception:
        pass

file = open('crawled.txt','w')
for page in visited_s:
    file.write(page)
    file.write("\n")
print(len(visited_s))

web_pages = dict()

#the function takes in pdf file and save output as web_page dict
def processor(url):
    if(url.endswith(('.pdf'))):
        r = requests.get(url)
        file = io.BytesIO(r.content)
        reader = PdfFileReader(file)
        if reader.isEncrypted:
            reader.decrypt('')
        web_pages[url] = []
        for page in range(reader.getNumPages()):
            contents = reader.getPage(page).extractText().split('\n')
            web_pages[url] = web_pages[url] + contents  #like a dictionary(url:content)
            web_pages[url] = " ".join(web_pages[url])
    else:
        #removing unwated tag, header,etc. and keep only text for the html.file
        string = ""
        status_code = urlopen(url)
        text_plain = status_code.read()
        soup = BeautifulSoup(text_plain, "html.parser")
        for remove in soup(["script","style"]):
            remove.extract()
        web_pages[url] = soup.getText()
        return

urls=[]
for l in open('crawled.txt').readlines():
    urls.append(l.replace('\n',''))
for page in tqdm(urls):
    try:
        processor(page)
    except Exception:
        pass

######################
#text pre processing #
#token,stem,stopW####
######################
tokenizer = RegexpTokenizer('([a-z]*[-]?[a-z]+|[A-Z][a-z]+|[A-Z]+)') 
stop_words = open('stopwords.txt').read()

stem_pages = dict()
for key in web_pages.keys():
    stem_pages[key] = tokenizer.tokenize(str(web_pages[key]))
    
stem_pages2 = dict()
for key in stem_pages.keys():
    llist = []
    for word in stem_pages[key]:
        new = stemmer.stem(word.lower())
        llist.append(new)
    stem_pages2[key] = l

stem_pages3 = dict()
for d in stem_pages2.keys():
    if stem_pages2[d]:
        stem_pages3[d] = stem_pages2[d]

#Removing Stop words
stem_pages4 = dict()
for key in stem_pages3.keys():
    l = []
    for word in stem_pages3[key]:
        if word not in stop_words:
            l.append(word)
    stem_pages4[key] = l

for key in stem_pages4.keys():
    for word in stem_pages4[key]:
        c = len(re.findall("[a-z]", word))
        if c <= 2:
            stem_pages4[key].remove(word)

json.dump(stem_pages4, open('urlWord.json', 'w'))

#creating a txt file and save pages found
counter = 0
for page in stem_pages4.keys():
    if(not page.endswith('.pdf')):
        try:
            urllib.request.urlretrieve(page, "Pages/"+ str(counter) + ".txt")
        except Exception:
            pass
        counter +=1

#for all the links in a page(in the director), create a dictonary obj
# remove prvious checkpoints
pages = os.listdir("Pages/")
pages.remove(".ipynb_checkpoints")

linkMarker.retrieveLinks(pages)
stem_pages4 = json.load(open('urlWord.json', 'r'))
linkCount = dict()
for page in stem_pages4.keys():
    linkCount[page] = lc.inLink(page)
    
json.dump(linkCount, open('linkCount.json', 'w'))
