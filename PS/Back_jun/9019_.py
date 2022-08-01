'''
3
1234 3412
1000 1
1 16


'''
def D(num):
    num = (num*2)
    return num%10000

def S(num):
    if num == 0:
        num = 9999
    else:
        num -= 1
    return num

def L(num):

    num_lst = list(str(num))
    if num <10:
        num_lst.insert(0,'0')
    if num <100:
        num_lst.insert(0,'0')
    if num <1000:
        num_lst.insert(0,'0')
    num = int(num_lst[1]+num_lst[2]+num_lst[3]+num_lst[0])
    return num

def R(num):
    num_lst = list(str(num))
    if num <10:
        num_lst.insert(0,'0')
    if num <100:
        num_lst.insert(0,'0')
    if num <1000:
        num_lst.insert(0,'0')

    num = int(num_lst[3]+num_lst[0]+num_lst[1]+num_lst[2])
    return num

def bfs(st_num,end_num, visited):

    q = deque([(st_num,'')])

    while q:
        
        num,alpha = q.popleft()
    
        # print(num,alpha)
        # print(q)

        visited[num] = 1
        if num == end_num:
            print(alpha)
            return

        n_num1 = D(num)
        if visited[n_num1]==0:
            alpha1 = alpha[:] + 'D'
            q.append((n_num1,alpha1))
            visited[n_num1] = 1

        n_num2 = S(num)
        if visited[n_num2]==0:
            alpha2 = alpha[:] + 'S'
            q.append((n_num2,alpha2))
            visited[n_num2] = 1

        n_num3 = L(num)
        if visited[n_num3]==0:
            alpha3 = alpha[:] + 'L'
            q.append((n_num3,alpha3))
            visited[n_num3] = 1

        n_num4 = R(num)
        if  visited[n_num4]==0:
            alpha4 = alpha[:] + 'R'
            q.append((n_num4,alpha4))
            visited[n_num4] = 1


from collections import deque
T = int(input())

for tc in range(1,T+1):
    st_num, end_num = map(int,input().split())
    visited = [0]* 10000
    bfs(st_num,end_num,visited)
