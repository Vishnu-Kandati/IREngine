import collections
class ParsedURLs:
    def __init__(self):
        self.parsed_urls = collections.OrderedDict()  # to remember the order in which URLs (keys) were added

    def add_item(self, url, links_found, promise, relevance, len, status_code, time):  # add an item into the dictionary
        self.parsed_urls[url] = [links_found, promise, relevance, len, status_code, time]

    def find(self, url):  # check if item already exists
        return url in self.parsed_urls

    def display(self):  # display URLs in dictionary i.e. the keys
        print(self.parsed_urls.keys())

    def get_keys(self):  # return all the keys of the dictionary
        return self.parsed_urls.keys()

    def get_item(self, key):  # return the number of links found, promise, page len, timestamp for a given key
        return len(self.parsed_urls[key][0]), self.parsed_urls[key][1], self.parsed_urls[key][2], \
               self.parsed_urls[key][3], self.parsed_urls[key][4], self.parsed_urls[key][5]