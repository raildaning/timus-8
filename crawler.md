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

    import urllib
    import urllib2
    from lxml import html
    from cookielib import CookieJar

    TASKS_URL = "http://acm.timus.ru/problemset.aspx?page=all"
    AUTH_URL = "http://acm.timus.ru/authedit.aspx"
    JUDGE_ID = "YOUID"
    PASSWORD = "PASS"

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

    import logging

    logging.basicConfig(filename='/tmp/logfile.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    for task in tasks_dict:
        logging.debug(u'%s: %s' % (task, tasks_dict[task]))

Чтобы знать именно наши результаты,
нужно сначала авторизоваться в системе и получить нужные куки

    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    data = urllib.urlencode({"Action": "edit",
                             "JudgeID": JUDGE_ID,
                             "Password": PASSWORD
                             })
    response = opener.open(AUTH_URL, data)

Получаем сырой xhtml, но нужно указать правильную локаль,
чтобы получить задачи на русском языке.

    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'Locale=Russian'))
    fd = opener.open(TASKS_URL)

И затем скармливаем его lxml и получаем тело страницы

    doc = html.fromstring(fd.read())
    body = doc.body

Каждая запись задачи хранится в элементе tr с классом *content*

    tasks_list = body.find_class('content')

Мы будем хранить наши записи в дикте вида
{Номер: [статус(True|False), название(String), стоимость(Integer)]}
Среди прочих нам попадётся строчка таблицы заголовок, её нужно пропустить

    tasks_dict = {}
    for task in tasks_list:
        if task[0].tag == 'th':
            continue
        tasks_dict.update(fill_dict(task))

Заполнять задачи будем в следующем порядке:

1.  Если в первом *td* содержится изображение "ok.gif" &#x2013; задача выполнена

2.  Второй *td* содержит номер задачи

3.  Третий *td* содержит название задачи

4.  Четвёртый и пятый *td* мы пропускаем

5.  Пятый *td* содержит стоимость задания

    def fill_dict(task):
        status, num, name, _, _, price = task.getchildren()
        if status.find('a'):
            status = 'ok.gif' in status.find('a').find('img').attrib.get('src')
        else:
            status = False
        return {num.text_content(): [status, name.text_content(), price.text_content()]}

Осталось записать результат в org-file

    import logging

    logging.basicConfig(filename='/tmp/logfile.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    for task in tasks_dict:
        logging.debug(u'%s: %s' % (task, tasks_dict[task]))
