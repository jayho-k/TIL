'''
배수마다 스위치가 바뀐다
전체를 N을 만들어야 한다
따라서 Y인것을 앞에 부터 찾는다

'''
lst = list('N' + input())
n = len(lst)

cnt = 0
for i in range(1,n):
    if lst[i] == 'Y':
        for s in range(i,n,i):
            
            if lst[s] == 'Y':
                lst[s] = 'N'
            else:
                lst[s] = 'Y'
            
        cnt += 1
        if 'Y' not in lst:
            break

print(cnt)
    













# lst = list('N' + input())
# n = len(lst)

# cnt = 0
# for i in range(1,n):
#     if i == 1:
#         if lst[i] == 'Y':
#             for s in range(1,n):
#                 if lst[s] == 'Y':
#                     lst[s] = 'N'
#                 else:
#                     lst[s] = 'Y'
                
#             cnt += 1
#             if 'Y' not in lst:
#                 break

#     else:
#         if lst[i] == 'Y':
#             for s in range(i, n, i):
#                 if lst[s] == 'Y':
#                     lst[s] = 'N'
#                 else:
#                     lst[s] = 'Y'
#             cnt += 1

#             if 'Y' not in lst:
#                 break

# print(cnt)
    