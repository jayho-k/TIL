'''
657 3
1 5 7

778 3
1 5 7

123 3
7 8 9

100000000 1
1
'''

# 18511번_큰 수 구성하기(3번 틀림)
'''
배운점
- visited를 따로 생성하는 것보다
        dfs(d+1,v+lst[i])
        dfs(d+1,v)
    이렇게 사용하는 것이 메모리를 더 아낄 수 있다.

- 원본은 최대한 건들이는 것이 아니다.
- 재귀에서 초기값을 설정할 때 함수에 넣어주는 것이 좋다
    - dfs(0,'0')
    - ['0'] + list(map(str,input().split())) 이렇게 하다가 틀림발생
- 부등호를 잘 보자 =, 

ANT
4
35000 COMPUTERARCHITECTURE
47000 ALGORITHM
43000 NETWORK
40000 OPERATINGSYSTEM

AAA
3
10000 BCD
20000 AAC
50000 DDD

정답 : -1

결과 : 20000

6
0 1 2 3 4 5
1 0 2 3 4 5
1 2 0 3 4 5
1 2 3 0 4 5
1 2 3 4 0 5
1 2 3 4 5 0

A
BABA

'''
#12919_A와B2
def dfs(word,t):
    global ans

    if t == word:
        ans = 1
        return

    if len(t)==len(word):
        return

    for d in range(2):
        if d==0:
            nw_word = addA(word)
            if nw_word not in visited:
                visited.add(nw_word)
                dfs(nw_word,t)
        else:
            nw_word = addB(word)
            if nw_word not in visited:
                visited.add(nw_word)
                dfs(nw_word,t)

def addA(word):
    word+='A'
    return word

def addB(word):
    tmp = ''
    for w in word:
        tmp = w+tmp
    tmp = 'B'+tmp
    return tmp

visited = set()
ans = 0
s = input()
t = input()
dfs(s,t)
print(ans)

# #15661_링크와 스타트
# from itertools import permutations
# import sys
# input = sys.stdin.readline

# def div_team(visited):
#     team1 = []
#     team2 = []
#     for i in range(len(visited)):
#         if visited[i]==0:
#             team1.append(i)
#         else:
#             team2.append(i)
#     return team1,team2

# def cal_pwr(team):
#     pwr_t = 0
#     for y1,x1 in permutations(team,2):
#         pwr_t+=grid[y1][x1]
#     return pwr_t

# def dfs(d,idx,end):
#     global mn

#     if d==end:
#         # print(visited)
#         team1,team2 = div_team(visited)
#         pwr_t1=cal_pwr(team1)
#         pwr_t2=cal_pwr(team2)
#         mn=min(mn,abs(pwr_t1-pwr_t2))
#         return

#     for i in range(idx,n):
#         if visited[i]==0:
#             visited[i]=1
#             dfs(d+1,i,end)
#             visited[i]=0

# mn = 1e9
# n = int(input())
# visited = [0]*n
# grid = [list(map(int,input().split())) for _ in range(n)]
# for i in range(1,n//2+1):
#     dfs(0,0,i)

# print(mn)




# # 2615_오목
# from pprint import pprint
# import sys
# input = sys.stdin.readline

# def play():
#     res_lst = []
#     for y in range(19):
#         for x in range(19):
#             if board[y][x]!=0:
#                 blwh,lo = isOmak(y,x,board[y][x])
#                 if blwh:
#                     res_lst.append((blwh,lo))
#     return res_lst


# def isOmak(sy,sx,blwh):

#     y1,x1 = sy,sx
#     y2,x2 = sy,sx
    
#     for d in range(4):
#         cnt = 1
#         while 1:
#             ny1 = y1+dy[d]
#             nx1 = x1+dx[d]
#             if ny1<0 or ny1>=19 or nx1<0 or nx1>=19 \
#                 or board[ny1][nx1]==0 or board[ny1][nx1]!=blwh:
#                 break
#             cnt+=1
#             y1 = ny1
#             x1 = nx1
        
#         while 1:
#             ny2 = y2+dy[d+4]
#             nx2 = x2+dx[d+4]
#             # 0이거나, 다른색이거나, visited
#             # 방문한적이 없거나, 방문한곳이 같은 색이라면 들어가도 된다.
#             # 방문한적이 있고,방문한곳이 다른색이라면 안된

