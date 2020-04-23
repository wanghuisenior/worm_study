import os

import cv2

imgName = "dog_cat.png"
xmlFileName = "xml\Haar_cascade_dog.xml"

if not (os.path.exists(imgName) and os.path.exists(imgName)):
	print("图片或检测器文件不存在")
# 矩形颜色和描边
color = (0, 0, 255)  # 红色框
strokeWeight = 1  # 线宽为 1

# 测试训练的检测器是否可用
windowName = "目标检测"
img = cv2.imread(imgName)

# 加载检测文件
cascade = cv2.CascadeClassifier(xmlFileName)

rects = cascade.detectMultiScale(img)

# 获取矩形列表
for x, y, width, height in rects:
	cv2.rectangle(img, (x, y), (x + width, y + height), color, strokeWeight)

# 显示
cv2.imshow(windowName, img)
cv2.waitKey(0)
