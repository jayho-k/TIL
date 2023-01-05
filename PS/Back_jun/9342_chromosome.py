'''
{A, B, C, D, E, F}

15
AFC
AAFC
AAAFFCC
AAFCC
BAFC
QWEDFGHJMNB
DFAFCB
ABCDEFC
DADC
SDFGHJKLQWERTYU
AAAAAAAAAAAAABBBBBBBBBBBBBBCCCCCCCCCCCCCCCCCCDDDDDDDDDDDEEEEEEEEEEEEEEEFFFFFFFFC
AAAFFFFFBBBBCCCAAAFFFF
ABCDEFAAAFFFCCCABCDEF
AFCP
AAFFCPP

1
AAAFFCC
'''
from collections import deque
def caculate(sp):
    j = 1
    for i in range(1,len(sp)):

        if lst[j]=='C':
            if sp[i]=='C':
                continue
            else:
                if i == len(sp):
                    return 'Infected!'
                else:
                    return 'Good'

        else:
            if sp[i]==lst[j]:
                continue
            else:
                if sp[i] == lst[j+1]:
                    j+=1
                else:
                    return 'Good'
    return 'Infected!'

lst = ['','A','F','C']
setting = set(lst)

T = int(input())
for _ in range(1,T+1):
    sp = input()
    print(caculate(sp))

        