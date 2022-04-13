'''
5
2
1 2
2 4

얘네 합이 0이 될때 cnt 를 세주면 되는건가??
0  0  0  0  0
1 -1 
   1    -1
'''

n = int(input())
b = int(input())
room = [0]*n
for _ in range(b):
    x,y = map(int,input().split())
    room[x-1] += 1
    room[y-1] -= 1

total = 0
cnt = 0
for i in room:
    total += i
    if total == 0:
        cnt += 1

print(cnt)