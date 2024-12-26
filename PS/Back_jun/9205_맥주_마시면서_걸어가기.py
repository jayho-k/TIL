"""
2
2
0 0
1000 0
1000 1000
2000 1000
2
0 0
1000 0
2000 1000
2000 2000
"""
from collections import deque

def bfs(start, reach, convStoreSet):

    q = deque()
    q.append(start)
    visited = set()
    visited.add(start)

    while q:
        x,y = q.popleft()

        # 편의 점을 들리기 전 reach 까지 갈 수 있는지 확인
        if abs(x - reach[0]) + abs(y - reach[1]) <= 1000:
            return "happy"
        
        # 갈 수 있는 편의점이 있는지 확인
        for (convX,convY) in convStoreSet:
            # 갈 수 없는 편의점 : 이미 갔던 곳, 거리가 1000보다 큰 곳
            if (convX,convY) in visited or abs(convX - x) + abs(convY - y) > 1000:
                continue
            
            # 나머지는 방문
            q.append((convX,convY))
            visited.add((convX,convY))
            
    return "sad"    

def mainPlay():
    
    n = int(input())
    start = tuple(map(int,input().split()))
    convStoreSet = set(tuple(map(int,input().split())) for _ in range(n))
    reach = tuple(map(int,input().split()))

    print(bfs(start, reach ,convStoreSet))

    
tc = int(input())
for _ in range(tc):
    mainPlay()




        # for d in range(4):
        #     ny = y + dy[d]
        #     nx = x + dx[d]

        #     if -32768 <=ny and ny <= 32767 and -32768 <= nx and nx <= 32767 and \
        #         (nx,ny) not in visited and (nx,ny)in convStoreSet:
                


        # 계산
        

        


