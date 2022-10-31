'''
quqacukqauackck
quackquackquackquackquackquackquackquackquackquack
'''
s = input()
lst = s.split('quack')

ans = 0
if len(lst)>1:
    tmp = ''.join(lst)
    if tmp == '':
        ans = 1
    else:
        ans = -1
else:
    tmp_s = list(lst[0])
    dock ='quack'
    cnt = 0
    while 1:
        for d_o in dock:
            for i in range(len(tmp_s)):
                if d_o == tmp_s[i]:
                    tmp_s = '_'
                    break
            else:
                break
        else:
            cnt+=1
    print(cnt)


print(ans)