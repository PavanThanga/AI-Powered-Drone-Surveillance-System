import cv2

fourcc = cv2.VideoWriter_fourcc(*"avc1")
out = cv2.VideoWriter("verify.mp4", fourcc, 25, (640, 480))

print("VideoWriter opened:", out.isOpened())

out.release()
