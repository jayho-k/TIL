'''
4
2 3 1
5 2 4 1
그 당시 항상 최선의 방법을 생각한다. = 그리디
방법1 그리디
방법2 bfs

큰것부터


'''

n = int(input())
dist = list(map(int,input().split()))
station = list(map(int,input().split()))
dist_cnt = len(dist)
station_sort = sorted(station[:-1])

accu = 0
last = dist_cnt
for i in range(len(station)-1):
    s2l = station_sort[i]
    lo_s2l = station.index(s2l)
    for j in range(lo_s2l,last):
        if dist[j]==0:
            break
        accu += s2l*dist[j]
        dist[j]=0
print(accu)
# print('ans : ', accu)