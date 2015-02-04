import requests
import sys
import random
import string
from bs4 import BeautifulSoup as bs
from urlparse import parse_qs
from subprocess import check_call as call 
from os import devnull


def get_stream_vars(url):
    r = requests.get(url)
    data = r.text
    soup = bs(data)

    for param in soup.find_all('param'):
        if param['name'].lower() == 'flashvars':
            return parse_qs(param['value'])
    return None 


def rip_stream(url, tmp_file):
    print "Ripping stream..."
    DEVNULL = open(devnull, 'w')
    call(['rtmpdump', '-r', url, '-o', tmp_file], 
         stdout=DEVNULL, stderr=DEVNULL, close_fds=True)


def convert_file(from_file, to_file):
    print "Convering flv to mp4"
    DEVNULL = open(devnull, 'w')
    call(['avconv', '-i', from_file, '-codec', 'copy', to_file],
         stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
 

if __name__ == '__main__':
    random = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
    tmp_file_from = '/tmp/{}.flv'.format(random)
    tmp_file_to = '/tmp/{}.mp4'.format(random)

    if len(sys.argv) != 2:
        print "Need exactly one argument: the url"
        exit(1)
    svars = get_stream_vars(sys.argv[1])
    if svars:
        complete_url = '{}/{}'.format(svars['streamer'][0], svars['file'][0])
        print "Stream url found at {}".format(complete_url)
        rip_stream(complete_url, tmp_file_from)
        convert_file(tmp_file_from, tmp_file_to)
        print "File ready at {}".format(tmp_file_to)
