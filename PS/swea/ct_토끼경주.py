'''
5
100 3 5 2 10 2 20 5
200 6 100
300 10 2
200 3 20
400


우선순위
현재까지의 총 점프 횟수가 적은 토끼, (jump수)
현재 서있는 행 번호 + 열 번호가 작은 토끼, (행열이 저장)
행 번호가 작은 토끼, ()
열 번호가 작은 토끼, ()
고유번호가 작은 토끼, (앞에 있는 토끼)

순서 : 우선순위 뽑음 => 상하좌우 위치 선정 => 우선순위 뽑음 => 이동 => 점수

1. 상하좌우
    1) 격자를 벗어남 => 방향을 바꿔 한 칸 이동
    2) 우선순위
        행 번호 + 열 번호가 큰 칸,
        행 번호가 큰 칸,
        열 번호가 큰 칸,
    3) 우선순위 높은 칸으로 이동
    3) 그 칸을 i번을 제외한 나머지 y+x


heapq 커스텀 방법
heap트리 구현하기
import heapq

class node:
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def __lt__(self, other):
        if self.A < other.A:   #오름차순
            return True
        elif self.A == other.A:
            return self.B > other.B  #첫번재 변수가 같으면 두번재 변수로 내림차순
        else:
            return False

    def __str__(self):
        return 'A : {}, B : {}'.format(self.A, self.B)

'''
# 정의
import heapq

max_p = 2001
pid_lst = [0]*max_p
id_2_idx = [0]*max_p
d_lst = [0]*max_p
jump_lst = [0]*max_p
loc_lst = [(0,0)]*max_p
result = [0]*max_p
is_runned = [0]*max_p
total_sum = 0

"""
# 커스텀 정렬을 위해 구조체를 만들어 준다.

class 안에 __lt__(self, other) 함수를 재정의해 주고
return 값은 True False로 해주면 된다.
"""
class Rabbit:
    def __init__(self,y,x,j,pid):
        self.y = y
        self.x = x
        self.j = j
        self.pid = pid

    def __lt__(self,other):

        # jump가 other과 다르다면 => True
        if self.j != other.j:
            return self.j < other.j

        # x+y가 다르다면 
        if self.x + self.y != other.x + other.y:
            return self.x + self.y < other.x + other.y
        
        # y가 다르다면
        if self.y != other.y:
            return self.y < other.y
        
        # x가 다르다면
        if self.x != other.x:
            return self.x < other.x

        return self.pid < other.pid


def init():
    global N,M,P
    N,M,P = o_lst[0],o_lst[1],o_lst[2]
    for i in range(1,P+1):
        pid_lst[i-1] = o_lst[i*2-2+3]
        d_lst[i-1] = o_lst[i*2-1+3]
        id_2_idx[pid_lst[i-1]] = i-1

def compare(com1,com2):
    
    if com1.y+com1.x != com1.y+com2.x:
        return com1.y+com1.x < com1.y+com2.x

    if com1.y!=com2.y:
        return com1.y<com2.y
    
    if com1.x!=com2.x:
        return com1.x<com2.x

    return com1.pid<com2.pid

# k번 반복 ==> 우선순위가 높은 토끼를 뽑아 멀리 보내주기
# print("위치")        
# print(up_r.y,up_r.x)
# print(down_r .y,down_r .x)
# print(right_r.y,right_r.x)
# print(left_r.y,left_r.x)
# print()

