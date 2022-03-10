# al = input()
# al_up = al.upper()
# al_lst = list(al_up)
# print(al_lst)

# alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# alpha_lst = list(alpha)
# # print(alpha_lst)
# lst = []

# for i in alpha_lst:
#     cnt = al_lst.count(i)
#     lst.append(cnt)
    
# print(lst)
# mx = max(lst)
# print(mx)
# mx_wh = lst.index(mx)
# print(mx_wh)
# answer = alpha_lst[mx_wh]

# if lst.count(mx) > 1:
#     print('?')
# else:
#     print(answer)


# # 문제열 실패// 하지만 연속된 수와 관련된 코드
# snt = input()
# snt_lst = list(snt)
# lst = [snt_lst[0]]

# for i in range(1, len(snt_lst)):
#     if snt_lst[i-1] == ' ' and snt_lst[i] == snt_lst[i-1]:
#         continue
#     else:
#         lst.append(snt_lst[i-1])

# cnt = lst.count(' ')

# if lst[0] == ' ':
#     print(cnt - 1)
# elif lst[-1] == ' ':
#     print(cnt)
# else:
#     print(cnt + 1)

# # 정답
# word = input().split()
# print(len(word))

# a, b = list(input().split())

# rev_a = list(reversed(a))
# rev_b = list(reversed(b))

# ra = ''.join(rev_a)
# rb = ''.join(rev_b)

# if ra > rb:
#     print(ra)
# else:
#     print(rb)

tc = int(input())

mx = 0
mn = mx
for _ in range(tc):

    n = int(input())
    lst = list(map(int, input().split()))
    lst2 = lst[:]

    for number in lst:
        if mx < number:
            mx = number

    for number in lst:

        if mn > number:
            mn = number
            print(mn)
            print(number)



    # print(mx)
    # print(mn)
    # diff = mx - mn

    # print(diff)