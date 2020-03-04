#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @FileName: 爬取豆瓣电影top250.py
 @Author: 王辉/Administrator
 @Email: wanghui@zih718.com
 @Date: 2019-02-16 15:20
 @Description:
"""
import os
import random


class MovieTop(object):
    def __init__(self, name):
        self.name = name


class P:
    count = 0


if __name__ == '__main__':
    a = MovieTop('adfadsf')
    print(a.name)
    a = P()
    b = P()
    c = P()
    P.count+=100
    c.count += 1
    # print(a.count)
    # print(b.count)
    # print(c.count)

    import requests
    res=requests.get('http://www.baidu.com',{'wdqq':'a'})
    print(res.status_code)
    print(res.text)
    print(dir(res))
