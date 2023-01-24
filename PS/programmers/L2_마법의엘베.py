def compare(storey):
    
    cnt = 0
    while storey:
        remain = storey%10
        # 5~9
        if remain>5:
            cnt+=(10-remain)
            storey+=10
        
        # 0~4
        elif remain<5:
            cnt+=remain
        
        # 5
        else:
            # 앞자리가 5~9 => 더해주는 것이 더 빠름
            if (storey//10)%10>=5:
                storey+=10
            cnt+=remain
        storey//=10
        
    return cnt

def solution(storey):
    cnt = compare(storey)
    return cnt



# def down(storey):
#     total = 0
#     for i in list(str(storey)):
#         total+=int(i)
#     return total

# def up2down(storey):
#     lst = list(map(int,list(str(storey))))
#     tmp = []
#     for i in range(len(lst)-1,0,-1):
#         diff = 10-lst[i]
#         tmp.append((lst[i],diff))
#         lst[i-1]+=1
    
    

# def solution(storey):
#     n = len(str(storey))
#     cnt = down(storey)
#     real_cnt_lst = up2down(storey)
#     print(real_cnt_lst)
#     return



# from collections import deque
# def bfs(c,buttons,storey):
#     visited = set()
#     visited.add(storey)
#     q = deque([(storey,0)])
#     while q:
#         stor,cnt = q.popleft()
#         for d in range(len(buttons)):
#             n_stor = stor+buttons[d]
            
#             if n_stor>0 and n_stor not in visited \
#             and n_stor<=10**c:
#                 q.append((n_stor,cnt+1))
#                 visited.add(n_stor)
#             elif n_stor==0:
#                 cnt+=1
#                 return cnt

# def solution(storey):
#     c = len(str(storey))
#     buttons = []
#     for i in range(c+1):
#         buttons.append(-10**i)
#         if i==c:
#             continue
#         buttons.append(10**i)
#     cnt = bfs(c,buttons,storey)
#     return cnt