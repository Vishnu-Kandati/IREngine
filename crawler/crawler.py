from utils import validate_link,visit_url,get_relevance,pre_validate_link,get_promise
import datetime
from bs4 import BeautifulSoup
import requests
from pagecount import PageCount
page_count = PageCount()

class Crawler:
    def __init__(self, links_to_parse, parsed_urls, query, pages, page_link_limit, mode, synonyms_list, lemmatized_words):
        # initializing all the attributes
        self.links_to_parse = links_to_parse
        self.parsed_urls = parsed_urls
        self.query = query
        self.pages = pages
        self.page_link_limit = page_link_limit
        self.mode = mode
        self.synonyms_list = synonyms_list
        self.lemmatized_words = lemmatized_words

    def run(self):
        item = self.links_to_parse.dequeue()  # get first item (highest promise) from the queue, item = [promise,url]
        print('Dequeued: ', item)
        url = item[1]
        if validate_link(url):  # after link is dequeued, check if it can be crawled i.e. status code, robots, MIME type
            html_text, links = visit_url(url, self.page_link_limit)  # read the HTML content of the URL, extract links
            print('writing')
            f = open(self.query+str(page_count.get_page_num())+".txt","x",encoding="utf-8")
            soup = BeautifulSoup(html_text, 'html.parser')
            #print(soup.prettify())
            tags = soup.find_all('p')
            for i in tags : 
                cont = i.get_text().split("\n")
                print(cont)
                for listitem in cont:
                    f.write('%s\n' % listitem)
            html_text, links = visit_url(url, self.page_link_limit)  # read the HTML content of the URL, extract links
            while (html_text, links) == (None, None):  # keep trying till visit_url() returns non-None values
                item = self.links_to_parse.dequeue()
                url = item[1]
                if validate_link(url):
                    html_text, links = visit_url(url, self.page_link_limit)

            page_count.increment()  # increment the page counter
            print(page_count.get_page_num())

            # get relevance of a URL after visiting it
            relevance = get_relevance(html_text, self.query, self.synonyms_list, self.lemmatized_words)
            # will use it to compute promise of its child links

            # add the crawled URL and details into the dictionary parsed_urls
            self.parsed_urls.add_item(url, links, item[0], relevance, len(html_text), requests.get(url).status_code,
                                      str(datetime.datetime.now().time()))
            print('Parsed: ', item)
            print('Relevance: ' + str(relevance) + '\n')

            for index in range(len(links)):  # add all the links present in the page to the queue
                if links[index] in self.parsed_urls.get_keys():  # if URL was already parsed earlier, continue
                    continue
                else:  # URL not parsed before
                    id = self.links_to_parse.find(links[index])  # check if the URL is already present in the queue
                    if id != -1:
                        # URL already present in the queue
                        if self.mode == 'bfs':
                            pass
                        else:  # for focused crawling, update the promise of the link using parent's relevance
                            # update item, pass parent relevance
                            self.links_to_parse.update_queue(links[index], relevance)
                    else:
                        # URL not in the queue
                        if pre_validate_link(links[index]):  # pre-validate before enqueue, validate upon dequeue
                            promise = get_promise(self.query, links[index], self.mode, relevance, self.synonyms_list,
                                                  self.lemmatized_words)
                            # 'relevance' is of parent
                            new_item = [promise, links[index]]
                            self.links_to_parse.enqueue(new_item)