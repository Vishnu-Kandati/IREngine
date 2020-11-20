import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib.robotparser
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
import datetime
from url_normalize import url_normalize
import time
import string

#Long Method Code Smell
def get_relevance(html_text, query, synonyms_list, lematized_words):
    """ returns the relevance of a page after crawling it """

    # remove punctuation from query
    punctuation = set(string.punctuation)
    query = ''.join(x for x in query if x not in punctuation)

    query_terms = query.lower().strip().split()
    relevance = 0

    soup = BeautifulSoup(html_text, 'lxml')

    if soup.title:
        # TITLE
        title = soup.title.text.lower()
        relevance_title = calculate_relevance(title,"title",query_terms,synonyms_list,lematized_words) 
        relevance += relevance_title
    if soup.find('h1'):
        # FIRST HEADING
        h1 = soup.find('h1').text.lower()  # first h1 heading
        relevance_heading = calculate_relevance(h1,"heading",query_terms,synonyms_list,lematized_words)
        relevance += relevance_heading
    if soup.find_all('a'):
        # ANCHOR TAGS TEXT
        a_text = ' '.join(list(set([a.text.lower() for a in soup.find_all('a')])))  # anchor tags text combined
        relevance_anchor = calculate_relevance(a_text,"anchor",query_terms,synonyms_list,lematized_words)
        relevance += relevance_anchor
    if soup.find_all('b'):
        # BOLD TEXT
        bold = ' '.join(list(set([b.text.lower() for b in soup.find_all('b')])))  # bold text combined
        relevance_anchor = calculate_relevance(bold,"bold",query_terms,synonyms_list,lematized_words)
        relevance += relevance_anchor
    return relevance

## Extract method Refactoring Technique
def calculate_relevance(query, partOfPage,query_terms,synonymslist,lematized_words):
        d={'title':[0.25,0.15,0.2,0.1,0.2,0.1],'heading':[0.5,0.45,0.45,0.4,0.45,0.4],'anchor':[0.25,0.15,0.2,0.1,0.2,0.1],'Bold':[0.25,0.15,0.2,0.1,0.2,0.1]}
        relevance = 0
        check_terms = [query_terms,synonymslist,lematized_words]
        for i in range(len(check_terms)):
            if all(query in partOfPage for query in check_terms[i]):  # all terms
                relevance += d[partOfPage][2*i]
            elif any(query in partOfPage for query in check_terms[i]):  # at least one term 
                relevance += d[partOfPage][2*i+1]
            else:
                pass  # keep relevance as is
        return relevance
