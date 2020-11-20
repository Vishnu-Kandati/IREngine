from utils import errors
import requests
from urllib.parse import urlparse, urljoin
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
