'''

4 2 1
1 1 5 2 2
1 4 7 1 6
'''

n,m,k = map(int, input().split())
grid = [[0]*n for _ in range(n)]

dy = [-1,-1,0,1,1,1,0,-1]
dx = [0,1,1,1,0,-1,-1,-1]

# y,x,m,s,d
magic = [list(map(int,input().split())) for _ in range(m)]

chck = []

for _ in range(k):
    for y,x,m,s,d in magic:

        ny = y + dy[d]*s
        nx = x + dx[d]*s

        if 0<=ny<n and 0<=nx<n:
            chck.append([ny,nx,m,s,d])

    chck.sort()
    # 같은지 안같은지 확인

    i = 1
    while i <len(chck):
        jy,jx,jm,js,jd = chck[i]
        py,px,pm,ps,pd = chck[i-1]

        if py == jy and px == jx:
            chck[i][2] += chck[i-1][2]
            chck[i][3] += chck[i-1][3]
            
            chck[i].append(pd)
            chck.pop(i-1)
        else:
            i += 1

    chch = []
    for c in chck:
        yc,xc = c[0], c[1]
        mc = c[2]
        sc = c[3]
        dc = c[4:]
        if len(dc) >= 2:
            chm = int(mc/5)
            chs = int(sc/len(dc))
            
            cnt = 0
            for i in dc:
                t = i%2
                if t == 0:
                    cnt += 1

            # 모두 홀수이거나 짝수
            if cnt == len(dc) or cnt == 0:
                for d in (0,2,4,6):
                    nyc = yc + dy[d]*chs
                    nxc = xc + dx[d]*chs

                    chck.append([nyc,nxc,chm,chs,d])
                    
            else:
                for d in (1,3,5,7):
                    nyc = yc + dy[d]*chs
                    nxc = xc + dx[d]*chs

                    chck.append([nyc,nxc,chm,chs,d])


print(chck)