def race():
    global total_sum
    k,s = o_lst[0],o_lst[1]
    
    # pq에 넣기
    rabbit_pq = []
    for i in range(P):
        y,x = loc_lst[i]
        new_rabbit = Rabbit(y,x,jump_lst[i],pid_lst[i])
        heapq.heappush(rabbit_pq,new_rabbit)
    

    # 경주 시작
    for _ in range(k):
        cur_r = heapq.heappop(rabbit_pq)
        comp_r = copy_r(cur_r)
        comp_r.y =0
        comp_r.x =0
        
        up_r = get_up(copy_r(cur_r),d_lst[cur_r.pid])
        down_r = get_down(copy_r(cur_r),d_lst[cur_r.pid])
        right_r = get_right(copy_r(cur_r),d_lst[cur_r.pid])
        left_r = get_left(copy_r(cur_r),d_lst[cur_r.pid])

        if compare(comp_r,up_r):
            comp_r = up_r
        
        if compare(comp_r,down_r):
            comp_r = down_r
 
        if compare(comp_r,right_r):
            comp_r = right_r
 
        if compare(comp_r,left_r):
            comp_r = left_r

        comp_r.j+=1
        heapq.heappush(rabbit_pq,comp_r)
        com_idx = id_2_idx[comp_r.pid]
        loc_lst[com_idx] = (comp_r.y,comp_r.x)
        jump_lst[com_idx]+=1
        
        is_runned[com_idx] = True

        # 얘만 마이너스 시키고 나중에 total을 더해주면 점수가 된다.
        result[com_idx] -= (comp_r.y + comp_r.x)
        total_sum += (comp_r.y + comp_r.x)

    bonus_rabbit = Rabbit(0,0,0,0)
    while rabbit_pq:
        cur = heapq.heappop(rabbit_pq)

        if not is_runned[id_2_idx[cur.pid]]:
            continue

        if compare(bonus_rabbit,cur):
            bonus_rabbit = cur
    
    result[id_2_idx[bonus_rabbit.pid]] += s

def dis_change():
    pid,L = o_lst[0],o_lst[1]
    idx = id_2_idx[pid]

    d_lst[idx] *= L


def find_winner():
    ans = 0
    for i in range(P):
        ans = max(ans,result[i]+total_sum)
    print("total_sum",total_sum)
    print(result)
    print(ans)

def copy_r(cur_r):
    return Rabbit(cur_r.y,cur_r.x,cur_r.j,cur_r.pid)

def get_up(r,d):
    # n-1 (d-(n-1)-위치)
    # 격자를 넘었을 경우 vs 안넘을 경우

    # 위치
     #왔다 갔다가 했을 때 4x4면 총 6칸 밖에 안나옴 따라서 n-1
    d%= 2*(N-1)

    # 위쪽 범위를 넘었을 때
    if d >= r.y:
        d -= (r.y)
        r.y=0
    
    # 위쪽 범위를 넘지 않았을 때
    else:
        r.y -= d
        d = 0

    if d>= N-1-r.y:
        d -= N-1-r.y
        r.y = N-1
    else:
        r.y += d
        d = 0

    r.y -= d
    
    return r


def get_down(r,d):
    d%= 2*(N-1)

    if d >= N-1-r.y:
        d -= (N-1-r.y)
        r.y = N-1
    
    else:
        r.y += d
        d = 0

    if d>= r.y:
        d -= r.y
        r.y = 0
    else:
        r.y-=d
        d = 0

    r.x -= d
    return r


def get_right(r,d):
    d%= 2*(M-1)

    if d >= -1-r.y:
        d -= (-1-r.y)
        r.y = -1
    
    else:
        r.y += d
        d = 0

    if d>= r.y:
        d -= r.y
        r.y = 0
    else:
        r.y-=d
        d = 0

    r.x -= d
    return r

def get_left(r,d):
    d%= 2*(M-1)

    # 위쪽 범위를 넘었을 때
    if d >= r.x:
        d -= (r.x)
        r.y=0
    
    # 위쪽 범위를 넘지 않았을 때
    else:
        r.x -= d
        d = 0

    if d>= M-1-r.x:
        d -= M-1-r.x
        r.x = M-1
    else:
        r.x += d
        d = 0

    r.x -= d
    
    return r

for _ in range(int(input())):
    
    lst = list(map(int,input().split()))
    o_num,o_lst = lst[0],lst[1:]
    
    if o_num==100:
        init()

    elif o_num==200:
        race()
        
    elif o_num==300:
        dis_change()

    elif o_num==400:
        find_winner()


