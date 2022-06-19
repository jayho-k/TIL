'''
"aabbaccc"	7
"ababcdcdababcdcd"	9
"abcabcdede"	8
"abcabcabcabcdededededede"	14
"xababcdcdababcdcd"	17

'''

s = 'a'
# print(s[:3])
mn = 1e9
for i in range(1,len(s)):

    lst = []
    for j in range(0,len(s),i):
        lst.append(s[j:j+i])

    num = 1
    tmp = [lst[0]]
    for k in range(1,len(lst)):
        if tmp[-1] == lst[k]:

            num += 1
            if k == len(lst)-1:
                tmp[-1] = str(num)+lst[k]

        else:
            if num == 1:
                tmp.append(lst[k])

            else:
                tmp[-1] = str(num)+tmp[-1]
                tmp.append(lst[k])
                num = 1
    
    ans = ''.join(tmp)
    mn = min(mn,len(ans))
    # print(tmp,len(ans))

if len(s) == 1:
    print(1)

else:
    print(mn)




# s_lst = list(s)

# mn = 1e9

# loc = []

# for i in range(1,len(s_lst)//2+1):

#     tmp1 = []

#     for j in range(0,len(s_lst),i):
#         t = s_lst[j:j+i]
#         tmp1.append(t)
#     # print(tmp1)

#     tmp2 = [tmp1[0]]

#     t_num = 0
#     for k in range(1,len(tmp1)):

#         if tmp2[-1] == tmp1[k]:
#             t_num += 1
#             if k == len(tmp1)-1:
#                 tmp2.append([t_num])

#         else:
#             if t_num == 0:
#                 tmp2.append(tmp1[k])

#             else:
#                 tmp2.append([t_num])
#                 tmp2.append(tmp1[k])
#                 t_num = 0

#     print(tmp2,len(tmp2))


#     a_lst = []
#     for t in tmp2:
#         a_lst += t

#     if mn > len(a_lst):
#         mn = len(a_lst)


# print(mn)








    # for k in range(len(tmp1)-1,0,-1):
    # # for k in range(len(tmp1)-1,0,-1):
    #     if tmp1[k] == tmp1[k-1]:
    #         t_num += 1
    #         tmp1.pop(k)

    #     else:
    #         if t_num == 0:
    #             continue
    #         else:
    #             tmp1.append(t_num)

    # print(tmp1)





    # tmp2 = [tmp1[0]]
    # for k in range(1,len(tmp1)):

    #     if tmp2[-1] == tmp1[k]:
    #         if type(tmp2[-2]) == int:
    #             tmp2[-2] += 1
    #         else:
    #             tmp2.insert(-2,1)
            
    #     else:
    #         tmp2.append(tmp1[k])

    # print(tmp2)