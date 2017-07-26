# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import pickle
from time import sleep
import thread

# 获取某个页面的封装函数
def get_html(targetUrl):
    # 要访问的目标页面
    # targetUrl = "http://test.abuyun.com/proxy.php"
    # targetUrl = 'http://www.baidu.com'
    try:
        resp = requests.get(targetUrl, proxies=proxies)
        if resp.status_code >= 300:  # 表示没有正常获取，状态码见：https://zh.wikipedia.org/zh-hans/HTTP%E7%8A%B6%E6%80%81%E7%A0%81
            for i in range(5):  # 重试5次
                print('retry{}:{}'.format(i,targetUrl))
                resp = requests.get(targetUrl, proxies=proxies)
                if resp.status_code<300:
                    break
                sleep(0.25)     # 每秒最多5个请求
        return resp.text
    except Exception as e:
        print(e)
        print(targetUrl)
        return None

# 获取小木虫页面所有帖子的url，标题，和最大页数
def get_qa_url(max_page):
    qa_urls = []
    for i in range(1,max_page+1):
        url = 'http://muchong.com/f-234-%s-typeid-52'%(i)
        if i%5==0:
            print('%s-%s:Get %s'%(i-4,i,url))
        html = get_html(url)
        if not html:    # 如果没有获取到这个页面，就跳过
            continue

        soup = BeautifulSoup(html,'lxml')
        qs_boby = soup.find('div',class_='forum_body xmc_line_lr')
        qs = qs_boby.find_all('tbody')
        for q in qs:
            body = q.find('th',class_='thread-name')
            type = body.find('span').find('a',class_='xmc_blue')
            is_vote = body.find('span', class_='icon_vote xmc_rm10')
            if type and not(is_vote):   # 只有是疑难解答并且不是投票的页面才需要爬虫
                question= body.find('a',class_='a_subject')
                first_url=question['href']
                title = question.get_text()
                base_url = first_url[:-2]
                urls = body.find_all('a',href=re.compile(base_url))
                pages = [url.get_text() for url in urls]
                try:
                    max_page=int(pages[-1])
                except Exception as e:
                    max_page=1
                qa_urls.append({'title':title,'base_url':base_url,'max_page':max_page})
    return qa_urls

# 获取每个帖子的问答数据
def get_qa_detail(base_url,max_page):
    answers = []
    for page in range(1,max_page+1):
        url = base_url+'-'+str(page)
        html = get_html(url)
        if not html:    # 如果没有获取到这个页面，就跳过
            continue

        soup = BeautifulSoup(html,'lxml')  # 千万不要使用'html.parser',解析html一堆问题,比如<br>标签解析时就出现问题
        floors = soup.find_all('tbody',id=re.compile("pid\d+"))

        for floor in floors:
            quality=0  # 不是应助回帖
            upvote_count=0  #点赞数

            # 获取是否是答案
            try:
                title = floor.find('h1',class_='forum_Tit xmc_bm20').find('font').get_text()
                if title==u'【答案】应助回帖':
                    quality=1
            except Exception:
                quality=0
            # print(quality)

            #获取点赞人数
            try:
                upvote = floor.find('td', id=re.compile('qtop')).find('a')
                count = upvote.find_all(text=True, recursive=False)
                count = ''.join(count)
                upvote_count = int(re.findall('\d+',count)[0])
            except Exception:
                upvote_count = 0
            # print(upvote_count)

            # 获取回答内容
            try:
                body = floor.find('div',class_='t_fsz').find('td',valign='top')
                answer = body.find_all(text=True, recursive=False)
                answer = ''.join(answer)
            except Exception as e:
                answer=''
            if answer!='':
                answers.append({'answer':answer,'quality':quality, 'upvote_count':upvote_count})
        # 删去头尾的方法,应对之前的破'html.parse'解析器的方法，气死了
        # for floor in floors:
        #     body = floor.find('div',class_='t_fsz').find('td',valign='top')
        #     answer = body.get_text() # 用get_text 会把'发自小木虫Android客户端'也加入进去
        #     for tag in body.children:
        #         if type(tag)==bs4.element.Tag:
        #             if(tag.name=='fieldset' or tag.name=='font'):
        #                 duoyu = tag.get_text()  # # 去除掉子节点的文字，如：'发自小木虫Android客户端'和应用回帖
        #                 answer = re.sub(duoyu, '', answer)
        #     answers.append(answer)
        #     print(answer)
    return answers