#             if ny2<0 or ny2>=19 or nx2<0 or nx2>=19 \
#                 or board[ny2][nx2]==0 or board[ny2][nx2]!=blwh:
#                 break
#             cnt+=1
#             y2 = ny2
#             x2 = nx2

#         if cnt==5:
#             return blwh,(sy+1,sx+1)

#         y1,x1 = sy,sx
#         y2,x2 = sy,sx

#     return None,None

# dy = [-1,-1,-1,0,1,1,1,0]
# dx = [-1,0,1,1,1,0,-1,-1]

# board = [list(map(int,input().split())) for _ in range(19)]
# res_lst = play()
# bl_cnt = 0
# wh_cnt = 0
# for res in res_lst:
#     res_blwh,location = res
#     if res_blwh==1:
#         bl_cnt+=1

#     elif res_blwh==2:
#         wh_cnt+=1
# res_lst.sort(key=lambda x: (x[1][1],x[1][0]))
# # print(res_lst)

# # if ((not bl_cnt and wh_cnt) or (bl_cnt and not wh_cnt)) and \
# #     (bl_cnt <=5 or bl_cnt<=5):
# #     print(res_lst[0][0])
# #     print(res_lst[0][1][0],res_lst[0][1][1])
# # else:
# #     print(0)


# # 동시에 이기는 경우
# if bl_cnt and wh_cnt:
#     print(0)

# elif not bl_cnt and not wh_cnt:
#     print(0)

# # 오목이 2개 이상인 경우
# elif bl_cnt>5 or wh_cnt>5:
#     print(0)

# # 나머지
# else:
#     print(res_lst[0][0])
#     print(res_lst[0][1][0],res_lst[0][1][1])



# if blwh==0:
#     print(blwh)
# else:
#     print(blwh)
#     print(lo[0],lo[1])



# # 9079_동전게임
# # from pprint import pprint
# import sys
# from collections import deque

# def bfs(st):
#     q = deque([(st,0)])
#     visited[st]=1

#     while q:
#         num,cnt = q.popleft()
#         # print(num)
#         if num==0 or num==511:
#             return cnt

#         cur_board = num2board(num)

#         for d in range(8):
#             if 0<=d<3:
#                 new_board = change_w(cur_board,d)

#             elif 3<=d<6:
#                 new_board = change_h(cur_board,d%3)
                
#             elif 6<=d<8:
#                 new_board = cross(cur_board,d%2)

#             new_num = board2num(new_board)
#             if visited[new_num] == 0:
#                 visited[new_num] = 1
#                 q.append((new_num,cnt+1))

#     return -1


# def change_w(board,y):
#     n_board = [row[:] for row in board]
#     for x in range(3):
#         if n_board[y][x]=='0':
#             n_board[y][x]='1'
#         else:
#             n_board[y][x]='0'
#     return n_board

# def change_h(board,x):
#     n_board = [row[:] for row in board]
#     for y in range(3):
#         if n_board[y][x]=='0':
#             n_board[y][x]='1'
#         else:
#             n_board[y][x]='0'
#     return n_board

# def cross(board,lo):
#     n_board = [row[:] for row in board]
#     if lo==0:
#         for i in range(3):
#             if n_board[i][i]=='0':
#                 n_board[i][i]='1'
#             else:
#                 n_board[i][i]='0'

#     elif lo==1:
#         for i in range(3):
#             if n_board[i][-i-1]=='0':
#                 n_board[i][-i-1]='1'
#             else:
#                 n_board[i][-i-1]='0'

#     return n_board

# def set_board(board):
#     n_board = [['0']*3 for _ in range(3)]
#     for y in range(3):
#         for x in range(3):
#             if board[y][x] == 'T':
#                 n_board[y][x] = '1'
#     return n_board

# def num2board(num):
#     # 정수 => 2진수 => board
#     bi_num = str(bin(num))[2:]
#     if len(bi_num)<9:
#         bi_num=('0'*(9-len(bi_num)))+bi_num
#     bi_lst = list(bi_num)
#     n_board = []
#     for i in range(0,9,3):
#         n_board.append(bi_lst[i:i+3])
#     return n_board

