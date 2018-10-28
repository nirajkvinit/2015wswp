import Queue
import json
from throttler import Throttle
from pagedownloader import download
from scrapperutils import same_domain, normalize
from extractor import get_links, get_images


def link_crawler(seed_url, delay=5, max_depth=-1, num_retries=1):
    """Crawl from the given seed URL by following links 
    """

    # datastore
    datastore = {}

    # The queue of urls that still need to be crawled
    crawl_queue = Queue.deque([seed_url])

    # The urls that have been seen and at depth
    seen = {seed_url: 0}

    # throttle the crawling speed
    throttle = Throttle(delay)

    while crawl_queue:
        url = crawl_queue.pop()
        if url in datastore.keys():
            continue

        linkData = {
            'url': url,
            'error': False,
            'links': [],
            'errordesc': None,
            'images': []
        }

        # Delay fetching data
        throttle.wait(url)
        fetchedHtml = download(url, num_retries=num_retries)
        html = fetchedHtml['data']

        if fetchedHtml['error']:
            linkData['error'] = fetchedHtml['error']
            linkData['errdesc'] = fetchedHtml['errdesc']
            continue

        links = []
        depth = seen[url]
        if depth != max_depth:
            # we can still crawl further

            fetchedLinks = get_links(html)
            if len(fetchedLinks) <= 0:
                continue

            # get images and store in the store
            linkData['images'] = get_images(html)

            links.extend(link for link in fetchedLinks)

            for link in links:
                link = normalize(seed_url, link)
                # check whether already crawled this link
                if link not in seen:
                    seen[link] = depth + 1
                    # check link is within same domain
                    if same_domain(seed_url, link):
                        # add this new link to queue
                        crawl_queue.append(link)

        datastore[url] = linkData

    return datastore


if __name__ == '__main__':
    datastore = link_crawler('http://www.tallydev.com',
                             delay=0, num_retries=1, max_depth=2)
    # print json.dumps(datastore)
    f = open('data.txt', "w+")
    f.write(json.dumps(datastore))
    f.close()