# 遍历获取所有帖子，并且分文件存储
def spider_all(start_page,end_page):
    qas = []
    for i in range(max_qa_len):
        qa_url = all_qa_urls[i]
        if i >= start_page and i < end_page:
            if (i % 1 == 0 or i == max_qa_len - 1):
                print('{}/{}:spider--{}'.format(i, max_qa_len, qa_url['base_url']))
            # {'answer':answer,'quality':quality, 'upvote_count':upvote_count}
            try:
                max_page = qa_url['max_page']
                if max_page > 5:  # 太多页面也没用 http://muchong.com/t-2939387-759 竟然有好几百页
                    max_page = 5  # 只取前5页
                ans = get_qa_detail(base_url=qa_url['base_url'], max_page=max_page)
            except Exception as e:
                print(e)
                print('url:{}')
                ans = []
            if len(ans) > 1:
                ques_title = qa_url['title']
                ques_appendix = ans[0]['answer']
                ans = ans[1:]
                url = qa_url['base_url'] + '-1'
                qas.append({'ques_title': ques_title, 'ques_appendix': ques_appendix, 'ans': ans, 'url': url})
            if (i + 1) % split_bg == 0 or i==max_qa_len - 1:
                store_qas(qas, '%s%s-%s.xml' % (store_path, i - split_bg + 1, i))
                qas = []

# 保存
def store_qas(qas,dst_path):  # qas.append({'ques_title':ques_title,'ques_appendix':ques_appendix,'ans':ans,'url':url})
    def format_qa(qa):
        def replace_(text):
            text = re.sub(u'\r','',text)   # 去掉行首行尾空白符（\n\r等），strip()功能没这么强大
            text = text.strip('\n')
            text = re.sub(u'[ \t<>]','',text)
            text = re.sub(u'[\n]+','<br>',text)
            return text

        ques_title = replace_(qa['ques_title'])
        ques_appendix = replace_(qa['ques_appendix'])
        ques = u'<title>{}</title><apdx>{}<apdx>'.format(ques_title,ques_appendix)
        answers = qa['ans'] # {'answer':answer,'quality':quality, 'upvote_count':upvote_count}
        anss = ''
        for ans in answers:
            ans = u"<answer>{}</answer><quality>{}</quality><upvote>{}</upvote>".format(replace_(ans['answer']), ans['quality'], ans['upvote_count'])
            anss += ans
        return u'<Q>{}</Q>\n<A>{}</A>\n<url>{}</url>\n'.format(ques,anss,qa['url'])

    with open(dst_path,'w') as f:
        for i in range(len(qas)):
            qa = qas[i]
            qa = format_qa(qa)
            f.write(qa.encode('utf-8'))
        print('write to file:%s'%(dst_path))


if __name__=='__main__':
    # 代理服务器
    proxyHost = "proxy.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "H43N9XM439Z7EWVD"
    proxyPass = "D793FACBDE4E9B38"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    store_path = './data/'
    muchong_max_page = 181
    split_bg = 100
    all = 0  # 0不及时爬虫
    thread_count = 6

    if all:
        # 获取所有的页面
        all_qa_urls = get_qa_url(muchong_max_page)  # {'title':title,'base_url':base_url,'max_page':max_page}
        pickle.dump(all_qa_urls, open('data/all_qa_urls.txt', 'w'))
    else:
        all_qa_urls = pickle.load(open('data/all_qa_urls.txt'))

    max_qa_len = (len(all_qa_urls))

    for i in range(thread_count):
        gap = int(max_qa_len/thread_count)
        thread.start_new_thread(spider_all,(i*gap,(i+1)*gap))
        sleep(0.2)

    sleep(3600*12)    # 保证主线程不要退出

    # spider_all(18000,18300)

        # get_qa_detail('http://muchong.com/t-9901803', 1)
    # text = get_html('http://muchong.com/t-9901803-1')
    # open('tmp/detail1.html','w').write(text.encode('utf-8'))
    #
    # text = get_html('http://muchong.com/t-11516693-1')
    # open('tmp/detail0.html', 'w').write(text.encode('utf-8'))



