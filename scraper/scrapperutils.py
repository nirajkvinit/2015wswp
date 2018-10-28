import urlparse


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link)  # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URLs belong to the same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc
