#!/usr/bin/env python2

import re
import os
import urllib
import urllib2
import logging
from lxml import html
from cookielib import CookieJar, Cookie

TIMUS_URL = "http://acm.timus.ru/"
TASKS_URL = TIMUS_URL + "problemset.aspx?page=all"
AUTH_URL = TIMUS_URL + "authedit.aspx"
PROBLEM_URL = TIMUS_URL + "problem.aspx"
CONFIG_PATH = "./crawler.conf"
OPENER = None

with open('./template.org', 'r') as template_file:
    template = template_file.read()

logging.basicConfig(filename='/tmp/logfile.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

document = {}

class Task(object):

    def __init__(self, num, status, name, price):
        self.num = int(num)
        self.status = status
        self.name = name
        self.price = price

    @property
    def url(self):
        return PROBLEM_URL + "?num=%d" % self.num

    def __str__(self):
        return u"{num} {status} {name} {price}".format(
            num=self.num, status=self.status, name=self.name,
            price=self.price)

    def get_task(self):
        return u"""* {status} {name:<40}:{price}:
        {problem}
        {curl_query}""".format(status=self.status, name=self.name, price=self.price,
                               problem=self.get_problem(), curl_query="{curl-query}")

    def table_to_org(self, table):
        return table.text_content()
    
    def get_problem(self):
        opener = get_opener()
        doc = html.fromstring(opener.open(self.url).read())
        problem_text = u""
        try:
            problem_body = doc.xpath("//div[contains(@id,'problem_text')]")[0]
        except IndexError:
            logging.debug('Problem no. {num} has no problem text'.format(num=self.num))
        else:
            for element in problem_body:
                if element.tag == "div":
                    problem_text += u"{text}\n".format(
                        text=element.text_content())
                elif element.tag == "h3":
                    problem_text += u"** {text}\n".format(
                        text=element.text_content())
                elif element.tag == "table":
                    problem_text += u"{text}\n".format(
                        text=self.table_to_org(element))
        finally:
            return problem_text

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


def get_task_line(task):
    """
    XMLElement -> [String, Bool, String, String]
    """
    status, num, name, _, _, price = task.getchildren()
    if status.find('a') is not None:
        status = 'ok.gif' in status.find('a').find('img').attrib.get('src')
    else:
        status = False
    return [num.text_content(), status, name.text_content(), price.text_content()]

def get_opener():
    global OPENER
    if OPENER:
        return OPENER
    cj = CookieJar()
    ck = Cookie(version=0, name='Locale', value='Russian', port=None,
                port_specified=False, domain='acm.timus.ru',
                domain_specified=False, domain_initial_dot=False, path='/',
                path_specified=True, secure=False, expires=None,
                discard=True, comment=None, comment_url=None,
                rest={'HttpOnly': None}, rfc2109=False)
    cj.set_cookie(ck)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    data = urllib.urlencode({"Action": "edit",
                             "JudgeID": JUDGE_ID,
                             "Password": PASSWORD})
    response = opener.open(AUTH_URL, data)
    OPENER = opener
    return opener

fd = get_opener().open(TASKS_URL)

doc = html.fromstring(fd.read())

raw_tasks_list = doc.body.find_class('content')

tasks_list = []
for task in raw_tasks_list:
    if task[0].tag == 'th':
        continue
    tasks_list += [get_task_line(task)]

def create_task(num, status, name, price):
    document[num] = Task(num, status, name, price)

for task in tasks_list:
    create_task(*task)

for task in sorted(document, key=lambda x: int(document[x].price)):
    template += "\n"
    template += document[task].get_task()
