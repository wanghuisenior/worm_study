#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @FileName: 直播源爬取.py
 @Author: 王辉/Administrator
 @Email: wanghui@zih718.com
 @Date: 2020/2/19 14:51
 @Description:
"""
# 参考https://github.com/wbt5/real-url
# 获取斗鱼直播间的真实流媒体地址，可在PotPlayer、flv.js等播放器中播放。
# 2019年11月2日：修复斗鱼预览地址获取的方法；新增未开播房间的判断。
# 2019年12月4日：斗鱼更新后更简单了，可直接在播放页源码的JS中找到播放地址。
import os
import sys

import requests
import re
import execjs
import time
import hashlib

"""
打包为exe格式
   1、安装pyinstaller
      升级pip
      pip install pyinstaller
   2、开始打包，在命令行或者powershell窗口输入
      pyinstaller -F 路径.py
      更换图标
      pyinstaller.exe -F --i 图标.icon 要打包的文件.py
      例如： pyinstaller.exe -F --i .\icon.ico .\直播源爬取.py
"""
# 直播源文件名称
live_xml_name = '直播源.asx'
txt = '直播源.txt'
if os.path.exists(live_xml_name):
	os.remove(live_xml_name)
if os.path.exists(txt):
	os.remove(txt)


##########################################################斗鱼直播爬取开始########################################################
def get_tt():
	tt1 = str(int(time.time()))
	tt2 = str(int((time.time() * 1000)))
	today = time.strftime('%Y%m%d', time.localtime())
	return tt1, tt2, today


def get_homejs(rid):
	room_url = 'https://m.douyu.com/' + rid
	response = requests.get(url=room_url)
	pattern_real_rid = r'"rid":(\d{1,7})'
	real_rid = re.findall(pattern_real_rid, response.text, re.I)[0]
	if real_rid != rid:
		room_url = 'https://m.douyu.com/' + real_rid
		response = requests.get(url=room_url)
	homejs = ''
	pattern = r'(function ub9.*)[\s\S](var.*)'
	result = re.findall(pattern, response.text, re.I)
	str1 = re.sub(r'eval.*;}', 'strc;}', result[0][0])
	homejs = str1 + result[0][1]
	return homejs, real_rid


def get_sign(rid, post_v, tt, ub9):
	docjs = execjs.compile(ub9)
	res2 = docjs.call('ub98484234')
	str3 = re.sub(r'\(function[\s\S]*toString\(\)', '\'', res2)
	md5rb = hashlib.md5((rid + '10000000000000000000000000001501' + tt + '2501' +
						 post_v).encode('utf-8')).hexdigest()
	str4 = 'function get_sign(){var rb=\'' + md5rb + str3
	str5 = re.sub(r'return rt;}[\s\S]*', 'return re;};', str4)
	str6 = re.sub(r'"v=.*&sign="\+', '', str5)
	docjs1 = execjs.compile(str6)
	sign = docjs1.call(
		'get_sign', rid, '10000000000000000000000000001501', tt)
	return sign


def mix_room(rid):
	result1 = 'PKing'
	return result1


def get_pre_url(rid, tt):
	request_url = 'https://playweb.douyucdn.cn/lapi/live/hlsH5Preview/' + rid
	post_data = {
		'rid': rid,
		'did': '10000000000000000000000000001501'
	}
	auth = hashlib.md5((rid + str(tt)).encode('utf-8')).hexdigest()
	header = {
		'content-type': 'application/x-www-form-urlencoded',
		'rid': rid,
		'time': tt,
		'auth': auth
	}
	response = requests.post(url=request_url, headers=header, data=post_data)
	response = response.json()
	pre_url = ''
	if response.get('error') == 0:
		real_url = (response.get('data')).get('rtmp_live')
		if 'mix=1' in real_url:
			pre_url = mix_room(rid)
		else:
			pattern1 = r'^[0-9a-zA-Z]*'
			pre_url = re.search(pattern1, real_url, re.I).group()
	return pre_url


def get_sign_url(post_v, rid, tt, ub9):
	sign = get_sign(rid, post_v, tt, ub9)
	request_url = 'https://m.douyu.com/api/room/ratestream'
	post_data = {
		'v': '2501' + post_v,
		'did': '10000000000000000000000000001501',
		'tt': tt,
		'sign': sign,
		'ver': '219032101',
		'rid': rid,
		'rate': '-1'
	}
	header = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Mobile Safari/537.36'
	}
	response = requests.post(url=request_url, headers=header, data=post_data).json()
	if response.get('code') == 0:
		real_url = (response.get('data')).get('url')
		if 'mix=1' in real_url:
			result1 = mix_room(rid)
		else:
			pattern1 = r'live/(\d{1,8}[0-9a-zA-Z]+)_?[\d]{0,4}/playlist'
			result1 = re.findall(pattern1, real_url, re.I)[0]
	else:
		result1 = 0
	return result1


def get_douyu_url(rid):
	rid = str(rid)
	tt = get_tt()
	url = get_pre_url(rid, tt[1])
	if url:
		return "http://tx2play1.douyucdn.cn/live/" + url + ".flv?uuid="
	else:
		result = get_homejs(rid)
		real_rid = result[1]
		homejs = result[0]
		real_url = get_sign_url(tt[2], real_rid, tt[0], homejs)
		if real_url != 0:
			real_url = "http://tx2play1.douyucdn.cn/live/" + real_url + ".flv?uuid="
		else:
			real_url = 0
		return real_url


def get_url_from_js(rid):
	# 从播放页源代码中直接匹配地址
	header = {
		'Content-Type': 'application/x-www-form-urlencoded'
	}
	try:
		response = requests.get('https://www.douyu.com/{}'.format(rid), headers=header).text
		real_url = re.findall(r'live/({}[\d\w]*?)_'.format(rid), response)[0]
	except:
		real_url = '直播间未开播或不存在'
	return "http://tx2play1.douyucdn.cn/live/" + real_url + ".flv?uuid="


# rid = input('请输入斗鱼数字房间号：\n')
# # real_url = get_real_url(rid)
# # print('该直播间地址为：\n' + real_url)
# #
# # # print(get_url_from_js('85894'))
##########################################################斗鱼直播爬取结束########################################################
##########################################################虎牙直播爬取结束########################################################
def get_huya_url(rid):
	room_url = 'https://m.huya.com/' + str(rid)
	header = {
		'Content-Type': 'application/x-www-form-urlencoded',
		'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Mobile Safari/537.36'
	}
	response = requests.get(url=room_url, headers=header)
	pattern = r"hasvedio: '([\s\S]*.m3u8)"
	result = re.findall(pattern, response.text, re.I)
	if result:
		real_url = result[0]
		real_url = re.sub(r'_1200[\s\S]*.m3u8', '.m3u8', result[0])
	else:
		real_url = 0
	return real_url


# rid = input('请输入虎牙房间号：\n')
# real_url = get_real_url(rid)
# print('该直播间源地址为：\n' + real_url)
##########################################################虎牙直播爬取结束########################################################
def update_file(name, id):  # 更新写入直播源文件
	douyu_url = 0
	huya_url = 0
	try:
		douyu_url = get_douyu_url(id)
		huya_url = get_huya_url(id)
		if not huya_url == 0:
			if not huya_url.startswith('https:'):
				huya_url = 'https:' + huya_url
	except IndexError:
		pass
	if douyu_url:
		with open(txt, 'a', encoding='utf-8') as t:
			t.write(name + '\n' + douyu_url + '\n')
			t.close()
		with open(live_xml_name, 'a', encoding='utf-8') as f:
			f.write('<entry>\n')
			f.write('<title>' + name + '</title>\n')
			f.write('<ref href="' + douyu_url + '"/>\n')
			f.write('</entry>\n')
			f.close()
			print(name, '直播地址', douyu_url)
	elif huya_url:
		with open(txt, 'a', encoding='utf-8') as t:
			t.write(name + '\n' + huya_url + '\n')
			t.close()
		with open(live_xml_name, 'a', encoding='utf-8') as f:
			f.write('<entry>\n')
			f.write('<title>' + name + '</title>\n')
			f.write('<ref href="' + huya_url + '"/>\n')
			f.write('</entry>\n')
			f.close()
			print(name, '直播地址', huya_url)
	else:
		print(name, '未开播！')


"""
我
是
分
割
线
"""
flag = input("输入0继续，输入斗鱼或虎牙直播间id获取其他直播间地址\n")
if flag != '0':
	update_file('未知直播间', flag)
update_file('芜湖大司马丶的直播间', 606118)
update_file('洞主丨歌神洞庭湖的直播间', 138243)
update_file('主播油条的直播间', 56040)
update_file('余小C真的很强的直播间', 1126960)
update_file('智勋勋勋勋的直播间', 312212)
update_file('faker的直播间', 1691127)
update_file('即将拥有人鱼线的PDD直播间', 101)
update_file('赏金术士的直播间', 912360)
update_file('卡尔的直播间', 521000)
update_file('霸哥的直播间', 189201)
"""
我
是
分
割
线
"""
# 写入页首和页尾
with open(live_xml_name, 'r+', encoding='utf-8') as f:
	content = f.read()
	f.seek(0, 0)
	f.write('<asx version="3.0">\n' + content)
	f.write('</asx>\n')
	f.write('<!-- 下面是注释内容，获取到斗鱼id：312212rwRnMhB4ZM_4000p 后可通过修改4000p定义清晰度 -->\n')
	f.write('<!-- href="http://tx2play1.douyucdn.cn/live/312212rwRnMhB4ZM_4000p.m3u8" -->')
	f.close()
print("直播源爬取结束！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！")
time.sleep(3)
sys.exit()
