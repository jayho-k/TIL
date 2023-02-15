from itertools import permutations
from itertools import combinations
from itertools import product
from itertools import accumulate
from itertools import combinations_with_replacement as cwr
from collections import Counter
from pprint import pprint


tu = (1,2,3,4,5,1,1,1,1,1,1,1,1)
print(Counter(tu))



# print(list(cwr(range(11),10)))




# # accumulate
# def func(x,y):
#     print(x,y)
#     return x+y
# n = 5
# # grid = [[0]*(n+1) for _ in range(n+1)]
# grid = [list(range(1,n+1)) for _ in range(n)]
# lst = list(range(1,n+1))
# print(lst)
# res_grid = []
# for _ in range(n):
#     res = list(accumulate(lst,func))
#     res_grid+=res
    
# pprint(grid)
# print(res)