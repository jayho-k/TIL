'''

1
1010
212

'''
def dfs(d, lst, bit):

    if d == len(lst):
        print(lst)
        
        return

    dfs(d+1, lst[d], bit[-1-d])
    dfs(d+1, lst[d], bit[-d])



T = int(input())

a = list(map(int,list(input())))
print(a)
b = list(map(int,list(input())))
print(b)

bit = [0,1]

dfs(0,a)

'''
1
1 1 1 1
1 1 1 2
1 1 2 1
1 1 1 1

'''
# from itertools import combinations

# T = int(input())
# grid = [list(map(int, input().split())) for _ in range(4)]

# a = []
# for i in grid:
#     a += i

# p_lst = list(combinations(a,7))
# p = set(p_lst)
# print(len(p))