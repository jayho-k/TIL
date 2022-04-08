# '''

# '''
# # 1
# lst1 = [i for i in range(55,-1,-11)]
# print(lst1)

# # 2
# lst2 = list(set(['a','b','t','a','a','a','b','a','a']))
# lst2.sort()
# print(lst2)

# # 3
# # 재귀가 진짜 부족
# # 10 9 8 7 6 5 6 7 8 9 10 표현
# def r(n):

#     if n == 5:
#         return

#     print(n)
#     r(n-1)
#     print(n)

# r(10)

# # 4


from collections import deque

def bfs(y,x):
    q = deque([(y,x)])
    dy = [0,0,1,-1]
    dx = [1,-1,0,0]

    while q:
        
        y,x = q.popleft()

        for d in range(4):
            ny = y + dy[d]
            nx = x + dx[d]

            if 0<=ny<n and 0<=nx<n and visited[ny][nx] == 0:
                visited[ny][nx] = 1
                q.append((ny,nx))

n = int(input())
graph = [list(map(int,input().split()))]
visited = [[0]*n for _ in range(n)]