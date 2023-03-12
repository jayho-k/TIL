'''
1
7 2 9   
1 1 7 1 
2 1 7 1
5 1 5 4
3 2 8 4 
4 3 14 1
3 4 3 3 
1 5 8 2 
3 5 100 1
5 5 1 1

'''
from collections import defaultdict

def move(micros):
    micro_dic = defaultdict(list)
    for micro in micros:
        y,x,m_num,d = micro
        ny = y+dy[d]
        nx = x+dx[d]
        micro_dic[(ny,nx)].append((m_num,d))
    return micro_dic

def check(micro_dic):
    new_micro_lst = []
    for micro in micro_dic:

        #setting
        my,mx = micro[0],micro[1]
        micro_lst = micro_dic[micro]

        # 미생물이 2개 이상일 경우
        if len(micro_lst)>=2:
            micro_lst.sort(reverse=True)
            md = micro_lst[0][1]
            m_num = 0
            for mn,_ in micro_lst:
                m_num+=mn
            new_micro_lst.append((my,mx,m_num,md))
        
        # 미생물이 1개일 경우
        else:
            m_num,md = micro_lst[0]

            # 범위 내에 있을 경우
            if 1<=my<n-1 and 1<=mx<n-1:
                new_micro_lst.append((my,mx,m_num,md))

            # 약품이 있는 경우
            else:
                m_num//=2
                if m_num:
                    new_micro_lst.append((my,mx,m_num,rev[md]))

    return new_micro_lst

def count_micro(micros):
    total = 0
    for _,_,m_num,_ in micros:
        total+=m_num
    return total

for tc in range(1,int(input())+1):
    n,m,k = map(int,input().split())
    micros = [list(map(int,input().split())) for _ in range(k)]

    # 상1 하2 좌3 우4
    dy = [0,-1,1,0,0]
    dx = [0,0,0,-1,1]
    rev = [0,2,1,4,3]

    for _ in range(m):
        micro_dic = move(micros)
        micros = check(micro_dic)

    total = count_micro(micros)
    print(f"#{tc} {total}")