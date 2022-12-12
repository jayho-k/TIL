'''
7 1 2 3 4 5 6 7
8 1 2 3 5 8 13 21 34
0

'''

# combination
def dfs(d,n,v):

    if d == 6:
        print(v)
        return

    dfs(d+1,n,v+[lst[d]])
    dfs(d+1,n,v)

while 1:
    n,*lst = map(int,input().split())
    if n == 0:
        break
    dfs(0,n,[])
    print()



# tmp = []
# def dfs(d,idx):

#     if d == 6:
#         print(*tmp)
#         return

#     for i in range(idx,len(lst)):
#         if lst[i] not in tmp:
#             tmp.append(lst[i])
#             dfs(d+1,i)
#             tmp.pop()

# while 1:
#     n,*lst = map(int,input().split())
#     if n == 0:
#         break
#     dfs(0,0)
#     print()


# from itertools import combinations
# while 1:
#     n,*lst = map(int,input().split())
#     if n == 0:
#         break

#     # 굳이 list로 바꾸지 않아도 된다.
#     # for ans in list(map(list,combinations(lst,6))):
#     for ans in combinations(lst,6):
#         print(*ans)
#     print()