# def board2num(board):
#     tmp = '0b'
#     for y in range(3):
#         for x in range(3):
#             tmp+=board[y][x]
#     return int(tmp,2)

# T = int(input())
# for _ in range(T):
#     mn = 1e9
#     visited = [0]*513
#     board = [list(input().split()) for _ in range(3)]
#     num_baord = set_board(board)
#     st = board2num(num_baord)
#     cnt = bfs(st)
#     print(cnt)





# def play(board,v):
#     global mn
#     if check(board):
#         mn = min(mn,v)
#         return
    
#     for j in range(3):
#         if visited[j]==0:
#             visited[j]=1
#             if j!=3:
#                 play(cross(board,j),v+1)
#             play(change_w(board,j),v+1)
#             play(change_h(board,j),v+1)
#             visited[j]=0



# # 16508_전공책
# # 부분 집합=> 값을 얻어내는 것을 먼저
# from itertools import combinations

# def count_same(com_lst,target):

#     vis_t = [0]*len(target)
#     total = 0
#     for book in com_lst:
#         cost,name = book
#         flag = False
#         for na in name:
#             for t in range(len(target)):
#                 # 같고 이미 지나 왔을 경우
#                 if na == target[t] and vis_t[t]==0:
#                     vis_t[t] = 1
#                     flag = True
#                     break
#         if flag:
#             total+=cost
#         else:
#             break
#     return total, vis_t.count(1)


# target = input()
# n = int(input())
# books_info = []
# for _ in range(n):
#     c,na = input().split()
#     books_info.append([int(c),na])

# mn = 1e9
# for i in range(1,n+1):
#     for com_lst in list(map(list,combinations(books_info,i))):
#         total, vis_t_cnt = count_same(com_lst,target)
#         if vis_t_cnt==len(target):
#             mn = min(mn,total)

# if mn==1e9:
#     print(-1)
# else:
#     print(mn)





# # 16937_두 스티커
# from itertools import combinations
# y,x = map(int,input().split())
# n = int(input())
# lst = [tuple(map(int,input().split())) for _ in range(n)]
# com_lst = list(combinations(lst,2))
# mx = 0
# for i in range(len(com_lst)):
#     stk1,stk2 = com_lst[i]
#     y1,x1 = stk1
#     y2,x2 = stk2
#     if ((y1+y2<=y and max(x1,x2)<=x) or (max(y1,y2)<=y and x1+x2<=x)) or \
#         ((y1+x2<=y and max(x1,y2)<=x) or (max(y1,x2)<=y and x1+y2<=x)) or \
#         ((x1+y2<=y and max(y1,x2)<=x) or (max(x1,y2)<=y and y1+x2<=x)) or \
#         ((x1+x2<=y and max(y1,y2)<=x) or (max(x1,x2)<=y and y1+y2<=x)):
#         mx = max(mx, (y1*x1)+(y2*x2))
# print(mx)


# # 14501_퇴사

# n = int(input())
# sch = [tuple(map(int,input().split())) for _ in range(n)]
# dp = [0]*(n+1)

# for day in range(n-1,-1,-1):
#     du,pay = sch[day]
#     if n<day+du:
#         dp[day] = dp[day+1]
#     else:
#         dp[day] = max(dp[day+du]+pay,dp[day+1])

# print(max(dp))




# # 16439 치킨치킨치킨
# from itertools import combinations
# def dfs(d,v_lst):
#     global remx
#     if d==3:
#         total = 0
#         for y in range(n):
#             mx = 0
#             for v in v_lst:
#                 if mx<pref[y][v]:
#                     mx=pref[y][v]
#             total+=mx
#         remx = max(total,remx)
#         return

#     for i in range(m):
#         if i not in v_lst:
#             dfs(d+1,v_lst+[i])


# n,m = map(int,input().split())
# lst = list(range(m))
# # com_lst = list(combinations(lst,3))
# pref = [list(map(int,input().split())) for _ in range(n)]
# remx = 0
# dfs(0,[])
# print(remx)

