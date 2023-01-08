

'''
3
asvdge ef ofmdofn
xvssc kxvbv
hull full suua pmlu
'''
# 9046_복호화
T = int(input())
for _ in range(1,T+1):
    dic = {}
    sp = input()
    for i in range(len(sp)):
        if sp[i] == ' ':
            continue

        if sp[i] in dic:
            dic[sp[i]]+=1

        else:
            dic[sp[i]]=1

    key_lst, val_lst = dic.keys(), dic.values()
    key_lst = list(key_lst)
    val_lst = list(val_lst)
    mx = max(val_lst)
    cnt = val_lst.count(mx)
    if cnt >1:
        print('?')
    else:
        print(key_lst[val_lst.index(mx)])