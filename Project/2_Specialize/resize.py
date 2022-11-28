import numpy
import cv2
import time
prev_time = 0
start = time.time()
video_path = "7-4_cam02_assault01_place04_day_summer.mp4"
vide_save_path = "modified3.mp4"

video = cv2.VideoCapture(video_path)
out_video = cv2.VideoCapture(vide_save_path)
width,height = int(video.get(3))//6,int(video.get(4))//6
frame_cnt = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

outputvideo = cv2.VideoWriter(vide_save_path,cv2.VideoWriter_fourcc(*'mp4v'), 10, (width,height))
frameRate = 10

# resize만 시키기
while True:
    hasFrame, frame = video.read()
    if not hasFrame:
        break

    resize_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    outputvideo.write(resize_frame)


video.release()
cv2.destroyAllWindows()
end = time.time()
print(end-start)


# # 방법 1
# sec = 0
# frame_time = 0

# i = 0
# while True:
#     video.set(cv2.CAP_PROP_POS_MSEC,frame_time*1000)
#     frame_time += 1/frameRate
#     hasFrames,frame = video.read()
#     if not hasFrames:
#         break
#     resize_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
#     outputvideo.write(resize_frame)
#     i+=1
#     if not i%20:
#         print(i)

# video.release()
# cv2.destroyAllWindows()
# end = time.time()
# print(end-start)



# # 방법2
# i = 0
# while True:
#     hasFrame, frame = video.read()
#     if not hasFrame:
#         break
#     i+=1
#     resize_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
#     outputvideo.write(resize_frame)
#     if not i%20:
#         print(i)

# video.release()
# cv2.destroyAllWindows()
# end = time.time()
# print(end-start)





# 필요한 프레임만 받는 방법
i=0
while True:
    hasFrame, frame = video.read()
    current_time = time.time() - prev_time

    if not hasFrame:
        break
    
    if current_time > 1./frameRate:
        i+=1
        prev_time = time.time()
        resize_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        outputvideo.write(resize_frame)
        if not i%20:
            print(i)

# 동영상 파일 또는 카메라를 닫고 메모리를 해제
video.release()

# 모든 창 닫기
cv2.destroyAllWindows()
end = time.time()
print(end-start)
