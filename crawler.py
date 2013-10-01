#!/usr/bin/env python2

import re
import os
import urllib
import urllib2
import logging
from lxml import html
from cookielib import CookieJar

TASKS_URL = "http://acm.timus.ru/problemset.aspx?page=all"
AUTH_URL = "http://acm.timus.ru/authedit.aspx"
CONFIG_PATH = "./crawler.conf"

logging.basicConfig(filename='/tmp/logfile.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_secrets():
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as fd:
            config = fd.readlines()
        return parse_config(config)
    raise IOError("%s is absent!" % CONFIG_PATH)

def parse_config(config):
    JUDGE_ID = ""
    PASSWORD = ""
    judgeid_regexp = re.compile(r'^JUDGE_ID')
    password_regexp = re.compile(r'^PASSWORD')
    comment_regexp = re.compile(r'^#')
    for line in config:
        if comment_regexp.match(line):
            continue
        if judgeid_regexp.match(line):
            JUDGE_ID = line.split(':')[1].strip()
        if password_regexp.match(line):
            PASSWORD = line.split(':')[1].strip()
    return JUDGE_ID, PASSWORD

try:
    JUDGE_ID, PASSWORD = get_secrets()
except IOError, e:
    JUDGE_ID = "MYID"
    PASSWORD = "PASSWORD"


cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
data = urllib.urlencode({"Action": "edit",
                         "JudgeID": JUDGE_ID,
                         "Password": PASSWORD})
response = opener.open(AUTH_URL, data)

def fill_dict(task):
    status, num, name, _, _, price = task.getchildren()
    if status.find('a'):
        status = 'ok.gif' in status.find('a').find('img').attrib.get('src')
    else:
        status = False
    return {num.text_content(): [status, name.text_content(), price.text_content()]}

opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', 'Locale=Russian'))
fd = opener.open(TASKS_URL)

doc = html.fromstring(fd.read())
body = doc.body

tasks_list = body.find_class('content')

tasks_dict = {}
for task in tasks_list:
    if task[0].tag == 'th':
        continue
    tasks_dict.update(fill_dict(task))

for task in tasks_dict:
    logging.debug(u'%s: %s' % (task, tasks_dict[task]))
