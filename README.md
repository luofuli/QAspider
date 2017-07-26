---
title: python 爬虫 小木虫论坛
tags: 爬虫
date: 2017-07-25 17:39
status: public
---

# 前言
## 这件事的来由
因为导师项目需要我爬取小木虫论坛的基金申请栏目下的论坛数据，所以便又重操就业（两年前接触过一次爬虫后就再也没有做过了），当作新知识一样学习了一下爬虫的整个流程，需要注意的是接下来的可能对于新手（好吧我承认我写的可能也不适合新手看。。）并且想通过一个实际例子学习爬虫的可能比较有实际意义。

# 爬虫准备工作
## 爬虫是什么？
爬虫的形象的解释，知乎上很多，我找了一个看起来挺好理解的：
 想象你是一只蜘蛛，现在你被放到了互联“网”上。那么，你需要把所有的网页都看一遍。怎么办呢？没问题呀，你就随便从某个地方开始，比如说人民日报的首页，这个叫initial pages，用$表示吧。在人民日报的首页，你看到那个页面引向的各种链接。于是你很开心地从爬到了“国内新闻”那个页面。太好了，这样你就已经爬完了俩页面（首页和国内新闻）！暂且不用管爬下来的页面怎么处理的，你就想象你把这个页面完完整整抄成了个html放到了你身上。突然你发现， 在国内新闻这个页面上，有一个链接链回“首页”。作为一只聪明的蜘蛛，你肯定知道你不用爬回去的吧，因为你已经看过了啊。所以，你需要用你的脑子，存下你已经看过的页面地址。这样，每次看到一个可能需要爬的新链接，你就先查查你脑子里是不是已经去过这个页面地址。如果去过，那就别去了。好的，理论上如果所有的页面可以从initial page达到的话，那么可以证明你一定可以爬完所有的网页。
