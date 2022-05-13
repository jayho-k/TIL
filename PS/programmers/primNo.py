'''


'''


def prim(num):
    num = int(num)

    for i in range(2,int(math.sqrt(num))+1):
        if num%i == 0:            
            return False
    return True

def dfs(d,v,l):
    
    if d == len(n_lst):
        if v != '' and v[0] != '0' and v != '1':
            tmp.add(v)
        return

    dfs(d+1,v+l[d],l)
    dfs(d+1,v,l)




from itertools import permutations
import math

numbers = "00100007"
n_lst = list(numbers)
lst = list(set(map(''.join,list(permutations(n_lst,len(n_lst))))))
tmp = set()

for l in lst:
    dfs(0,'',l)

tmp_lst = list(tmp)

cnt = 0
for t in tmp_lst:
    if prim(t) == True:
        cnt += 1

print(cnt)