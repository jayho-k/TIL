'''
어떤 문자를 정확히 k개 포함하는 가장 잛은 연속 문자열의 길이
조건 1 : k개 포함
조건 2 : 가장 짧은 길이


어떤 문자를 정확히 k개를 포함하고, 문자열의 첫번째와 마지막 글자가 같고 가장 긴 문자열의 길이
조건 1 : k개 포함
조건 2 : 첫, 끝 같음
조건 3 : 가장 김

'''
import sys
input = sys.stdin.readline

t = int(input())

for _ in range(t):
    st = list(input())
    n = len(st)
    k = int(input())

    mx = 0
    mn = 1e9

    total = 0
    end = 1
    for strt in range(n):
        stnd = st[strt]
        cnt = 1

        while end < n:
            com = st[end]
            if com==stnd:
                cnt += 1
                if cnt == k:
                    total = len(st[strt:end+1])
                    mx = max(mx, total)
                    mn = min(mn, total)
                    break

            end += 1

        cnt -= 1

    if mn != 1e9 or mx != 0:
        print(mn, mx)
    else:
        print(-1)




# import sys
# input = sys.stdin.readline

# t = int(input())

# for _ in range(t):
#     st = list(input())
#     n = len(st)
#     k = int(input())

#     mx = 0
#     mn = 1e9
#     for i in range(n):
#         stnd = st[i]
#         cnt1 = 1
#         total1 = 1
#         for j in range(i+1,n):
#             com = st[j]

#             # 3번: k개 포함하면서 가장 잛음
#             if stnd == com:
#                 total1 += 1
#                 cnt1 += 1
#                 if cnt1 > k:
#                     continue

#                 if cnt1 == k:
#                     mn = min(total1, mn)
#                     mx = max(total1, mx)
#             else:
#                 total1 += 1


#     if mn != 1e9 or mx != 0:
#         print(mn, mx)
#     else:
#         print(-1)



# import sys
# input = sys.stdin.readline

# t = int(input())

# for _ in range(t):
#     st = list(input())
#     n = len(st)
#     k = int(input())

#     mx = 0
#     mn = 1e9

#     for i in range(n):
#         stnd = st[i]

#         for j in range(i+1,n):
#             com = st[j]
#             com_lst = st[i:j+1]
#             leng = len(com_lst)
#             cnt = com_lst.count(stnd)

#             if cnt > k:
#                 break
#             elif cnt == k:
#                 mn = min(mn,leng)

#                 if com_lst[0] == com_lst[-1]:
#                     mx = max(mx,leng)

#     if mn != 1e9 or mx != 0:
#         print(mn, mx)
#     else:
#         print(-1)








# import sys
# input = sys.stdin.readline

# t = int(input())

# for _ in range(t):
#     st = list(input())
#     n = len(st)
#     k = int(input())

#     mx = 0
#     mn = 1e9

#     for i in range(n):
#         stnd = st[i]

#         for j in range(i+1,n):
#             com = st[j]
#             com_lst = st[i:j+1]
#             leng = len(com_lst)
#             cnt = com_lst.count(stnd)

#             if cnt > k:
#                 continue
#             elif cnt == k:
#                 mn = min(mn,leng)

#                 if com_lst[0] == com_lst[-1]:
#                     mx = max(mx,leng)

#     if mn != 1e9 or mx != 0:
#         print(mn, mx)
#     else:
#         print(-1)









