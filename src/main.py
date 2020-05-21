
from tkinter import *
import subprocess
import tkinter as tk

#Runnning the standard python UI
window = tk.Tk() 
window.title("Web Search Engine")
window.rowconfigure(0, minsize = 10, weight=1)
window.columnconfigure(1, minsize= 10, weight=1)

Label(window, text='Please type in your search', width = 20, height = 5).grid(row= 0) 

def expanderSearch():
    query = entry.get()
    execute = 'python ExpanderSearch.py "' + query + '"' 
    subprocess.Popen(execute, shell =True)
    window.destroy()
    
def search():
    query = entry.get()
    execute = 'python Search.py "' + query + '"' 
    subprocess.Popen(execute, shell =True)
    window.destroy()

entry = Entry(window) 
entry.grid(sticky="nsew",row = 0, column = 1, padx = 5, pady = 10) 
button1 = Button(window, command = search, text = "search for result")
button1.grid(row = 1, column = 0, padx = 5, pady = 10)
button2 = Button(window, command = expanderSearch, text = "query expander search")
button2.grid(row = 1, column = 1, padx = 5, pady = 10)


mainloop() 