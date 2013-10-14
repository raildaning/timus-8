<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Основная идея</a></li>
<li><a href="#sec-2">2. Реализация</a></li>
</ul>
</div>
</div>

# Основная идея

Необходимо собрать все задачи с [timus.ru](http://acm.timus.ru/problemset.aspx)
и представить их в виде org-файла (timus.org).

-   Структура каждой задачи должны быть вида:

        * {TODO|DONE} имя-задачи                                        :сложность:
          текст задания

          org-babel вставка с curl-запросом отправки текстового файла tasknum_timus.py

-   Создать для каждой задачи файл tasknum\_timus.org с содержанием

        Текст задачи

        #+name: имя_задачи
        #+begin_src python :results output :shebang "#!/usr/bin/env python3" :tangle $tasknum_timus.py

        #+end_src

-   Ключ для обновления только основного файла, не трогающий файлы решений

# Реализация

Даные мы будем получать со страницы с таблицей задач

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
            return u"""* {status} {name:<40}:{price}:\n{problem}\n{curl_query}""".format(
                status=self.status and u"DONE" or u"TODO", name=self.name,
                price=self.price, problem=self.get_problem(),
                curl_query=u"{curl-query}")

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
                        if 'problem_source' in element:
                            continue
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

Подготовим возможность логгировать ход выполения нашего скрипта

    logging.basicConfig(filename='/tmp/logfile.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

Чтобы знать именно наши результаты,
нужно сначала авторизоваться в системе и получить нужные куки,
но сначала надо получить наши логин и пароль, если мы указали их в отдельном файле

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

Необходимо установить все Cookie: русскую локаль и добавить систему хранения
куков авторизации  — CookieJar

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

Получаем сырой xhtml

    fd = get_opener().open(TASKS_URL)

И затем скармливаем его lxml и получаем тело страницы

    doc = html.fromstring(fd.read())

Каждая запись задачи хранится в элементе tr с классом *content*

    raw_tasks_list = doc.body.find_class('content')

Мы будем хранить наши записи в списке вида
[Номер(Integer), статус(True|False), название(String), стоимость(Integer)]
Среди прочих нам попадётся строчка таблицы заголовок, её нужно пропустить

    tasks_list = []
    for task in raw_tasks_list:
        if task[0].tag == 'th':
            continue
        tasks_list += [get_task_line(task)]

Заполнять задачи будем в следующем порядке:

1.  Если в первом *td* содержится изображение "ok.gif" &#x2013; задача выполнена

2.  Второй *td* содержит номер задачи

3.  Третий *td* содержит название задачи

4.  Четвёртый и пятый *td* мы пропускаем

5.  Пятый *td* содержит стоимость задания

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

Осталось записать результат в org-file

    def create_task(num, status, name, price):
        document[num] = Task(num, status, name, price)

    for task in tasks_list:
        create_task(*task)

    for task in sorted(document, key=lambda x: int(document[x].price)):
        template += "\n"
        template += document[task].get_task()

Для хранения всего документа создадим класс записей задач

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

        <<get_task>>

        <<get_problem>>

Функция, возвращающая для каждой задачи запись в org-файл

    def get_task(self):
        return u"""* {status} {name:<40}:{price}:\n{problem}\n{curl_query}""".format(
            status=self.status and u"DONE" or u"TODO", name=self.name,
            price=self.price, problem=self.get_problem(),
            curl_query=u"{curl-query}")

Получаем описание задачи с сайта

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
                    if 'problem_source' in element:
                        continue
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
