# -*- encoding:utf-8 -*-

import requests


# 要访问的目标页面
# targetUrl = "http://test.abuyun.com/proxy.php"
targetUrl = 'http://www.baidu.com'

# 代理服务器
proxyHost = "proxy.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息
proxyUser = "H43N9XM439Z7EWVD"
proxyPass = "D793FACBDE4E9B38"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
  "host" : proxyHost,
  "port" : proxyPort,
  "user" : proxyUser,
  "pass" : proxyPass,
}

proxies = {
    "http"  : proxyMeta,
    "https" : proxyMeta,
}

# resp = requests.get(targetUrl, proxies=proxies)
# print resp.status_code
# print resp.text

r = requests.get('http://muchong.com/t-11520192-1', proxies=proxies)
content = r.text
# open('test.html','w').write(content.encode('gbk'))
if r.status_code<300:
    print r.status_code
    # ip = re.search(r'code.(.*?)..code', content)
    # print (ip.group(1))