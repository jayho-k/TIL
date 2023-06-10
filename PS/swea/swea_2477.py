'''
1
2 2 6 1 2
3 2
4 2
0 0 1 2 3 4

1
4 2 30 4 2
3 2 2 10
2 6
0 2 2 4 5 6 7 9 9 15 15 16 17 18 18 19 19 22 23 24 24 24 25 25 25 26 27 27 28 29
'''

from collections import deque

def go_regi():
    
    time=0
    wait_lst = deque()
    complete_lst = [] # time,e,p_num
    empty = [0]*len(regi) #[[time,p_num]*len(regi)]

    for p in range(len(person)):
        wait_lst.append((person[p],p))


    while wait_lst:
        time+=1

        # 시간 줄이기
        empty_cnt = 0
        for e1 in range(len(empty)):
            if empty[e1]:
                empty[e1]-=1

            if empty[e1]==0:
                empty_cnt+=1
        # 창구가 비었을 경우 추가해줘야함
        while empty_cnt and wait_lst and wait_lst[0][0]<time:
            
            # 들어온 시간
            _,p_num = wait_lst.popleft()
            
            # 창구 들어가기
            for e2 in range(len(empty)):
                if empty[e2]==0:
                    empty[e2]=regi[e2]
                    complete_lst.append((time+regi[e2],e2,p_num))
                    empty_cnt-=1
                    break
    
    complete_lst.sort(key=lambda x : (x[0],x[1]))
    # print(complete_lst)
    return complete_lst

def go_fix(comlete_lst):
    
    time=0
    wait_lst = deque(comlete_lst)  # time,regi_num,p_num
    print(comlete_lst)
    complete = [] 
    empty = [0]*len(fix)
    while wait_lst:

        time+=1
        empty_cnt = 0

        for e1 in range(len(empty)):
            if empty[e1]!=0:
                empty[e1]-=1

            if empty[e1]==0:
                empty_cnt+=1

        # print(empty)
        # print(empty_cnt)
        while empty_cnt and wait_lst and wait_lst[0][0] < time:
            _,regi_num,p_num = wait_lst.popleft()

            # fix들어가기
            for e2 in range(len(empty)):
                if empty[e2]==0:
                    empty[e2]=fix[e2]
                    empty_cnt-=1
                    complete.append((regi_num,e2,p_num))
                    break
    # print(wait_lst)
    return complete



for tc in range(1,int(input())+1):
    n,m,k,a,b = map(int,input().split())
    regi = list(map(int,input().split()))
    fix = list(map(int,input().split()))
    person = list(map(int,input().split()))
    total = 0 

    complete_lst = go_regi()
    res = go_fix(complete_lst)
    
    # print(a,b)
    # print(res)
    for rn,fn,pn in res:
        if a==rn+1 and b==fn+1:
            print(rn+1,fn+1)
            total+=pn+1

    if total:
        print(f"#{tc} {total}")
    else:
        print(f"#{tc} {-1}")




# from collections import deque

# def go_rep(wait):
#     repair_empty = [0]*len(repair)
#     waitq = deque(wait)
#     timer = 0

#     res = []
    
#     while waitq:

#         timer += 1
#         rp_empty = 0
#         for rj in range(len(repair_empty)):
#             if repair_empty[rj]:
#                 repair_empty[rj]-=1

#             if repair_empty[rj]==0:
#                 rp_empty+=1
#         # print("timer : ",timer)
#         # print("check전",repair_empty)
#         # print("rp_empty : ",rp_empty)
#         while rp_empty and waitq and waitq[0][0]<timer:
#             wt,wcust,rg_num = waitq.popleft()
#             for rpi in range(len(repair_empty)):
#                 if repair_empty[rpi]==0:
#                     repair_empty[rpi]=repair[rpi]
#                     res.append((rg_num,rpi,wcust))
#                     rp_empty-=1
#                     break
#         # print("check후",repair_empty)
#         # print(wait)
#         # print(res)
#         # print()
#     return res

# def go_regi():
    
#     timer = 0
#     cusq = deque()
#     for i in range(len(custom)):
#         cusq.append((custom[i],i))

#     regi_empty = [0]*len(regi)
#     wait = []
#     while cusq:
#         # 어떤 것으로 break걸지 생각하기
#         timer+=1
        
#         # 창구에 존재 + 비어있는지
#         rg_empty = 0
#         for ri in range(len(regi_empty)):
#             if regi_empty[ri]:
#                 regi_empty[ri]-=1

#             if regi_empty[ri]==0:
#                 rg_empty+=1
#         # 창구에 들어가기
#         # 창구가 비어있고, 고객이 존재하고, 고객의 시간이 맞을 경우
#         # print("check전",regi_empty)
#         # print("empty : ",empty)
#         while rg_empty and cusq and cusq[0][0]<timer:
#             t,cnum = cusq.popleft()
#             for rei in range(len(regi_empty)):
#                 if regi_empty[rei]==0:
#                     regi_empty[rei]=regi[rei] #걸리는 시간체크
#                     wait.append((regi[rei]+timer,cnum,rei)) #총걸린 시간, 고객번호, 창구번호
#                     rg_empty-=1
#                     break
#         # print("check후",regi_empty)
#         # print()

#     wait.sort(key=lambda x : (x[0],x[2]))
#     # print(wait)
#     return wait


# for tc in range(1,int(input())+1):
#     # 접수, 정비, 고객, 지갑접수, 지갑정비
#     n,m,k,a,b = map(int,input().split())
#     regi = list(map(int,input().split()))
#     repair = list(map(int,input().split()))
#     custom = list(map(int,input().split()))
#     wait = go_regi()
#     res = go_rep(wait)
#     total = 0
#     # print("wait",wait)
#     # print(a,b)
#     # print("res", res)
#     for rg_num,rp_num,wcust in res:
#         if a == rg_num+1 and b == rp_num+1:
#             # print('rg_num , rp_num : ',rg_num,rp_num, wcust)
#             total += wcust+1
#     if total:
#         print(f"#{tc} {total}")
#     else:
#         print(f"#{tc} {-1}")