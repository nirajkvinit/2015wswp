import re
from pdownload import download
import urlparse
import robotparser
from throttler import Throttle


def link_crawler(seed_url, max_depth=2):
    """Crawl from the given seed URL following links matched by link_regex
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(seed_url)
    rp.read()
    user_agent = 'Mozilla/5.0'
    throttle = Throttle(2)

    crawl_queue = [seed_url]
    # seen = set(crawl_queue)
    seen = {}
    while crawl_queue:
        url = crawl_queue.pop()
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url)
            # Filter for links matching our regular expression
            for link in get_links(html):
                link = urlparse.urljoin(seed_url, link)
                # print link
                # check if crawler has already seen this link
                if link not in seen:
                    seen.add(link)
                    crawl_queue.append(link)
        else:
            print 'Blocked by robots.txt', url


def get_links(html):
    """Return a list of links from html
    """
    if not html:
        return []
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com')
