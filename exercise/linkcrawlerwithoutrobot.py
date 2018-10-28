import re
import urlparse
import urllib2
import time
from datetime import datetime
import robotparser
import Queue


def link_crawler(seed_url, delay=5, max_depth=-1, headers=None, num_retries=1):
    """Crawl from the given seed URL by following links 
    """
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'

    # The queue of urls that still need to be crawled
    crawl_queue = Queue.deque([seed_url])

    # The urls that have been seen and at depth
    seen = {seed_url: 0}
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()

        throttle.wait(url)
        html = download(url, headers, num_retries=num_retries)
        html = html['data']

        if not html:
            print ' html is empty '
            continue

        links = []
        depth = seen[url]
        if depth != max_depth:
            # we can still crawl further
            links.extend(link for link in get_links(html))

            for link in links:
                link = normalize(seed_url, link)
                # check whether already crawled this link
                if link not in seen:
                    seen[link] = depth + 1
                    # check link is within same domain
                    if same_domain(seed_url, link):
                        # add this new link to queue
                        crawl_queue.append(link)


class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """

    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()


def download(url, headers, num_retries, data=None):
    print 'downloading: ', url
    scapingData = {'error': None, 'data': '', 'errdesc': ''}

    request = urllib2.Request(url, data, headers)
    opener = urllib2.build_opener()

    try:
        response = opener.open(request, timeout=10)
        html = response.read()
        code = response.code
        scapingData['data'] = html

    except urllib2.URLError as excp:
        # print 'Download error:', excp.reason

        scapingData['error'] = True
        scapingData['errdesc'] = excp.reason

        if hasattr(excp, 'code'):
            code = excp.code
            if num_retries > 0 and 500 <= code < 600:
                # retry 5xx http errors
                return download(url, headers, num_retries-1, data)
        else:
            code = None
    except Exception as exp:
        scapingData['error'] = True
        scapingData['errdesc'] = 'Failed to download the page'
    return scapingData


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link)  # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URLs belong to the same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def get_links(html):
    """Return a list of links from html
    """
    if not html:
        print('empty results')
        return []
    # a regular expression to extract all links from webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)

    # list of all links from webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://www.tallydev.com',
                 delay=0, num_retries=1, max_depth=2)
