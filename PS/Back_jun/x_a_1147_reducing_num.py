'''
953 ==> 이런걸 줄어드는 수
n번째 줄어드는 수를 수하기

'''

def br(num):
    ans.append(int(num))
    for j in range(0,int(num[-1])):
        br(num+str(j))


n = int(input())
ans = []
for i in range(10):
    br(str(i))


if n>len(ans):
    print(-1)

else:
    ans.sort()
    print(ans[n-1])





# n = int(input())


# i = 0
# goal = 0
# while goal<n:
    
#     # string => int
#     st = list(str(i))
#     num = list(map(int,st))
#     if len(num) == 1:
#         goal += 1
#         i += 1 

#     else:
#         for j in range(len(num)-1,-1,-1):

#             cnt = 1
#             if num[j-1] > num[j]:
#                 cnt += 1
#                 if cnt == len(num):
#                     goal += 1
#                 i += 1

#             else:
#                 # 자리수
#                 lo = len(num) - j -1
#                 i += (10**(lo)) - (10**(lo-1)*num[j])

#                 # i += (10**(lo)*9)
#                 goal += 1

#                 break 
#     print(i)
#     if goal>=n:
#         break

    
# print(i-1)

