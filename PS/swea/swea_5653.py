'''



1
9 10 37                
0 0 0 0 0 0 0 0 3 0
0 0 0 0 0 0 0 0 5 3
0 0 2 0 0 0 0 4 0 0
3 0 0 0 0 0 4 0 0 0
0 0 0 0 0 3 5 0 0 2
0 0 0 0 0 0 0 0 0 5
0 0 0 0 0 0 0 0 2 3
0 0 0 0 0 0 0 0 0 0
0 0 2 2 0 0 0 0 0 0

1
2 2 10
1 1
0 2

1
5 5 19
3 2 0 3 0
0 3 0 0 0
0 0 0 0 0
0 0 1 0 0
0 0 0 0 2
'''
from collections import deque
def find_inact():
    inact = deque()
    for y in range(n):
        for x in range(m):
            if grid[y][x]:
                inact.append((grid[y][x],y,x,1))
                visited.add((y,x))
    return inact

for tc in range(1,int(input())+1):

    n,m,k = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]

    visited = set()

    breed = []
    act = deque()
    inact = find_inact()
    dy = [-1,0,1,0]
    dx = [0,1,0,-1]
    
    for t in range(1,k+1):

        if act:
            for _ in range(len(act)):
                a_life,ay,ax,cnt,timer = act.popleft()
                if cnt==0:
                    cnt+=1
                    # 이미 한시간이 지난 상태라고 볼 수 있다.
                    # 왜냐하면 다음 사이클에 act가 움직이기 때문
                    # 따라서 1시간 뒤에 번식을 한다는 뜻 
                    # => 바로 breed를 해야한다는 뜻
                    # 즉 breed가 act보다 밑에 있어야한다는 뜻이다
                    breed.append((a_life,ay,ax))
                    

                if timer%a_life==0:
                    continue
                else:
                    # 처음 온애는 breed로 보냄
                    # act상태로 다시 보냄
                    act.append((a_life,ay,ax,cnt,timer+1))
        
        if inact:
            for _ in range(len(inact)):
                ia_life,iay,iax,timer = inact.popleft()
                if timer%ia_life==0:

                    # 한시간이 뒤에 => 다음 cycle에 진행한다는 뜻
                    # act가 위에 있어야 한다는 뜻이다
                    act.append((ia_life,iay,iax,0,1))
                else:
                    inact.append((ia_life,iay,iax,timer+1))

        if breed:
            breed.sort(reverse=True)
            for b in range(len(breed)):
                b_life,by,bx = breed[b]
                for d in range(4):
                    ny = by+dy[d]
                    nx = bx+dx[d]
                    if (ny,nx) not in visited:
                        visited.add((ny,nx))

                        # 번식을 하고 바로 timer가 움직이지 않는다
                        # inact.append를 한다는 것 
                        # => 번식을 완료하고 inact상태로 바뀌었다는 뜻
                        # 즉 다음 cycle부터 계산을 하면 된다.
                        inact.append((b_life,ny,nx,1))
            breed=[]

    
        # print("cycle", t)
        # print("act     : ",act)
        # print("inact   : ",inact)
        # print("visited : ",visited)
        # print()
    
    ans = len(act)+len(inact)
    print(f"#{tc} {ans}")



        

