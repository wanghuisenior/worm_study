#!/usr/bin env python
import os

##########################################################
flag = True  # True:生成正样本描述文件,False:生成负样本描述文件##
rootdir = '狗子'  # 样本图片所在目录                       #
img_type = ['jpg', 'png', 'bmp']  # 允许的图片文件类型
##########################################################

files = os.listdir(rootdir)
name = os.path.split(files[0])
file_name = 'pos.txt' if flag else 'neg.txt'
with open(rootdir + '\\' + file_name, 'w+') as f:
	for file in files:
		# name = os.path.split(file)
		if file.endswith(tuple(img_type)):
			print(file)
			if flag:
				f.write(rootdir + '\\' + file + ' ' + '1 0 0 30 30\n')
			else:
				f.write(rootdir + '\\' + file + '\n')
		else:
			pass
