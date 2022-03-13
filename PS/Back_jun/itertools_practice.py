from itertools import permutations
from itertools import combinations
from itertools import product
from pprint import pprint

lst = [1,2,3,4,5]

grid = [0]*9
lst2= [1,1,1]

# print(list(combinations(lst, 2)))
# print(list(product(*grid)))

pprint(grid)

print(list(map(list,product(lst2, grid))))