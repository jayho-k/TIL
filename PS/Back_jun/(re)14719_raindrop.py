'''

4 4
3 0 1 4

4 8
3 1 2 3 4 1 1 2

4 8
3 1 2 3 4 1 1 4


4 11
3 1 2 3 4 4 4 4 1 1 4


'''

# two pointer

def rain():
    pass



y,x = map(int,input().split())
lst = list(map(int,input().split()))

l,r = 0,len(lst)-1
lmax = rmax = 0
total = 0
while l<r:

    lmax = max(lmax, lst[l])
    rmax = max(rmax, lst[r])

    if lmax <= rmax:
        total += lmax-lst[l]
        l += 1

    else:
        total += rmax-lst[r]
        r -= 1

print(total)
    












# def rain(lst):

#     mx_i = 0
#     stnd = 0
#     total = lst[0]
#     # if lst[mx_i] == mx:
#     #     return mx_i, total

#     # else:

#     for i in range(1,len(lst)):
#         # if lst[i] == mx:
#         #     mx_i = i
#         #     return mx_i, total

#         if lst[stnd] > lst[i]:
#             total += lst[stnd]

#         elif lst[stnd] == lst[i]:
#             total += lst[stnd]
#             stnd = i

#         else:
#             stnd = i
#             total += lst[stnd]

#     return mx_i, total



# y,x = map(int,input().split())
# lst = list(map(int,input().split()))
# area = x*y

# mx = max(lst)

# mx_i,total1 = rain(lst)

# lst.reverse()
# r_mx_i, total2 = rain(lst)

# ans = total1+total2-sum(lst)-area


# if ans <=0:
#     print(0)
# else:
#     print(ans)
