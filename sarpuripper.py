import requests
import sys
import random
import string

from rq import Queue
from rq.job import Job
from worker import conn
from flask import Flask, request, render_template
from bs4 import BeautifulSoup as bs
from urlparse import parse_qs
from subprocess import check_call as call 
from os import devnull


app = Flask(__name__)
app.debug = True
q = Queue(connection=conn)


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


def process_file(url, rnd):
    tmp_file_from = '/tmp/{}.flv'.format(rnd)
    tmp_file_to = '/tmp/{}.mp4'.format(rnd)

    svars = get_stream_vars(url)
    if svars:
        complete_url = '{}/{}'.format(svars['streamer'][0], svars['file'][0])
        rip_stream(complete_url, tmp_file_from)
        convert_file(tmp_file_from, tmp_file_to)
        return tmp_file_to
 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        rnd = ''.join(
            [random.choice(
                string.ascii_letters + string.digits) for n in xrange(32)])
        url = request.form['url']
        job = q.enqueue_call(
            func="sarpuripper.process_file", args=(url, rnd), result_ttl=600)
        print job.get_id()
    return render_template('index.html')


@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202


if __name__ == '__main__':
    app.run()
