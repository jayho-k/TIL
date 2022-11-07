'''
5 5 1
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0
1 1 1 1 1

'''
from pprint import pprint

def defense(h_lst,e_lst,d):
    kill_cnt = 0
    while 1:
        targeted_lst = []
        for hy,hx in h_lst:
            # mn = 1e9
            # targeted_e = (-1,-1)
            # and mn > r
            targeted_e_lst = []
            for ey,ex in e_lst:
                r = abs(hy-ey)+abs(hx-ex)
                if r <= d  and (ey,ex) not in targeted_lst:
                    targeted_e_lst.append((ey,ex))
                    # targeted_e = (ey,ex)

            if targeted_e_lst != []:
                targeted_e_lst.sort(key = lambda x : (x[1]))
                targeted_lst.append(targeted_e_lst[0])
                kill_cnt += 1

            # print(targeted_e_lst)

            # if targeted_e != (-1,-1):
            #     targeted_lst.append(targeted_e)
            #     kill_cnt += 1
        # print(targeted_lst)

        n_e_lst = []
        for tey,tex in e_lst:
            if tey+1<n and (tey,tex) not in targeted_lst:
                n_e_lst.append((tey+1,tex))
        
        if n_e_lst == []:
            return kill_cnt
        e_lst = n_e_lst

def h_loc():
    h_lst = []
    for x in range(m):
        h_lst.append((n,x))
    return list(map(list,combinations(h_lst,3)))

def e_loc():
    e_lst = []
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 1:
                e_lst.append((y,x))
    return e_lst

from itertools import combinations
n,m,d = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
h_lst_com = h_loc()
e_lst = e_loc()

mx = 0
for i in range(len(h_lst_com)):
    # print('**** : ',h_lst_com[i])
    cnt = defense(h_lst_com[i],e_lst,d)
    mx = max(mx, cnt)
    # print('*'*40)

print(mx)



