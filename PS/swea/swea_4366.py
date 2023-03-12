'''

1
1010
212

'''
from itertools import product

def check(two,thr):
    # print(two,thr)
    # print(int(''.join(two),2), int(''.join(thr),3))
    if int(''.join(two),2)==int(''.join(thr),3):
        return int(''.join(two),2)
    else:
        return 0


def compare(pr,two,thr):

    w,h = pr
    th_fix = thr[h]
    if two[w]=='0':
        two[w]='1'
    else:
        two[w]='0'
    

    for zot in ['0','1','2']:
        if th_fix==zot:
            continue
        thr[h]=zot
        val = check(two[:],thr[:])
        thr[h]=th_fix
        if val:
            return val
    


for tc in range(1,int(input())+1):

    two = list(input())
    thr = list(input())
    two_lst = range(len(two))
    thr_lst = range(len(thr))    
    ans = 0
    for pr in product(two_lst,thr_lst):
        val = compare(pr,two[:],thr[:])
        if val:
            ans = val
            break
    print(f"#{tc} {ans}")