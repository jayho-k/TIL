'''




'''
from collections import deque

def go_rep(wait):
    repair_empty = [0]*len(repair)
    waitq = deque(wait)
    timer = 0

    res = []
    
    while waitq:

        timer += 1
        rp_empty = 0
        for rj in range(len(repair_empty)):
            if repair_empty[rj]:
                repair_empty[rj]-=1

            if repair_empty[rj]==0:
                rp_empty+=1

        while rp_empty and waitq and waitq[0][0]<timer:
            wt,wcust,rg_num = waitq.popleft()
            for rpi in range(len(repair_empty)):
                if repair_empty[rpi]==0:
                    repair_empty[rpi]=repair[rpi]
                    res.append((rg_num,rpi,wcust))
                    rp_empty-=1
                    break
    return res

def go_regi():
    
    timer = 0
    cusq = deque()
    for i in range(len(custom)):
        cusq.append((custom[i],i))

    regi_empty = [0]*len(regi)
    wait = []
    while cusq:

        timer+=1
        
        # 창구에 존재 + 비어있는지
        rg_empty = 0
        for ri in range(len(regi_empty)):
            if regi_empty[ri]:
                regi_empty[ri]-=1

            if regi_empty[ri]==0:
                rg_empty+=1
        
        # 창구에 들어가기
        # 창구가 비어있고, 고객이 존재하고, 고객의 시간이 맞을 경우
        while rg_empty and cusq and cusq[0][0]<timer:
            t,cnum = cusq.popleft()
            for rei in range(len(regi_empty)):
                if regi_empty[rei]==0:
                    regi_empty[rei]=regi[rei] #걸리는 시간체크

                    # 총걸린 시간 = 창구에서 일한 시간 + 현재시간
                    # t는 고객이 도착한 시간이잖아 => 그럼 기다린 시간이 포함되지 않음
                    wait.append((regi[rei]+timer,cnum,rei)) #총걸린 시간, 고객번호, 창구번호
                    rg_empty-=1
                    break

    wait.sort(key=lambda x : (x[0],x[2]))
    # print(wait)
    return wait


for tc in range(1,int(input())+1):

    # 접수, 정비, 고객, 지갑접수, 지갑정비
    n,m,k,a,b = map(int,input().split())
    regi = list(map(int,input().split()))
    repair = list(map(int,input().split()))
    custom = list(map(int,input().split()))
    wait = go_regi()
    res = go_rep(wait)
    total = 0
    for rg_num,rp_num,wcust in res:
        if a == rg_num+1 and b == rp_num+1:
            total += wcust+1
    if total:
        print(f"#{tc} {total}")
    else:
        print(f"#{tc} {-1}")






# def go_regi():
    
#     timer = 0
#     cusq = deque()
#     for i in range(len(custom)):
#         cusq.append((custom[i],i))

#     regi_empty = [0]*len(regi)
#     repair_empty = [0]*len(repair)
#     waitq = deque()

#     res = []
#     while len(res)<len(custom):

#         timer += 1
#         rp_empty = 0
#         # print(timer)
#         for rj in range(len(repair_empty)):
#             if repair_empty[rj]:
#                 repair_empty[rj]-=1

#             if repair_empty[rj]==0:
#                 rp_empty+=1

#         while rp_empty and waitq and waitq[0][0]<timer:
#             wt,wcust,rg_num = waitq.popleft()
#             for rpi in range(len(repair_empty)):
#                 if repair_empty[rpi]==0:
#                     repair_empty[rpi]=repair[rpi]-1
#                     res.append((rg_num,rpi,wcust))
#                     rp_empty-=1
#                     break
        
#         rg_empty = 0
#         for ri in range(len(regi_empty)):
#             if regi_empty[ri]:
#                 regi_empty[ri]-=1

#             if regi_empty[ri]==0:
#                 rg_empty+=1

#         while rg_empty and cusq and cusq[0][0]<timer:
#             t,cnum = cusq.popleft()
#             for rei in range(len(regi_empty)):
#                 if regi_empty[rei]==0:
#                     regi_empty[rei]=regi[rei] #걸리는 시간체크
#                     waitq.append((regi[rei]+t,cnum,rei)) #총걸린 시간, 고객번호, 창구번호
#                     rg_empty-=1
#                     break
#         waitq = deque(sorted(list(waitq)))

#         # print(res)
#     return res