原文链接：https://www.zhihu.com/question/20899988/answer/24923424
## 框架选择： request + bs4(BeautifulSoup)
爬虫之前先去知乎上搜寻了大半天，寻找一种最适合自己的技术框架。我的目标定位是：快速简洁。最开始选择urllib2连接网站，获取到html内容（相当于把浏览器F12看到的html内容抓下来），然后再使用python的re包通过正则匹配来解析网站，提取我需要的内容。但是后面发现request 比urllib2好用多了，bs4里面的BeautifulSoup来解析网页也特别爽（因为自己写正则匹配有时候总是考虑不全面），因此我就不介绍自己使用urllib2的各种坑啦，直接上request和bs4。
## request 入门
request 中文官网[http://docs.python-requests.org/zh_CN/latest/index.html](http://docs.python-requests.org/zh_CN/latest/index.html)
第一步：[安装最新的request](http://docs.python-requests.org/zh_CN/latest/user/install.html#install)
第二步：随便抓个网页，比如 [新浪新闻](http://news.sina.com.cn/)，一行代码就ok
python版本：2.7
``` python
import request
resp = requests.get(http://news.sina.com.cn/)   # 返回unicode
print(resp)
```
第三步：有时候因为各种原因第一次没有获取到url的内容，我们就需要捕捉异常并重试几次，写个函数解决这个问题，以后每次就可以通过get_html(targetUrl)来获取网页内容了。
``` python
def get_html(targetUrl):
    try:
        resp = requests.get(targetUrl)
        if resp.status_code>=300:    # 表示没有正常获取，状态码见：https://zh.wikipedia.org/zh-hans/HTTP%E7%8A%B6%E6%80%81%E7%A0%81
            for i in range(5):    # 重试5次
                print('retry{}:{}'.format(i,targetUrl))
                resp = requests.get(targetUrl)
                if resp.status_code<300:
                    break
                sleep(0.25)     # 每秒最多5个请求
        return resp.text
    except Exception as e:
        return None
```
## bs4 入门
之前有讲过，如果自己写正则表达式难免因为考虑不周而出错，比如要获得一个<div></div>标签里的内容，如果用贪婪匹配看起来是可以的但是如果<div></div>标签嵌套了<div></div>标签，那就匹配到后者</div>，所有这个时候用一些别人造好的结构化解析html文档的包就很方便啦，比如bs4里面的BeautifulSoup。
BeautifulSoup中文官网 [https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html](https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html)
### 安装BeautifulSoup和解析器
安装方法见中文官网
解析器最好用lxml，前往不要用python内置的"html.parser"
why：见**搜索文档树**的章节
### 快速开始
``` python
from bs4 import BeautifulSoup
soup = BeautifulSoup(open("index.html"))  
# 或者
soup = BeautifulSoup("<html>data</html>")
```
下面两种等价，也就是默认使用lxml（安装成功后）
``` python
soup = BeautifulSoup(open("index.html"))  
soup = BeautifulSoup(open("index.html"),'lxml')  
```
### 属性的种类
html是有很多tag组成的，所以BeautifulSoup有以下种类Tag , NavigableString , BeautifulSoup , Comment 
- Tag：html的tag，每个tag都有name和很多个Attributes（属性操作与字典相同），例如：
``` python
soup = BeautifulSoup('<b class="boldest">Extremely bold</b>')
tag = soup.b
tag.name
# b
tag['class']
# boldest
```
- BeautifulSoup：这个对象表示的是一个文档的全部内容，操作与Tag对象类似，只是它的name是唯一的'document'，但是没有Attributes，但是可以像Tag一样遍历和搜索文档树
- NavigableString：tag标签中的字符串
``` python
soup = BeautifulSoup('<b class="boldest">Extremely bold</b>')
tag = soup.b
tag.string
# u'Extremely bold'
type(tag.string)
# <class 'bs4.element.NavigableString'> 
unicode_string = unicode(tag.string)  # 转换成普通的Unicode字符串更节省内存
unicode_string
# u'Extremely bold'
type(unicode_string)   
# <type 'unicode'>
```
> 使用.string属性的时候要特别小心，如果tag只有一个 NavigableString 类型子节点,那么这个tag可以使用 .string 得到子节点

也就是对于下面这个例子：
``` python
soup = BeautifulSoup('<p>a<br>b</p>')
p_tag = soup.p
p_tag.string
# 输出结果是 None,因为p_tag有三个子节点，一个a字符串，一个<br>标签，一个b字符串，可以通过.contents查看
```
- Comment： 注释。Tag , NavigableString , BeautifulSoup 几乎覆盖了html和xml中的所有内容,但是还有一些特殊对象.容易让人担心的内容是文档的注释部分，用的很少，不多说了。
 
### 遍历文档树
遍历文档树最重要的就是要明白'子节点'这个概念
> 一个Tag可能包含多个**字符串（NavigableString）**或其它的**Tag**,这些都是这个Tag的子节点
BeautifulSoup中字符串节点（NavigableString）不支持这些属性,因为字符串没有子节点。

也就是说对于 `“<p>a<br>b</p>”`里面的p标签它的子节点有三个 a，` <br>`， b

遍历的方法我认为两种方式：
- 直接通过tag的名字遍历当前Tag下的文档树，比如index.html（以后都以这个为例子）
- 通过.contents 、 .children、 .descendants、.string、.strings 和 stripped_strings等获取子节点，具体见官方文档。
``` html
<html>
    <head>
        <title>The Dormouse's story</title>
    </head>
    <body>
        <p class="title"><b>The Dormouse's story</b></p>
       <p class="story">There were three little sisters; and their names were
            <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
            <a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
            <a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
    </body>
```
``` python
soup = BeautifulSoup('index.html')
soup.head   
# <head><title>The Dormouse's story</title></head>
soup.title
# <title>The Dormouse's story</title>
```
如果想获得所有的p标签怎么办呢？那就要用到搜索的方法find_all()啦，见下一章。
> 实际上除了涉及到父子、前后关系的时候就用这种遍历的方法，我不推荐用标签名字，因为find_all()配合正则表达式更通用。

###  搜索文档树（最常用）
介绍一个find_all()就够用啦，find()只是返回匹配的第一个

首先介绍过滤器
> 过滤器： *字符串* ,*正则表达式* ,*列表*, *True（表示任意）* .

然后看看find_all()

> find_all( name , attrs , recursive , text , \*\*kwargs )

第一个参数：查找所有名字为 name 的tag，可使用**过滤器**
第二个参数：按照tag属性搜索，比如：id='link2'或者class_='codelight'(注意class要有下划线，因为class是python关键字)，可使用**过滤器**
第三个参数：是否递归（不递归默认文档树只遍历一层）
第四个参数：通过 text 参数可以搜搜文档中的字符串内容，可使用**过滤器**

好抽象是吧，以上面的个例子说明
``` python
soup.find_all("title")
# [<title>The Dormouse's story</title>]

soup.find_all(["title","p"])
#  <title>The Dormouse's story</title>
#  <p class="title"><b>The Dormouse's story</b></p>
#  <p class="story">xxxxxx</p>

soup.find_all("p", class_="title")
# [<p class="title"><b>The Dormouse's story</b></p>]

soup.find_all(id=re.compile("link"))
# [<a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
#  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
#  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]

soup.find(text=re.compile("sisters"))
# u'There were three little sisters; and their names were\n'
```

> 此处解释我用"html.parser"遇到的坑

``` python
soup = BeautifulSoup('<p>I love Lancy, <br>but she loves Bob.</p>','lxml')
soup.p.contents
Out[3]: [u'I love Lancy, ', <br/>, u'but she loves Bob.']
soup.p.find_all(text=True, recursive=False)
Out[4]: [u'I love Lancy, ', u'but she loves Bob.']
soup = BeautifulSoup('<p>I love Lancy, <br>but she loves Bob.</p>','html.parser')
soup.p.contents
Out[5]: [u'I love Lancy, ', <br>but she loves Bob.</br>]
soup.p.find_all(text=True, recursive=False)
Out[6]: [u'I love Lancy, ']
```
可以看出html.parser的容错能力太差了，所以千万别用
所以也总结出来了对于这种嵌套的标签，获取标签内所有文本内容的方法（lxml才能做到）：
`tag.find_all(text=True, recursive=False)` 返回的是列表哦，然后再`' '.join(tag)`

# 爬取小木虫
## 总体思路
因为项目需要的是基金申请的QA数据，即一问一答数据，所以我就只爬取“基金申请->疑难解答”(http://muchong.com/f-234-1-typeid-52)帖子问题以及回答。先看看疑难解答栏目下的网页结构：
![](~/19-28-14.jpg)
最上方是url，其中http://muchong.com/f-234-x-typeid-52 中的x就是第几页（多试几页就可以找到这个规律），在右边中部可以看到最多181页。大致浏览一下，每页大概100个帖子，然后每个贴子有一个标题和当前帖子的总页数，还有发帖者和时间等等。点开某一个贴子就跳转到某个页面：http://muchong.com/t-y-z  其中y就是这个帖子的id，z是这个帖子当前的页数。
ok，到这里url的构造大概清楚了：先通过主页获取到最大的帖子页数（因为小木虫更新不太频繁，所以我就直接看了是181页），再让x遍历1-181，通过url：http://muchong.com/f-234-x-typeid-52获取到每个页面的所有帖子的t-url和t-title，在通过这个t-url获取到单个帖子的内容。
## 获取所有帖子的t-url和t-tile和最大页数
``` python
# 获取小木虫页面所有帖子的url，标题，和每个帖子的最大页数
def get_qa_url(max_page):
    qa_urls = []
    for i in range(1,max_page+1):
        url = 'http://muchong.com/f-234-%s-typeid-52'%(i)
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
```
##  获取每个帖子的问答数据
``` python
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
    return answers
```
## 遍历获取所有帖子，并且分文件存储
``` python
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
```

# 解决爬虫ip被封问题
大概爬了一千多个帖子把，ip就被封了，表现就是返回的html内容是空的，然后通过浏览器也打不开或者空白。
在网上谷歌了很久，尝试了以下解决方法：
1、用vpn，这样子封的就是vpn的服务器ip，封了就手动换一个代理服务器就可以，缺点是手动换太麻烦
2、自己维护一个代理ip池，做法就是定期去各种代理ip网站上爬一堆，验证有效性（访问一个稳定的网站，如果失败了就无效），无效的丢掉，有效的存数据库，然后每次爬的时候，对 ip 做评分，好的加分，坏的减分，低于阈值的随机丢弃。介于太复杂了，虽然自己很想尝试，但是最后还是放弃了
3、买一个稳定靠谱的代理ip。我最后选择了[阿布代理](https://www.abuyun.com/)，可以先联系QQ客服试用几个小时。

怎么用代理ip呢？很简单，在[接入指南](https://www.abuyun.com/http-proxy/pro-manual.html)里面有很多语言的接入代码，找到python就行了（注意是动态版还是专业版）

# 源代码
[github](https://github.com/jimiyulu/QAspider)
[blog](http://luofuli.farbox.com/post/pa-chong/pythonpa-chong-xiao-mu-chong)

# 后记
还是很想尝试自己维护一个ip代理池嘻嘻，感觉程序媛用付费的总是不太好。

