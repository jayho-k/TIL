'''

3
2 16
4 6
6 10




'''
n = int(input())
lst = []
for _ in range(n):
    s,l = map(int,input().split())
    lst.append([s,1])
    lst.append([l,-1])
    # mx = max(mx,l)

lst.sort(key=lambda x : (x[0], -x[1]))

n_lst = [lst[0]]

for i in range(1,n*2):
    if n_lst[-1][0] == lst[i][0]:
        n_lst[-1][1] += lst[i][1]
        continue

    n_lst.append(lst[i])

# print(n_lst)


total = 0
total_mx = 0
sm_d = 0
lg_d = 1e9
for j in range(len(n_lst)-1):

    total += n_lst[j][1]

    if total_mx < total:
        sm_d = n_lst[j][0]
        total_mx = total

    # if total_mx + lst[j][1] == total_mx-1:
    #     lg_d = lst[j][0]

    if total_mx == total:
        lg_d = n_lst[j+1][0]

print(n_lst)
print(total_mx)
print(sm_d, lg_d)








# n = int(input())
# lst = []
# input_mx = 0
# input_mn = 1e9


# for _ in range(n):
#     s,l = map(int,input().split())
#     input_mn = min(s,input_mn)
#     input_mx = max(l,input_mx)
#     lst.append([s,l])


# dp = [0]*(input_mx-input_mn+1)


# for i in range(n):
#     sm, lg = lst[i]
#     dp[sm-input_mn] += 1
#     dp[lg-input_mn] -= 1

# total = 0
# total_mx = 0
# sm_d = 0
# lg_d = 1e9
# for d in range(len(dp)):

#     total += dp[d]

#     if total_mx < total:
#         sm_d = d
#         total_mx = total

#     elif total_mx == total:
#         lg_d = d



# print(total_mx)
# print(sm_d+input_mn, lg_d+1+input_mn)



