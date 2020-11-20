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
import collections
from validator import pre_validate_link

errors = []
def get_start_pages(query, num_start_pages=10):
    """ get start pages by performing a Google search """

    res = requests.get('https://www.google.com/search', params={'q': query})
    soup = BeautifulSoup(res.content, 'lxml')
    links = soup.find_all('a')

    initial_links = []
    count = 0

    for link in links:
        href = link.get('href')
        if "url?q=" in href and "webcache" not in href:
            l_new = href.split("?q=")[1].split("&sa=U")[0]
            if pre_validate_link(url_normalize(l_new)):  # pre-validating link before enqueue, but validate upon dequeue
                count += 1
                if count <= num_start_pages:
                    initial_links.append(url_normalize(l_new))
                else:
                    break
    return list(set(initial_links))

def get_promise(query, mode, url, synonyms_list, lematized_words):
    """ returns the promise of a URL, based on which URLs are placed on the priority queue """
    if mode.lower() == 'bfs':
        return 1  # all pages have the same promise in a simple bfs crawl since we do not compute relevance
    else:
        # calculate promise based on the link
        # remove punctuation from query
        punctuation = set(string.punctuation)
        query = ''.join(x for x in query if x not in punctuation)

        query_terms = [q.lower() for q in query.strip().split()]
        parent_relevance = 0.5
        final_promise =  calculate_promise(parent_relevance, url, query_terms,synonyms_list,lematized_words)

        return final_promise

##The method get_promise is splitted into get_promise and calculate_promise to reduce the long paramterlist.
# Replace Paramater with method call technique is used. 
def calculate_promise(parent_relevance, url, query_terms,synonymslist,lematized_words):
        promise = 0 
        # checking if all or any of the terms are in the link, if synonyms are present, if lemmatized words are present
        d={'queryterms':[0.2,0.25],'synonyms_list':[0.4,0.2],'lematizedwords':[0.4,0.2]}
        check_terms = [query_terms,synonymslist,lematized_words]
        for i in range(len(check_terms)):
            if all([x in url.lower() for x in check_terms]):  # all query terms are in the URL
                promise += d[check_terms[i]][0]
            elif any([x in url.lower() for x in check_terms]):  # at least 1 query term in URL, but not all
                promise += d[check_terms[i]][1]
            else:  # no query term in URL
                pass  # keep promise as it is   
        promise += 0.25 * parent_relevance  # giving a certain weight to URL's parent's relevance
        promise /= len(url)  # to penalize longer URLs
        return promise


def get_synonyms_and_lemmatized(query):
    """ returns a dict with a list of synonyms per word in the query """

    query = query.lower()

    # remove punctuation from query
    punctuation = set(string.punctuation)
    query = ''.join(x for x in query if x not in punctuation)

    words = word_tokenize(query)

    pos = {}  # part of speech
    for word in words:
        pos.update({word: pos_tag([word], tagset='universal')[0][1]})

    simplified_pos_tags = {}

    for x in pos.keys():
        if pos[x] == 'NOUN':
            simplified_pos_tags.update({x: 'n'})
        elif pos[x] == 'VERB':
            simplified_pos_tags.update({x: 'v'})
        elif pos[x] == 'ADJ':
            simplified_pos_tags.update({x: 'a'})
        elif pos[x] == 'ADV':
            simplified_pos_tags.update({x: 'r'})
        else:
            simplified_pos_tags.update({x: 'n'})  # consider everything else to be a noun

    synonyms = {}
    for w in words:
        synonyms[w] = []

    for w in words:
        if len(wordnet.synsets(w, pos=simplified_pos_tags[w])) != 0:
            s = [x.lower().replace('_', ' ') for x in wordnet.synsets(w, pos=simplified_pos_tags[w])[0].lemma_names() if
                 x.lower() != w]
            for x in s:
                if x not in synonyms[w]:
                    synonyms[w].append(x)

    wordnet_lemmatizer = WordNetLemmatizer()
    # lemmatize all words, return only those which aren't the same as the word
    lemmatized_words = [wordnet_lemmatizer.lemmatize(w, simplified_pos_tags[w]) for w in words if
                        wordnet_lemmatizer.lemmatize(w, simplified_pos_tags[w]) != w]

    return synonyms, list(set(lemmatized_words))


def visit_url(url, page_link_limit):
    """ parses a page to extract text and first k links; returns HTML text and normalized links """

    try:
        res = requests.get(url)
        if res.status_code == 200 and 'text/html' in res.headers['Content-Type']:  # also checking MIME type
            html_text = res.text
            soup = BeautifulSoup(res.content, 'lxml')
            f_links = soup.find_all('frame')
            a_links = soup.find_all('a')

            # check if the page has a <base> tag to get the base URL for relative links
            base = soup.find('base')
            if base is not None:
                base_url = base.get('href')
            else:
                # construct the base URL
                scheme = urlparse(url).scheme
                domain = urlparse(url).netloc
                base_url = scheme + '://' + domain

            src = [urljoin(base_url, f.get('src')) for f in f_links]
            href = [urljoin(base_url, a.get('href')) for a in a_links]

            links = list(set(src + href))[:page_link_limit]
            links = [url_normalize(l) for l in links if pre_validate_link(url_normalize(l))]
            # pre_validate before enqueue, but validate after dequeue

            return html_text, links
        else:
            return None, None
    except:
        return None, None
