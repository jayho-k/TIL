from itertools import permutations
from itertools import combinations
from itertools import product


lst = [1,2,3,4,5]

grid = [list(range(5)) for _ in range(5)]

print(list(combinations(lst, 2)))

print(list(product(*grid)))