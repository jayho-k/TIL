'''

알파벳을 빼가면서 정답맞추기

'''
import sys

def dfs(tt):
    global ans
    tn = len(tt)
    if tn == sn:
        if s == tt:
            ans = 1
            return
        return

    if tt[-1] == "A":
        dfs(tt[:-1])

    if tt[0] == "B":
        tmp = tt[::-1]
        dfs(tmp[:-1])


s = sys.stdin.readline().rstrip()
t = sys.stdin.readline().rstrip()
sn = len(s)
ans = 0
dfs(t)
print(ans)



'''

알파벳을 더해가면서 정답맞추기

'''

# def first(st):
#     st = st[:-1]
#     return st

# def second(st):
#     st = st[1:]
#     return st[::-1]

# def dfs(d,c):
#     global ans

#     if d == c:
#         cs = s[:]
#         for o in tmp[:]:
#             if o==0:
#                 cs = first(cs)
#             else:
#                 cs = second(cs)

#         if cs == t:
#             ans = 1
#             return
#         else:
#             return

#     tmp[d] = 1
#     dfs(d+1,c)
#     tmp[d] = 0
#     dfs(d+1,c)

# import sys

# s = sys.stdin.readline().rstrip()
# t = sys.stdin.readline().rstrip()
# sn = len(s)
# tn = len(t)

# c = tn - sn

# tmp = [0]*c
# orders = []
# ans = 0
# dfs(0,c)

# print(ans)



'''
permutation
'''
# from itertools import permutations

# def first(st):
#     st += "A"
#     return st

# def second(st):
#     st += "B"
#     return st[::-1]

# import sys

# s = sys.stdin.readline().rstrip()
# t = sys.stdin.readline().rstrip()
# sn = len(s)
# tn = len(t)

# c = tn - sn

# tmp = [0,1]*c
# tmp = list(permutations(tmp,c))
# tmp = list(set(tmp))
# orders = list(map(list, tmp))


# for order in orders:
#     cs = s[:]
#     for o in order:
#         if o==0:
#             cs = first(cs)
#         else:
#             cs = second(cs)

#     if cs == t:
#         ans = 1
#         break
# else:
#     ans = 0

# print(ans)