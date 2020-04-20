#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 @FileName: vlc_palyer.py
 @Author: 王辉/Administrator
 @Email: wanghui@zih718.com
 @Date: 2020/2/21 17:43
 @Description:
"""
import os
import platform
import threading
import tkinter as tk
import sqlite3
import requests
import re
#pip3 install PyExecJS
import execjs
import time
import hashlib
# 设置VLC库路径，需在import vlc之前
from tkinter import ttk

os.environ['PYTHON_VLC_MODULE_PATH'] = "./vlc-3.0.8"
import vlc


# python -m pip install python-vlc


# os.environ['PYTHON_VLC_LIB_PATH'] = './vlc-3.0.8/libvlc.dll'

#########################################################sqlite 数据库操作类开始##########################################
class DBTool(object):
	def __init__(self):
		"""
		初始化函数，创建数据库连接
		"""
		self.conn = sqlite3.connect('room.db')
		self.c = self.conn.cursor()

	def executeUpdate(self, sql, ob):
		"""
		数据库的插入、修改函数
		:param sql: 传入的SQL语句
		:param ob: 传入数据
		:return: 返回操作数据库状态
		"""
		try:
			self.c.executemany(sql, ob)
			i = self.conn.total_changes
		except Exception as e:
			print('错误类型： ', e)
			return False
		finally:
			self.conn.commit()
		if i > 0:
			return True
		else:
			return False

	def executeDelete(self, sql, ob):
		"""
		操作数据库数据删除的函数
		:param sql: 传入的SQL语句
		:param ob: 传入数据
		:return: 返回操作数据库状态
		"""
		try:
			self.c.execute(sql, ob)
			i = self.conn.total_changes
		except Exception as e:
			return False
		finally:
			self.conn.commit()
		if i > 0:
			return True
		else:
			return False

	def executeQuery(self, sql, ob):
		"""
		数据库数据查询
		:param sql: 传入的SQL语句
		:param ob: 传入数据
		:return: 返回操作数据库状态
		"""
		test = self.c.execute(sql, ob)
		return test

	def executeClearSql(self, sql):
		"""
		数据库数据查询
		:param sql: 传入的SQL语句
		:param ob: 传入数据
		:return: 返回操作数据库状态
		"""
		test = self.c.execute(sql)
		return test

	def close(self):
		"""
		关闭数据库相关连接的函数
		:return:
		"""
		self.c.close()
		self.conn.close()


#########################################################sqlite 数据库操作类结束##########################################
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
##########################################################虎牙直播爬取开始########################################################
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
		if not real_url.startswith('https:'):
			real_url = 'https:' + real_url
	else:
		real_url = 0
	return real_url


# rid = input('请输入虎牙房间号：\n')
# real_url = get_real_url(rid)
# print('该直播间源地址为：\n' + real_url)
##########################################################虎牙直播爬取结束########################################################

#########################################################流媒体播放器开始##########################################
class Player:
	'''
		args:设置 options
	'''

	def __init__(self, *args):
		if args:
			instance = vlc.Instance(*args)
			self.media = instance.media_player_new()
		else:
			self.media = vlc.MediaPlayer()

	# 设置待播放的url地址或本地文件路径，每次调用都会重新加载资源
	def set_uri(self, uri):
		self.media.set_mrl(uri)

	# 播放 成功返回0，失败返回-1
	def play(self, path=None):
		if path:
			self.set_uri(path)
			return self.media.play()
		else:
			return self.media.play()

	# 暂停
	def pause(self):
		self.media.pause()

	# 恢复
	def resume(self):
		self.media.set_pause(0)

	# 停止
	def stop(self):
		self.media.stop()

	# 释放资源
	def release(self):
		return self.media.release()

	# 是否正在播放
	def is_playing(self):
		return self.media.is_playing()

	# 已播放时间，返回毫秒值
	def get_time(self):
		return self.media.get_time()

	# 拖动指定的毫秒值处播放。成功返回0，失败返回-1 (需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
	def set_time(self, ms):
		return self.media.get_time()

	# 音视频总长度，返回毫秒值
	def get_length(self):
		return self.media.get_length()

	# 获取当前音量（0~100）
	def get_volume(self):
		return self.media.audio_get_volume()

	# 设置音量（0~100）
	def set_volume(self, volume):
		return self.media.audio_set_volume(volume)

	# 返回当前状态：正在播放；暂停中；其他
	def get_state(self):
		state = self.media.get_state()
		if state == vlc.State.Playing:
			return 1
		elif state == vlc.State.Paused:
			return 0
		else:
			return -1

	# 当前播放进度情况。返回0.0~1.0之间的浮点数
	def get_position(self):
		return self.media.get_position()

	# 拖动当前进度，传入0.0~1.0之间的浮点数(需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
	def set_position(self, float_val):
		return self.media.set_position(float_val)

	# 获取当前文件播放速率
	def get_rate(self):
		return self.media.get_rate()

	# 设置播放速率（如：1.2，表示加速1.2倍播放）
	def set_rate(self, rate):
		return self.media.set_rate(rate)

	# 设置宽高比率（如"16:9","4:3"）
	def set_ratio(self, ratio):
		self.media.video_set_scale(0)  # 必须设置为0，否则无法修改屏幕宽高
		self.media.video_set_aspect_ratio(ratio)

	# 设置窗口句柄
	def set_window(self, wm_id):
		if platform.system() == 'Windows':
			self.media.set_hwnd(wm_id)
		else:
			self.media.set_xwindow(wm_id)

	# 注册监听器
	def add_callback(self, event_type, callback):
		self.media.event_manager().event_attach(event_type, callback)

	# 移除监听器
	def remove_callback(self, event_type, callback):
		self.media.event_manager().event_detach(event_type, callback)


class App(tk.Tk):
	def __init__(self):
		super().__init__()
		self.player = Player()
		self.title("直播助手 by wanghuisenior")
		self.create_video_view()
		self.create_control_view()
		self.create_tree_view()

	def create_video_view(self):
		# 在这里定义播放器的宽高，大小
		self._canvas = tk.Canvas(self, width='800', height='500', bg="black")
		self._canvas.pack(side=tk.RIGHT, fill='both', expand='yes')
		self.player.set_window(self._canvas.winfo_id())

	def create_control_view(self):
		frame = tk.Frame(self, width=80, padx=10, pady=8, bg='green')
		tk.Button(frame, text="加载", command=lambda: self.click(3)).pack(anchor='nw', side=tk.TOP, padx=10, pady=8)
		# tk.Button(frame, text="播放", command=lambda: self.click(0)).pack(anchor='nw', side=tk.LEFT, padx=5)
		tk.Button(frame, text="暂停", command=lambda: self.click(1)).pack(anchor='nw', side=tk.TOP, padx=10, pady=8)
		tk.Button(frame, text="停止", command=lambda: self.click(2)).pack(anchor='nw', side=tk.TOP, padx=10, pady=8)
		global comboxlist
		comboxlist = ttk.Combobox(frame)  # 初始化
		comboxlist["values"] = ("斗鱼", "虎牙", "3", "4")
		comboxlist.current(0)  # 选择第一个
		# comboxlist.bind("<<ComboboxSelected>>", go)  # 绑定事件,(下拉列表框被选中时，绑定go()函数)
		comboxlist.pack(anchor='nw', side=tk.TOP, padx=3, pady=8)

		global entry1, entry2
		entry1 = tk.Entry(frame)
		entry1.insert(10, '直播间名')
		entry1.pack(anchor='nw', side=tk.TOP, padx=2, pady=8)
		entry2 = tk.Entry(frame)
		entry2.insert(10, '直播间ID')
		entry2.pack(anchor='nw', side=tk.TOP, padx=2, pady=8)
		tk.Button(frame, text="新增", command=lambda: self.click(4)).pack(anchor='nw', side=tk.TOP, padx=10, pady=8)
		tk.Button(frame, text="删除", command=lambda: self.click(5)).pack(anchor='nw', side=tk.TOP, padx=10, pady=8)
		tk.Button(frame, text="清  空", bg='deeppink', command=lambda: self.click(6)).pack(anchor='nw', side=tk.TOP,
		                                                                                 padx=10, pady=8)
		tk.Button(frame, text="隐藏列表", command=lambda: self.click(7)).pack(anchor='nw', side=tk.TOP, padx=2, pady=8)
		tk.Button(frame, text="显示列表", command=lambda: self.click(8)).pack(anchor='nw', side=tk.TOP, padx=2, pady=8)
		frame.pack_propagate(0)
		frame.pack(expand='no', fill="both", side="left", anchor="w")

	def create_tree_view(self):
		global tree
		global player
		player = self.player
		tree = ttk.Treeview(self, show="headings")
		tree.pack(expand=0, fill="both", side="left", anchor="w")
		tree.bind('<Double-1>', tree_double_click)
		tree.bind('<3>', tree_right_click)
		# 定义列
		tree["columns"] = ("id", "platform", "ID", "直播间", "地址", "状态")
		# 设置列属性，列不显示
		tree.column("id", width=40, anchor='n')
		tree.column("platform", width=40, anchor='n')
		tree.column("ID", width=40, anchor='n')
		tree.column("直播间", width=100, anchor='n')  # n，s，e，w，ne，nw，，se，sw
		tree.column("地址", width=100)
		tree.column("状态", width=50, anchor='n')
		# 设置表头
		tree.heading("id", text="id")
		tree.heading("platform", text="ID")
		tree.heading("ID", text="ID")
		tree.heading("直播间", text="直播间")
		tree.heading("地址", text="地址")
		tree.heading("状态", text="状态")
		tree['displaycolumns'] = ("ID", "直播间", "状态")

	def click(self, action):
		if action == 0:
			if self.player.get_state() == 0:
				self.player.resume()
			elif self.player.get_state() == 1:
				pass  # 播放新资源
			else:
				self.player.play("http://tx2play1.douyucdn.cn/live/1126960rrfpXoBAm.flv?uuid=")
		elif action == 1:
			if self.player.get_state() == 1:
				self.player.pause()
		elif action == 2:
			self.player.stop()
		elif action == 3:  # 加载所有主播的状态
			# 添加数据
			threading.Thread(target=load_tree).start()
		# load_tree()
		elif action == 4:
			# print(comboxlist.get(),comboxlist.current())
			list_index = comboxlist.current()
			room_name = ''
			room_id = 0
			try:
				room_name = entry1.get()
				room_id = int(entry2.get())
			except ValueError:
				pass
			if room_id:
				db = DBTool()
				rooms = db.executeQuery('SELECT * FROM room', [])
				flag = True
				for i in rooms:
					if i[1] == room_id:
						flag = False
				if flag:
					# 获取直播源地址并添加到数据库
					if list_index == 0:
						douyu_url = get_douyu_url(room_id)
						state = 1 if douyu_url else 0
						db.executeUpdate('INSERT INTO room (platform,room_id,name, real_url,state) VALUES (?,?,?,?,?)',
						                 [(list_index, room_id, room_name, douyu_url, state)])
					if list_index == 1:
						try:
							huya_url = get_huya_url(room_id)
							state = 1 if huya_url else 0
							# print(huya_url, state)

							db.executeUpdate(
								'INSERT INTO room (platform,room_id,name, real_url,state) VALUES (?,?,?,?,?)',
								[(list_index, room_id, room_name, huya_url, state)])
						except AttributeError:
							pass
					db.close()
			entry1.delete(0, len(entry1.get()))
			entry2.delete(0, len(entry2.get()))
		elif action == 5:
			room_id = 0
			try:
				room_id = int(entry2.get())
			except ValueError:
				pass
			if room_id:
				db = DBTool()
				db.executeDelete('DELETE FROM room WHERE room_id=?', [room_id])
				db.close()
			entry2.delete(0, len(entry2.get()))
		elif action == 6:
			db = DBTool()
			db.executeDelete('DELETE FROM room', [])
			db.close()
		elif action == 7:
			tree.pack_forget()
		elif action == 8:
			tree.pack()
		else:
			pass


def load_tree():
	del_tree(tree)
	db = DBTool()
	rooms = db.executeQuery('SELECT * FROM room', [])
	i = 0
	for r in rooms:
		res = list(r)
		platform = res[1]
		room_id = res[2]
		res[4] = get_douyu_url(room_id) if platform == 0 else get_huya_url(room_id) if platform == 1 else 0
		# db.executeUpdate('UPDATE room SET real_url = ? WHERE room_id = ?', [(res[4],room_id)])
		res[5] = '未开播' if res[4] == 0 else '录播' if 'replay' in res[4] else '已开播'
		if res[1] == 1 and res[4] != 0 and 'replay' not in res[4]:
			print(res[3], res[4])
			if res[2] == 189201:
				# print('----------', res[4])
				str = re.search("\d+.*", res[4]).group()
				res[4] = 'https://al.hls.huya.com/backsrc/' + str
				print(res[3], res[4])
		tree.insert('', i, text='abcd', values=res)
		i += 1
	db.close()


def del_tree(tree):
	x = tree.get_children()
	for item in x:
		# print(item)
		tree.delete(item)


def tree_double_click(event):
	real_url = ''
	for item in tree.selection():
		item_text = tree.item(item, "values")
		# print(item_text)
		real_url = item_text[4]
	player.play(real_url)


def tree_right_click(event):
	flag = tree.identify_row(event.y)
	if flag:
		tree.selection_set(flag)
	for item in tree.selection():
		item_text = tree.item(item, "values")


# print(item_text[0], item_text[1], item_text[2], item_text[3], )


# Player.play(item_text[2])
# Player.play("http://tx2play1.douyucdn.cn/live/606118ryey9Bwn5C.flv?uuid=")


if "__main__" == __name__:
	app = App()
	app.mainloop()

#########################################################流媒体播放器结束##########################################
