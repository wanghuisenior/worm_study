import cv2
import sys


def getImage(index, path):
	cap = cv2.VideoCapture(0)
	num = 1
	while cap.isOpened():
		ok, frame = cap.read()
		if not ok:
			break
		image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		if cv2.waitKey(1) & 0xFF == ord('c'):
			num = num + 1;
			img_name = '%s/%d.jpg' % (path, num)
			cv2.imwrite(img_name, frame)
		cv2.imshow('getFaceIamge', frame)
	cap.release()
	cv2.destroyAllWindows()


if __name__ == '__main__':
	getImage(0, 'data')
