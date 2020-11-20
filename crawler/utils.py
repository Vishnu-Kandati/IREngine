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


def pre_validate_link(url):
    """ only checks if the link contains excluded words and/or types """

    excluded_words = ['download', 'upload', 'javascript', 'cgi', 'file']
    excluded_types = [".asx", ".avi", ".bmp", ".css", ".doc", ".docx",
                      ".flv", ".gif", ".jpeg", ".jpg", ".mid", ".mov",
                      ".mp3", ".ogg", ".pdf", ".png", ".ppt", ".ra",
                      ".ram", ".rm", ".swf", ".txt ", ".wav", ".wma",
                      ".wmv", ".xml", ".zip", ".m4a", ".m4v", ".mov",
                      ".mp4", ".m4b", ".cgi", ".svg", ".ogv", ".dmg", ".tar", ".gz"]

    for ex_word in excluded_words:
        if ex_word in url.lower():
            errors.append('Link contains excluded terms')
            return False

    for ex_type in excluded_types:
        if ex_type in url.lower():
            errors.append('Link contains excluded type')
            return False

    return True


def validate_link(url):
    """ checks if website is crawlable (status code 200) and if its robots.txt allows crawling
    also checks for the MIME type returned in the response header """

    # checking if the url returns a status code 200
    try:
        r = requests.get(url)
        if r.status_code == 200:
            pass  # website returns status code 200, so check for robots.txt
        else:
            print(url, r.status_code, 'failed')
            errors.append(r.status_code)
            return False
    except:
        print(url, 'request failed')  # request failed
        errors.append('Request Failed')
        return False

    # checking if the website has a robots.txt, and then checking if I am allowed to crawl it
    domain = urlparse(url).scheme + '://' + urlparse(url).netloc

    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(domain + '/robots.txt')
        rp.read()
        if not rp.can_fetch('*', url):  # robots.txt mentions that the link should not be parsed
            print('robots.txt does not allow to crawl', url)
            errors.append('Robots Exclusion')
            return False
    except:
        return False

    # checking the MIME type returned in the response header
    try:
        if 'text/html' not in r.headers['Content-Type']:
            errors.append('Invalid MIME type')
            return False
    except:
        errors.append('Request Failed')
        return False
    return True


def get_input():
    """ get query, number of start pages, number of pages to be returned and mode """

    query = input('Enter your query (default: "wildfires california"): ').strip()
    num_start_pages = input("Enter the number of start pages (default: 10): ").strip()
    n = input("Enter the number of pages to be returned (at least 10, default: 1000): ").strip()
    page_link_limit = input("Enter the max. no. of links to be fetched from each page (at least 10, default: 25): ")\
        .strip()
    mode = input("Enter mode 'bfs' or 'focused' (default: 'bfs'): ").strip()
    relevance_threshold = input('Enter the relevance threshold (min: 0, max: 4.75, default: 1): ').strip()

    print('\nObtaining start pages...\n')
    # checking if values are input correctly, otherwise use defaults
    if len(query) == 0:
        query = 'wildfires california'

    if len(num_start_pages) == 0 or int(num_start_pages) <= 0:
        num_start_pages = 10

    if len(n) == 0 or int(n) < 10:
        n = 1000

    if len(page_link_limit) == 0 or int(page_link_limit) < 10:
        page_link_limit = 25

    if len(mode) == 0 or mode.lower() not in {'bfs', 'focused'}:
        mode = 'bfs'

    if len(relevance_threshold) == 0 or (int(relevance_threshold) < 0 or int(relevance_threshold) > 4.75):
        relevance_threshold = 1

    return query, int(num_start_pages), int(n), int(page_link_limit), mode, int(relevance_threshold)


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

##Long Method Code Smell
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


def get_harvest_rate(parsed_urls, threshold):
    """ return harvest rate i.e. # relevant links/# total links parsed """

    total_parsed = len(parsed_urls.get_keys())
    total_relevant = 0

    for link in parsed_urls.get_keys():
        if parsed_urls.get_item(link)[2] >= threshold:
            total_relevant += 1

    harvest_rate = total_relevant/total_parsed

    return harvest_rate


def create_log(parsed_urls, query, num_start_pages, num_crawled, page_link_limit, n, mode, harvest_rate, threshold,
               total_time):
    """ creates a log file for the crawler """

    file = open('crawler_log.txt', 'w')

    file.write('Query: ' + query + '\n')
    file.write('Number of Crawlable Start Pages: ' + str(num_start_pages) + '\n')
    file.write('Number of URLs to be Crawled: ' + str(n) + '\n')
    file.write('Max. Number of Links to be Scraped per Page: ' + str(page_link_limit) + '\n')
    file.write('Crawl Mode: ' + mode + '\n')

    file.write('\n')
    file.write('Number of URLs Crawled: ' + str(num_crawled) + '\n')
    total_size = sum([parsed_urls.get_item(x)[3] for x in parsed_urls.get_keys()])
    file.write('Total Size (Length) of all Pages Crawled: ' + str(total_size) + '\n')
    if total_time < 1:  # convert to seconds
        total_time *= 60
        file.write('Total Time Elapsed: ' + str(total_time) + ' sec\n')
    else:
        file.write('Total Time Elapsed: ' + str(total_time) + ' min\n')

    file.write('Harvest Rate: ' + str(harvest_rate) + ' at Threshold: ' + str(threshold) + '\n')

    unique_errors = list(set(errors))
    file.write('\nErrors: \n')
    file.write('-------\n')
    for e in unique_errors:
        file.write(str(e) + ': ' + str(errors.count(e)) + '\n')
    file.write('\nURLs Crawled:\n')
    file.write('-------------\n\n')

    counter = 0
    for p in parsed_urls.get_keys():
        file.write(str(counter+1) + '. \n')
        file.write('URL:' + p + '\n')
        num_links, page_promise, relevance, page_size, status_code, timestamp = parsed_urls.get_item(p)

        file.write('Number of Links in Page:' + str(num_links) + '\n')
        file.write('Page Size:' + str(page_size) + '\n')
        file.write('Page Promise: ' + str(page_promise) + '\n')
        file.write('Page Relevance: ' + str(relevance) + '\n')
        file.write('Status Code: ' + str(status_code) + '\n')
        file.write('Crawled at:' + str(timestamp) + '\n')
        file.write('\n\n')
        counter += 1