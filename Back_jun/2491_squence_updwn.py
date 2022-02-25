'''


'''

n = int(input())
lst = list(map(int, input().split()))

c = [1]*n
d = [1]*n

for i in range(1,n):
    if lst[i-1] <= lst[i]:
        c[i] = c[i-1] + 1
    
    if lst[i-1] >= lst[i]:
        d[i] = d[i-1] + 1

print(c)
print(d)

# n = int(input())
# lst = list(map(int, input().split()))

# sv_h = lst[0]
# sv_l = lst[0]
# cnt_h = 0
# cnt_l = 0
# total = []

# for nx in range(1,n):
    
#     if sv_h >= lst[nx]:
#         cnt_h += 1
#         sv_h = lst[nx]
#         total.append(cnt_h)
    
#     else:
#         total.append(cnt_h)
#         cnt_h = 0
#         sv_h = lst[nx]

#     if sv_l <= lst[nx]:
#         cnt_l += 1
#         sv_l = lst[nx]
#         total.append(cnt_l)
    
#     else:
#         total.append(cnt_l)
#         cnt_l = 0
#         sv_l = lst[nx]

    

# if not total:
#     print(1)
# else:
#     print(max(total)+1)