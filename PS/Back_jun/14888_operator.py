'''
+,-,*,/
확인
dfs에서 return의 의미
depth의 의미 : lst의 몇번째 까지 갔니?
for문을 dfs안에 써줄 필요가 없다 
=> d+1 => 이것이 for문과 같은 역할을 하게 된다.

'''


def operator(d,plus,minus,time,div,compare):
    global mx, mn

    if d==n:
        mx = max(mx,compare)
        mn = min(mn,compare)
        return
    
    if plus != 0:
        operator(d+1,plus-1,minus,time,div,compare+lst[d])

    if minus != 0:
        operator(d+1,plus,minus-1,time,div,compare-lst[d])

    if time != 0:
        operator(d+1,plus,minus,time-1,div,compare*lst[d])

    if div != 0:
        operator(d+1,plus,minus,time,div-1,int(compare/lst[d]))   

n = int(input())
lst = list(map(int,input().split()))
plus,minus,time,div = map(int,input().split())
mx = -1e9
mn = 1e9
operator(1,plus,minus,time,div,lst[0])
print(mx)
print(mn)




























# lst = []
# def dfs(d,p,m,t,div,v):

#     if d == n:
#         lst.append(v)
#         return

#     if p != 0:
#         dfs(d+1,p-1,m,t,div,v+n_lst[d])

#     if m != 0:
#         dfs(d+1,p,m-1,t,div,v-n_lst[d])

#     if t != 0:
#         dfs(d+1,p,m,t-1,div,v*n_lst[d])

#     if div != 0:
#         if v < 0:
#             dfs(d+1,p,m,t,div-1,-((-v)//n_lst[d]))
#         elif v>=0:
#             dfs(d+1,p,m,t,div-1,v//n_lst[d])



# n = int(input())
# n_lst = list(map(int, input().split()))
# oper = list(map(int, input().split()))
# p,m,t,div = oper
# v = n_lst[0]
# dfs(1,p,m,t,div,v)
# print(max(lst))
# print(min(lst))



