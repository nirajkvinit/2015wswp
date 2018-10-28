import urllib2


def download(url, num_retries=1, timeout=30):
    print 'downloading: ', url
    scapingData = {'error': None, 'data': '', 'errdesc': ''}

    # Default User Agent
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'

    request = urllib2.Request(url, '', {'User-agent': user_agent})
    opener = urllib2.build_opener()

    try:
        response = opener.open(request, timeout=timeout)
        html = response.read()
        code = response.code
        scapingData['data'] = html

    except urllib2.URLError as exp:
        scapingData['error'] = True
        scapingData['errdesc'] = exp.reason

        if hasattr(exp, 'code'):
            code = exp.code
            if num_retries > 0 and 500 <= code < 600:
                # retry 5xx http errors
                return download(url, num_retries=num_retries-1, timeout=timeout)
        else:
            code = None
    except Exception as exp:
        scapingData['error'] = True
        scapingData['errdesc'] = 'Failed to completely download the page. Timeout'
    return scapingData
