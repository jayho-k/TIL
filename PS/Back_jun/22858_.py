'''
5 2
4 1 3 5 2
4 3 1 2 5


4 1
4 3 2 1
4 3 2 1

'''

n,k = map(int,input().split())

s_lst = list(map(int,input().split()))
d_lst = list(map(int,input().split()))


for _ in range(k):
    
    ns_lst = [0]*n

    for i in range(n):
        ns_lst[d_lst[i]-1] = s_lst[i]
    s_lst = ns_lst
print(*s_lst)