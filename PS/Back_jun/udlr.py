'''
가장 왼쪽 위 (1,1)
가장 오른쪽 아래 (n,n)

LRUD

'''
n = int(input())
x, y = 1,1 
mv = list(input().split())

dx = [0,0,-1,1]
dy = [-1,1,0,0]
btn = ['L','R','U','D']

for m in mv:
    for i in range(len(btn)):
        if m == btn[i]:
            nx = x + dx[i]
            ny = y + dy[i]
    if nx < 1 or ny< 1 or nx > n or ny >n:
        continue

    x, y = nx, ny

print(x,y)

