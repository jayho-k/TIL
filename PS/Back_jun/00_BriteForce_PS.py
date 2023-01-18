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
'''
def dfs(d,v):
    global mx
    if d == depth:
        if mx < int(v) and int(v) <= n:
            mx = int(v)
        return

    for i in range(len(lst)):
        dfs(d+1,v+lst[i])
        dfs(d+1,v)

mx = 0
n,k = map(int,input().split())
depth = len(list(str(n)))
lst = list(map(str,input().split()))
dfs(0,'0')
print(mx)


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

