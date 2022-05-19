'''

궁수 3명 : D이하인 적중 가장 가까운 적 => itertools

5 5 1
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0
1 1 1 1 1

'''
def defence(hunter,enemy,d):

    cnt = 0
    while 1:
        # chck = [[0]*m for _ in range(n)]

        chck = []

        for hy,hx in hunter:
            for ey, ex in enemy:
                dis = abs(hy-ey)+abs(hx-ex)
                if d>= dis:
                    # chck[ey][ex] = 1
                    chck.append((ey,ex))

        if chck:
            for cy, cx in chck:
                grid[cy][cx] = 0
                cnt += 1

        new_enemy = []
        if enemy != []:
            for i in range(len(enemy)):
                enemy[i][0] += 1
                ey = enemy[i][0]
                ex = enemy[i][1]

                if 0<=ey<n and 0<=ex<m:
                    new_enemy.append((ey,ex))





    #     if new_enemy == []:
    #         break

    #     else:
    #         enemy = new_enemy
    
    # return cnt


def stp():

    for y in range(n):
        for x in range(m):
            # if grid[y][x] == 0:
            #     hunters.append([y,x])

            if grid[y][x] == 1:
                enemy.append([y,x])
    

from pprint import pprint
from itertools import combinations

n,m,d = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(n)]
enemy = []
hunters = []

stp()

for i in range(m):
    lst1 = [n,i]
    hunters.append(lst1)

hunters = list(map(list,combinations(hunters,3)))

mx = 0
for hunter in hunters:

    cnt = defence(hunter,enemy,d)
    mx = max(mx,cnt)

print(mx)