# mx_pref = 0
# for com in com_lst:
#     total = 0
#     for y in range(n):
#         mx = 0
#         for c in com:
#             if pref[y][c] > mx:
#                 mx = pref[y][c]
#         total+=mx

#     if mx_pref < total:
#         mx_pref=total
# print(mx_pref)



# def dfs(d,v):
#     global mx
#     if d == depth:
#         if mx < int(v) and int(v) <= n:
#             mx = int(v)
#         return

#     for i in range(len(lst)):
#         dfs(d+1,v+lst[i])
#         dfs(d+1,v)

# mx = 0
# n,k = map(int,input().split())
# depth = len(list(str(n)))
# lst = list(map(str,input().split()))
# dfs(0,'0')
# print(mx)


# # 15721_번데기
# n = int(input())
# t = int(input())
# bdg = input()

# lo = 0
# cnt = 0
# round = 0
# bdg_board = ''
# flag = False
# while 1:
#     round+=1
#     bdg_board = '0101'
#     bdg_board+= '0'*(round+1)+'1'*(round+1)

#     for b in bdg_board:
#         if b == bdg:
#             cnt += 1
#         if cnt == t:
#             flag = True
#             break
#         lo = (lo+1)%n

#     if flag:
#         break

# print(lo)


# total_round = [0]
# for i in range(1,n+1):
#     total_round.append(((total_round[-1]*2)+(4+((i+1)*2)))//2)

# round = 0
# for j in range(1,n+1):
#     if total_round[j]>=t:
#         round = j
#         break

# # print(total_round)
# # print('round', round)
# bdg_rule = '0101'
# bdg_rule+=('0'*(round+1))
# bdg_rule+=('1'*(round+1))
# # print(bdg_rule)


# cnt = total_round[round-1]
# ans = 0
# for k in range(len(bdg_rule)):
#     if bdg_rule[k]==bdg:
#         cnt+=1
#     if cnt==t:
#         break

# print((total_round[round-1]*2+k)%n)


# a = 0
# n,k = map(int,input().split())

# if k ==0:
#     for h in range(n+1):
#         for m in range(60):
#             for s in range(60):
#                 if k in (map(int,list(str(h))) if h>=10 else map(int,['0',str(h)])) or \
#                     k in (map(int,list(str(m))) if m>=10 else map(int,['0',str(m)])) or \
#                     k in (map(int,list(str(s))) if s>=10 else map(int,['0',str(s)])):
#                     a+=1

# else:
#     for m in range(n+1):
#         for i in range(60):
#             for j in range(60):
#                 if k in map(int,list(str(i))) or k in map(int,list(str(j))) or  k in map(int,list(str(m))):
#                     a+=1

# print(a)


# # 19532 수학은 비대면강의입니다
# def cal(a,b,c,d,e,f):
#     for y in range(-999,1000):
#         for x in range(-999,1000):
#             if (a*x)+(b*y)==c and (d*x)+(e*y)==f:
#                 return x,y

# a,b,c,d,e,f = map(int,input().split())
# print(*cal(a,b,c,d,e,f))



# # 22864 피로도
# def cal(a,b,c,m):
#     ans = 0
#     tired = 0
#     for _ in range(1,25):
#         if tired+a <= m:
#             ans+=b
#             tired+=a
#         else:
#             tired-=c
#             if tired < 0:
#                 tired = 0
#     return ans

# a,b,c,m = map(int,input().split())
# if a>m:
#     print(0)
# else:
#     print(cal(a,b,c,m))


# # 2231 분해합
# def cal(num):
#     total = num
#     for s in str(num):
#         total += int(s)
#     return total

# n = int(input())
# ans = 0
# for i in range(1,n):
#     t = cal(i)
#     if t==n:
#         ans=i
#         break

# print(ans)


# # 2798 블랙잭
# def recur(d,v,cards,visited):
#     global mx
#     if v>m:
#         return

#     if d == 3:
#         mx = max(mx,v)
#         return

#     for i in range(len(cards)):
#         if visited[i]==0:
#             visited[i]=1
#             recur(d+1,v+cards[i],cards,visited)
#             visited[i]=0

# mx = 0
# n,m = map(int,input().split())
# cards = list(map(int,input().split()))
# visited = [0]*n
# recur(0,0,cards,visited)
# print(mx)

