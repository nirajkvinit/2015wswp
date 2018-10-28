import urllib2


def download(url, user_agent='Mozilla/5.0', num_retries=2):
    print 'downloading: ', url
    headers = {'User-agent': user_agent}
    try:
        request = urllib2.Request(url, headers=headers)
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as exp:
        print 'download error', exp.reason
        html = None
        if num_retries > 0:
            print 'retry'
            if hasattr(exp, 'code') and 500 <= exp.code < 600:
                print 'retry2'
                return download(url, num_retries-1)
    return html


if __name__ == '__main__':
    print download('http://www.novamining.com')
