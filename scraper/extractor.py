import re


def get_links(html):
    """Return a list of links from html
    """
    if not html:
        return []
    # a regular expression to extract all links from webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)

    # list of all links from webpage
    return webpage_regex.findall(html)


def get_images(html):
    if not html:
        return []
    img_regex = re.compile('<img[^>]+src=["\'](.*?)["\']', re.IGNORECASE)
    return img_regex.findall(html)
