# fps test

resize + fps 줄이기

fps 30 ==> fps 10으로 만들때 어느 방법이 가장 빠른지 실험

3840 2160 => //6, //6 으로 진행

영상 길이 : 4분 57초

영상 총 frame 수 : 8952

영상 사이즈 : 3840 2160

#### 방법 1 : video.set(cv2.CAP_PROP_POS_MSEC,frame_time*1000)

- video.set(cv2.CAP_PROP_POS_MSEC,frame_time*1000) 사용

- CAP_PROP_POS_MSEC
  
  - 해당 시간에 동영상을 setting하는 방법
  
  - 즉 원하는 시간으로 이동을 하여 frame을 가져오는 방법을 사용하였다

1836.2730021476746 초 : 약 9분

이것은 저장할 때 쓰는 함수 가 아닌듯 하다

실시간 영상을 보낼때 다시 사용해 봐야된다

```python
prev_time = 0
start = time.time()
FPS = 5

video_path = "7-4_cam02_assault01_place04_day_summer.mp4"
vide_save_path = "modified.mp4"

video = cv2.VideoCapture(video_path)
width,height = int(video.get(3))//6,int(video.get(4))//6
frame_cnt = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
video_fps = int(video.get(cv2.CAP_PROP_FPS))
outputvideo = cv2.VideoWriter(vide_save_path,cv2.VideoWriter_fourcc
\(*'mp4v'), 10, (width,height))

sec = 0
frame_time = 0
frameRate = 10

i = 0
while True:
    video.set(cv2.CAP_PROP_POS_MSEC,frame_time*1000)
    frame_time += 1/frameRate
    hasFrames,frame = video.read()
    if not hasFrames:
        break

    resize_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    outputvideo.write(resize_frame)

    i+=1
    if not i%20:
        print(i)

video.release()
cv2.destroyAllWindows()
end = time.time()
print(end-start)
```

#### 방법 2 : 그냥 돌려서 저장하기 :

문제점 : 이렇게 저장하게 되면 fps10 단위로 저장을 하기 때문에 그냥 영상이 길어지고 느려지게 된다.

205.5035057067871

```python
# 방법2
i = 0
while True:
    hasFrame, frame = video.read()
    if not hasFrame:
        break
    i+=1
    resize_frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    outputvideo.write(resize_frame)
    if not i%20:
        print(i)

video.release()
cv2.destroyAllWindows()
end = time.time()
print(end-start)
```

#### 방법 3 : 필요한 프레임만 받는 방법

frame rate를 정해두고 모두 돌아가는 프레임에서 필요한 프레임만 받아 저장하게 된다.

157.6975679397583

가장 빠른 방법

- 영상을 저장하고 보낼 때 좋을듯 하다

문제점

- 정확한 시간에 frame을 받아오지 못한다 하지만 영상에는 크게 지장없어보인다.

```python
prev_time = 0
start = time.time()
FPS = 5

video_path = "7-4_cam02_assault01_place04_day_summer.mp4"
vide_save_path = "modified.mp4"

video = cv2.VideoCapture(video_path)
width,height = int(video.get(3))//6,int(video.get(4))//6
frame_cnt = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
video_fps = int(video.get(cv2.CAP_PROP_FPS))
outputvideo = cv2.VideoWriter(vide_save_path,cv2.VideoWriter_fourcc
\(*'mp4v'), 10, (width,height))

sec = 0
frame_time = 0
frameRate = 10

i=0
while True:
    hasFrame, frame = video.read()
    current_time = time.time() - prev_time

    if not hasFrame:
        break

    if current_time > 1./frameRate:
        i+=1
        prev_time = time.time()
        resize_frame = cv2.resize(frame, (width, height),\
        interpolation=cv2.INTER_AREA)
        outputvideo.write(resize_frame)
        if not i%20:
            print(i)

# 동영상 파일 또는 카메라를 닫고 메모리를 해제
video.release()

# 모든 창 닫기
cv2.destroyAllWindows()
end = time.time()
print(end-start)
```
