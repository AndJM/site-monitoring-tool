"""
Simple website monitoring tool with command line utility. Uses the requests
module.
Comments scattered throughout indicate places for improvement
"""

import argparse
import logging
import sys
import time
try:
    import requests
except ImportError:
    sys.exit("requests module is missing, use 'pip install requests'"
             "see http://docs.python-requests.org/en/master/")

# create and configure logger
LOG_FORMAT = '%(levelname)s %(asctime)s Status: %(message)s'  #  msg contains checked URLs, their status and the response times
logging.basicConfig(filename='sitelogfile.log',
                    level=logging.INFO,
                    format=LOG_FORMAT,
                    datefmt='%Y-%m-%d %H:%M:%S'  # default ISO 8601 format
                    )


HTML_WRAP = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>Site Monitoring</title>
    <style>
      h1  { text-align: center; }
    </style>
  </head>
  <body>
    <h1>Site Monitoring (most recent)</h1>
%s
  </body>
</html>
'''


def get_site_status(url):
    """
    Checks for connection level problems (e.g. the web site is down)
    Measures the time it took for the web server to complete the whole request.
    """
    time_elapsed = None
    requests_obj = None
    try:
        requests_obj = requests.get(url)
    except requests.ConnectionError:
        msg = 'connection error'
    except requests.HTTPError:
        msg = 'HTTP error occurred'
    except requests.Timeout:  # future: requests that produced this error are safe to retry.
        msg = 'request timed out'
    else:
        msg = 'is up, code {}'.format(requests_obj.status_code)
        time_elapsed = str(requests_obj.elapsed)
    finally:
        return requests_obj, msg, time_elapsed


def check_content(requests_obj, content_requirement):
    """
    Verifies that the page content received from
    the server matches the content requirements.
    """
    return content_requirement in requests_obj.text  # future: probably re is better for more sophisticated requirements


def check_sites(filename):
    """
    The workhorse: handles the file IO, calls the other functions,
    writes a log file that shows the progress of the periodic checks.
    """
    messages = []
    with open(filename, 'r') as f:
        for url, content_requirement in load_file(f):
            r, msg, time_elapsed = get_site_status(url)
            if time_elapsed is None:
                msg = ' '.join([url, msg])
                logging.warning(msg)
                messages.append(msg)
            else:
                result = check_content(r, content_requirement)
                msg = ' '.join([url, msg, "Time elapsed:", time_elapsed, "Contains content:", str(result)])
                logging.info(msg)
                messages.append(msg)
    return messages


def load_file(file):
    file.readline()  # throw away first line
    for line in file:
        yield [token.strip() for token in line.split(',')]


def _launch():
    """
    Invokes the command line utility, allows configuring the waiting period.
    """
    parser = argparse.ArgumentParser(prog='python apdemo',
                                     description='Simple program and command line utility for site monitoring')
    parser.add_argument('filename',
                        help='filename is of file containing the URLs and corresponding page content requirements <URL string>')
    parser.add_argument('-t',
                        type=int,
                        dest='checking_period',
                        default=1800,
                        help='Change default checking period in seconds')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s 1.0')
    try:
        args = parser.parse_args()  # namespace containing the arguments to the command
    except IOError as msg:
        parser.error(str(msg))

    # future: check first for internet connectivity!
    while True:
        messages = check_sites(args.filename)
        message_string = ''
        for m in messages:
            message_string += '<h1>' + m + '</h1><br>'
        #  single-page HTTP server interface in the same process that shows
        # (HTML) each monitored web site and their current (last check) status.
        # python -m http.server 8080
        # access the url: http://localhost:8080/
        with open('index.html', 'w') as file:
            file.write(HTML_WRAP % message_string)
        time.sleep(args.checking_period)  # Periodically makes an HTTP request to each page every half hour


if __name__ == '__main__':
    _launch()
