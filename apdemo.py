"""
Simple website monitoring tool. Uses requests. Was going with writing my own
socket, then giving up using http.client.HTTPConnection but realized was hurting my
chances for the job competion with other coandidiates as time might be factor!
"""

import argparse
import logging
import sys
try:
    import requests
except ImportError:
    sys.exit("requests module is missing, use 'pip install requests'"
             "see http://docs.python-requests.org/en/master/")

# create and configure logger
LOG_FORMAT = '%(levelname)s %(asctime)s Status: %(message)s'  #  msg contains checked URLs, their status and the response times
logging.basicConfig(filename='sitelogfile.log',
                    level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt='%Y-%m-%d %H:%M:%S'  # default ISO 8601 format
                    )

def get_site_status(url):
    """
    connection level problems (e.g. the web site is down)
    Measures the time it took for the web server to complete the whole request.
    """
    time_elapsed = None
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        msg = 'connection error'
    except requests.exceptions.HTTPError:
        msg = 'HTTP error occurred'
    except requests.exceptions.Timeout:  # Requests that produced this error are safe to retry.
        msg = 'request timed out'
    else:
        msg = 'site is up, status: {}'.format(r.status_code)
        time_elapsed = str(r.elapsed)
    finally:
        return r, msg, time_elapsed


def check_content(requests_obj, content_requirement):
    """
    content problems (e.g. the content requirements were not fulfilled)
    Verifies that the page content received from the server matches the content requirements.
    """
    return content_requirement in requests_obj.text  # future: probably re is better for more sophisticated requirements


def check_sites(filename):
    """
    Writes a log file that shows the progress of the periodic checks.
    """
    with open(filename, 'r') as f:
        for url in load_file(f):
            r, msg, time_elapsed = get_site_status(url)
            if time_elapsed == None:

            logging.warning(' '.join([url, msg]))
            check_content(url)
                    logging.info(' '.join([url, msg, time_elapsed]))




def load_file(file):
    file.readline()  # throw away first line
    for line in file:
        line.strip()
        yield line


def _launch():
    parser = argparse.ArgumentParser(prog='python -m apdemo',
                                     description='Simple program and command line utility for site monitoring')

    parser.add_argument('filename', action='store',
                        dest='my_value_name',
                        help='Store a simple value')

    parser.add_argument('-t', action='store',
                        dest='checking_period',
                        help='Change default checking period')

    parser.add_argument('--version', action='version',
                        version='%(prog)s 1.0')

    args = parser.parse_args()  # namespace containing the arguments to the command




    # check for internet connectivity

    # Periodically makes an HTTP request to each page
    make_check(args.filename)


if __name__ == '__main__':
    _launch()
