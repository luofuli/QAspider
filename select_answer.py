# -*- coding: utf-8 -*-
import re
import os
import numpy as np

# 筛选答案的方法1：是否是应助回答*5+点赞数
def method1(ass):
    as_ = []
    for i, anss in enumerate(ass):
        ans = re.findall(u'<answer>(.*?)</answer>',anss)
        quality = re.findall(u'<quality>(.*?)</quality>',anss)
        upvote = re.findall(u'<upvote>(.*?)</upvote>',anss)
        if len(ans)!=len(quality) or len(ans)!=len(upvote):
            return []
        score = [int(quality[j])*5+int(upvote[j]) for j in range(len(ans))]
        k = np.argmax(score)
        select = ans[k]
        # if(len(select)<=1):    # 如果最佳回答为空（表情等），那么选择一个回答最长的最为答案
        #     score = [len(a) for a in ans]
        #     k = np.argmax(score)
        #     select = ans[k]
        as_.append(select)
    return as_

def clean(qs,ps,as_):
    new_qs = []
    new_ps = []
    new_as = []
    for i in range(len(qs)):
        q = re.sub(u'([\[【].*?[\]】])','',qs[i])  # 去掉标题里的【转载】 or [已完结] or [关帖]
        pattern = re.compile(u'[ \t]')   # 去掉空格等空白符
        q = pattern.sub('',q)
        p = pattern.sub('',ps[i])
        a = pattern.sub('',as_[i])
        if len(a)>=1:      # 有答案的才返回
            new_qs.append(q)
            new_ps.append(p)
            new_as.append(a)
    return new_qs,new_ps,new_as

def do_all():
    with open(dst_path+'questions.txt','w') as fq, \
    open(dst_path+'questions_appendix.txt','w') as fp, \
    open(dst_path+'answers.txt','w') as fa:
        for f_name in os.listdir(src_path):
            if '.xml' in f_name:
                data = open(src_path+f_name).read().decode('utf-8')
                data = data.replace('\n','')
                qs_title = re.findall(u'<title>(.*?)</title>',data)
                qs_apdx = re.findall(u'<apdx>(.*?)<apdx>',data)
                ass = re.findall(u'<A>(.*?)</A>',data)
                as_ = method1(ass)
                if len(qs_title)!=len(ass) or len(qs_apdx)!=len(ass):
                    print(u'QA不匹配:{}'.format(f_name))
                elif as_==[]:
                    print(u'answer can not match:{}'.format(f_name))
                else:
                    qs_title,qs_apdx,as_ = clean(qs_title,qs_apdx,as_)
                    fq.write('\n'.join(qs_title).encode('utf-8'))
                    fp.write('\n'.join(qs_apdx).encode('utf-8'))
                    fa.write('\n'.join(as_).encode('utf-8'))

if __name__=="__main__":
    src_path = './data/'
    dst_path = './QA/'

    do_all()