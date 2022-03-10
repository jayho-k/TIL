'''
가로 => for i j
세로 => for j i
대각선1 => for i i
대각선2 => for i -i-1

lst = 
모든 숫자를 리스트에 집어 넣어
'''
# 따로 풀어주었을때 실행시간이 더 잛다

def sum_cross(lst):
    total_r = 0
    total_l = 0
    for i in range(len(lst)):
        total_r = lst[i][i]
        total_l = lst[i][-i-1]

    return total_r, total_l

def rot(lst):
    r_lst = list(map(list, zip(*lst)))
    return r_lst

T = 10
for tc in range(1,T+1):
    
    text_num = int(input())

    lsts = []
    for i in range(100):
        s = list(map(int, input().split()))
        lsts.append(s)
    # lst 생성되게 된다.
    # 가로는 그냥 for문으로 돌려서 다 집어 넣는다
    mx_lst = []
    r_lsts = rot(lsts)
    for i in range(len(lsts)):
        sm = sum(lsts[i])
        r_sm = sum(r_lsts[i])
        mx_lst.append(sm)
        mx_lst.append(r_sm)

    # 대각선
    sc1, sc2 = sum_cross(lsts)
    mx_lst.append(sc1)
    mx_lst.append(sc2)


    mx = max(mx_lst)
    print(f'#{tc} {mx}')




