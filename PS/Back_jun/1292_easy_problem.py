
'''
3 7
'''

n1, n2 = map(int,input().split())

lst = [0]

for i in range(50):
    for _ in range(i):
        lst.append(i)

ans = lst[n1:n2+1]
print(ans)
print(sum(ans))













# '''
# 3 7
# '''
# mn, mx = map(int,input().split())

# bigger = 0
# smaller_lst = [1e9]
# s = 0
# b = 0
# sm = 0
# bg = 0
# for i in range(1,1001):
#     bigger += i
#     smaller = smaller_lst[-1]
    
#     if smaller < mn <= bigger:
#         s = i
#         dif1 = bigger-mn + 1
#         sm = s*dif1

#     if smaller < mx <= bigger:
#         b = i
#         dif2 = mx - smaller
#         bg = b*dif2

#     smaller_lst.append(bigger)

# total = 0
# for t in range(s+1,b):
#     total += t**2

# # print(sm)
# # print(bg)

# if 

# ans = sm + bg + total
# print(ans)