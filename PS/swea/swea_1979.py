'''
2
5 3
0 0 1 1 1
1 1 1 1 0
0 0 1 0 0
0 1 1 1 1
1 1 1 0 1
5 3
1 0 0 1 0
1 1 0 1 1
1 0 1 1 1
0 1 1 0 1
0 1 1 1 0

'''
# for tc in range(1,int(input())+1):
#     n,k = map(int,input().split())
#     grid_h = [list(map(str,input().split()))for _ in range(n)]
#     grid_w = list(map(list,zip(*grid_h)))
#     ans = 0
#     for i in range(n):
#         ans+=''.join(grid_h[i]).split('0').count('1'*k)
#         ans+=''.join(grid_w[i]).split('0').count('1'*k)
#     print(f"#{tc} {ans}")





for tc in range(1,int(input())+1):
    
    n,k = map(int,input().split())
    grid = [list(map(str,input().split()))for _ in range(n)]
    ans = 0
    for y in range(n):
        cnt_w = 0
        cnt_h = 0
        for x in range(n):

            if grid[y][x]=='1':
                cnt_w +=1
            else:
                if cnt_w == 3:
                    ans+=1
                cnt_w=0

            if grid[x][y]=='1':
                cnt_h+=1
            else:
                if cnt_h == 3:
                    ans+=1
                cnt_h=0
        
        else:
            if cnt_w==3:
                ans+=1

            if cnt_h==3:
                ans+=1
    print(f"#{tc} {ans}")