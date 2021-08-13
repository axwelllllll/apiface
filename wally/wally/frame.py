import cv2
vidcap = cv2.VideoCapture('video_11.16.20.mov')
success,image = vidcap.read()
count = 0

while success:
  cv2.imwrite("aiframe%d.jpg" % count, image)     
  success,image = vidcap.read()
  print(' les frames sont la: ', success)
  count += 1