import os

import cv2

result = []
def get_all(cwd):
	get_dir = os.listdir(cwd)
	print(get_dir)
	for i in get_dir:
		sub_dir = os.path.join(cwd, i)
		if os.path.isdir(sub_dir):
			get_all(sub_dir)
		else:
			result.append(i)


# 处理样本，灰度化，归一化，大小为（50, 50）
path = "cascadetrain/positive/img/"
print(os.path.exists(path))
get_all(path)