
'''
5
20 50
10 100
30 120
60 110
80 90


7
0 20
3 10
5 17
7 13
8 15
14 25
16 30
'''
import heapq
from collections import defaultdict
class Compare1:

    def __init__(self,st,ed):
        self.st = st
        self.ed = ed

    def __lt__(self,other):
        if self.st != other.st:
            return self.st < other.st
        
        if self.ed != other.ed:
            return self.ed < other.ed

class Compare2:

    def __init__(self,ed,seat_num):
        self.ed = ed
        self.seat_num = seat_num

    def __lt__(self,other):

        if self.ed != other.ed:
            return self.ed < other.ed
        
        if self.seat_num != other.seat_num:
            return self.seat_num < other.seat_num
        
def play():
    time = -1

    while q and time<1000001:
        time+=1
        # start
        while q and q[0].st<time:
            
            qc = heapq.heappop(q)
            if not exit_lst:
                seat_dic[len(end_lst)] += 1
                heapq.heappush(end_lst,Compare2(qc.ed,len(end_lst)))

            else:
                seat_num = heapq.heappop(exit_lst)
                seat_dic[seat_num] += 1
                heapq.heappush(end_lst,Compare2(qc.ed,seat_num))

        # end
        while end_lst and end_lst[0].ed<=time:
            # 빠지면 자리 비워줘야함
            end_c = heapq.heappop(end_lst)
            heapq.heappush(exit_lst,end_c.seat_num)
            # exit_lst.append(end_c.seat_num)


n = int(input())

q = [] # 시작 시간, 끝나는 시간
end_lst = [] # 끝나는 시간, 좌석
exit_lst = [] # 좌석
seat_dic = defaultdict(int)

for _ in range(n):
    st,ed = map(int,input().split())
    heapq.heappush(q,Compare1(st,ed))

play()


print(len(seat_dic))
for i in range(len(seat_dic)):
    print(seat_dic[i], end=' ')
