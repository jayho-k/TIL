'''

55-50+40


'''

s = input()
lst = s.split('-')

ans_lst = []
for ls in lst:
    tmp = 0
    l = ls.split('+')
    
    for t in l:
        tmp+= int(t)

    ans_lst.append(tmp)

ans = ans_lst[0]
for a in ans_lst[1:]:
    ans -= a

print(ans)





# for s in st:
#     if s == '-':

#         total += int(tmp)


#         tmp_lst.append(tmp)
#         tmp_lst.append('-')
#         if flag == False:
#             flag = True
#             tmp_lst.append('(')
#         else:
#             flag = False
#             tmp_lst.append(')')
#         tmp = ''
#         pass
#     elif s == '+':
#         tmp_lst.append(tmp)
#         tmp_lst.append('+')
#         tmp = ''
#     else:
#         tmp+=s

# else:
#     if flag == False:
#         tmp_lst.append(tmp)
#     else:
#         tmp_lst.append(tmp)
#         tmp_lst.append(')')

# print(tmp_lst)
