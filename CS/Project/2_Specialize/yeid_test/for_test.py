'''



'''
import time
import threading
tmp = []
def infinite():
    i = 0
    while 1:
        i+=1
        tmp.append(i)
        time.sleep(1)
st = threading.Thread(
    target=infinite, args=()
)
st.start()
time.sleep(1)
for i in tmp:
    print(i)
    print(tmp)
    time.sleep(1)