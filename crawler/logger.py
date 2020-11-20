from utils import errors
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