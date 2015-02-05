#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import sys
import random
import string
import os

from rq import Queue
from rq.job import Job
from worker import conn
from flask import Flask, request, render_template, jsonify
from bs4 import BeautifulSoup as bs
from urlparse import parse_qs
from subprocess import check_call as call 
from os import devnull
from unidecode import unidecode as _
from re import sub


app = Flask(__name__)
app.debug = True
q = Queue(connection=conn)
BASE_DIR = '/tmp/sarpuripper'


def get_soup(url):
    r = requests.get(url)
    data = r.text
    return bs(data)


def get_stream_vars(soup):
    for param in soup.find_all('param'):
        if param['name'].lower() == 'flashvars':
            return parse_qs(param['value'])
    return None 


def get_show_title(soup):
    title = _(soup.find(id='thattatitill').text)
    date = soup.find(class_='sarpur-date').find(text=True)

    result = '{} {}'.format(title, date).strip()

    result = sub(r'[^\w\s]+', '', result)
    result = sub(r'\s+', '_', result)
    return result


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


def process_file(url, rnd, title, svars):

    tmp_file_from = '/tmp/{}.flv'.format(rnd)
    tmp_file_to = '{}/{}.mp4'.format(BASE_DIR, title)

    if os.path.exists(tmp_file_to):
        return tmp_file_to

    if svars:
        complete_url = '{}/{}'.format(svars['streamer'][0], svars['file'][0])
        rip_stream(complete_url, tmp_file_from)
        convert_file(tmp_file_from, tmp_file_to)
        os.remove(tmp_file_from)
        return tmp_file_to
 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        rnd = ''.join(
            [random.choice(
                string.ascii_letters + string.digits) for n in xrange(32)])
        url = request.form['url']

        soup = get_soup(url)
        title = get_show_title(soup)
        svars = get_stream_vars(soup)

        job = q.enqueue_call(
            func="sarpuripper.process_file", args=(url, rnd, title, svars), result_ttl=600)
        return jsonify(job_id=job.get_id(), file_title=title)
    return render_template('index.html')


@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202


if __name__ == '__main__':
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    app.run()
