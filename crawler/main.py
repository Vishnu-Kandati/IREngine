from PriorityQueue import PriorityQueue
from parsedURL import ParsedURLs
from crawler import Crawler
from pagecount import page_count
from utils import get_harvest_rate,create_log,get_start_pages,get_synonyms_and_lemmatized,get_input
import time
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('wordnet')

def main():
    query, num_start_pages, n, page_link_limit, mode, relevance_threshold = get_input()
    start_time = time.time()
    start_pages = get_start_pages(query, num_start_pages)

    links_to_parse = PriorityQueue()
    parsed_urls = ParsedURLs()

    # get synonyms list and lemmatized words
    synonyms, lemmatized_words = get_synonyms_and_lemmatized(query)
    # creating a combined list of synonyms without duplicates
    synonyms_list = list(set([s for sublist in list(synonyms.values()) for s in sublist]))

    print('Found %d crawlable start pages:\n' % len(start_pages))
    # enqueue the start pages after computing their promises
    for s in start_pages:
        # promise = get_promise(query, s, mode, 0)  # initially, parent_relevance is 0
        promise = 1  # assuming that all the start pages are equally promising
        links_to_parse.enqueue([promise, s])

    # display the queue
    links_to_parse.display_queue()
    print('\n')

    while links_to_parse and page_count.get_page_num() < n:
        crawler = Crawler(links_to_parse, parsed_urls, query, n, page_link_limit, mode, synonyms_list, lemmatized_words)
        crawler.run()

    end_time = time.time()
    total_time = (end_time - start_time)/60  # minutes

    # compute harvest rate
    harvest_rate = get_harvest_rate(parsed_urls, relevance_threshold)

    # create a crawler log file
    create_log(parsed_urls, query, len(start_pages), len(parsed_urls.get_keys()), page_link_limit, n, mode,
               harvest_rate, relevance_threshold, total_time)


if __name__ == "__main__":
    main()