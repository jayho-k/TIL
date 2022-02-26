'''
우선순위 세기

'''

# r = int(input())

# for _ in range(r):
#     al = list(map(int, input().split()))
#     bl = list(map(int, input().split()))
#     mn_cnt = min(al[0], bl[0])

#     alst = sorted(al[1:], reverse=True)
#     blst = sorted(bl[1:], reverse=True)

#     for i in range(mn_cnt):
#         if alst[i] > blst[i]:
#             print('A')
#             break

#         elif alst[i] < blst[i]:
#             print('B')
#             break

#     else:
#         if al[0] > bl[0]:
#             print('A')

#         elif al[0] < bl[0]:
#             print('B')
#         else:
#             print('D')


n = 5
lst = [x for x in range(1,n+1)]
print(lst)
print(list(map(list,enumerate(lst))))













