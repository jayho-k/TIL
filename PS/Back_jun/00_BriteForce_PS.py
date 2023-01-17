'''


5 3 2 10
'''
a = 0
n,k = map(int,input().split())

if k ==0:
    for h in range(n+1):
        for m in range(60):
            for s in range(60):
                if k in (map(int,list(str(h))) if h>=10 else map(int,['0',str(h)])) or \
                    k in (map(int,list(str(m))) if m>=10 else map(int,['0',str(m)])) or \
                    k in (map(int,list(str(s))) if s>=10 else map(int,['0',str(s)])):
                    a+=1

else:
    for m in range(n+1):
        for i in range(60):
            for j in range(60):
                if k in map(int,list(str(i))) or k in map(int,list(str(j))) or  k in map(int,list(str(m))):
                    a+=1

print(a)


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

