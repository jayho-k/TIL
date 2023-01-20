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
'''

# 9079_동전게임
from pprint import pprint
import sys
sys.setrecursionlimit(10**9)


T = int(input())
def play(board,v):
    global mn
    if check(board):
        mn = min(mn,v)
        return
    
    for j in range(3):
        if visited[j]==0:
            visited[j]=1
            if j!=3:
                play(cross(board,j),v+1)
            play(change_w(board,j),v+1)
            play(change_h(board,j),v+1)
            visited[j]=0

def check(board):
    cnt = 0
    for y in range(3):
        for x in range(3):
            if board[y][x]=='H':
                cnt+=1
    
    if cnt==9 or cnt==0:
        print(board)
        return True
    else:
        return False

def change_w(board,y):
    n_board = [row[:] for row in board]
    for x in range(3):
        if n_board[y][x]=='H':
            n_board[y][x]='T'
        else:
            n_board[y][x]='H'
    return n_board

def change_h(board,x):
    n_board = [row[:] for row in board]
    for y in range(3):
        if n_board[y][x]=='H':
            n_board[y][x]='T'
        else:
            n_board[y][x]='H'
    return n_board

def cross(board,lo):
    n_board = [row[:] for row in board]
    if lo==0:
        for i in range(3):
            if n_board[i][i]=='H':
                n_board[i][i]='T'
            else:
                n_board[i][i]='H'

    elif lo==1:
        for i in range(3):
            if n_board[i][-i-1]=='H':
                n_board[i][-i-1]='T'
            else:
                n_board[i][-i-1]='H'

    return n_board

for _ in range(T):
    mn = 1e9
    visited = [0]*3
    board = [list(input().split()) for _ in range(3)]
    play(board,0)
    print(mn)








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

