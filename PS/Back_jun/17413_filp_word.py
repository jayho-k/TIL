'''
baekjoon online judge
<open>tag<close>
<ab cd>ef gh<ij kl>
one1 two2 three3 4fourr 5five 6six
<int><max>2147483647<long long><max>9223372036854775807
'''

s = input()

no_flip=False

tmp_lst = []
tmp = ''
for i in range(len(s)):

    if s[i]=='<':
        tmp = tmp+s[i]
        no_flip = True

    elif s[i]=='>':
        tmp = tmp+s[i]
        tmp_lst.append(tmp)
        tmp = ''
        no_flip = False

    elif s[i] == ' ':
        tmp = tmp+s[i]
        tmp_lst.append(tmp)
        tmp=''

    elif no_flip==True:
        tmp = tmp+s[i]

    else:
        tmp = s[i]+tmp

if tmp != '':
    tmp_lst.append(tmp)

print(''.join(tmp_lst))