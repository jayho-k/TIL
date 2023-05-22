"""

4
3 5 2 7

4
9 5 4 8
"""
from collections import deque

def play():

    for i in range(n):

        while stack and lst[stack[-1]] < lst[i]:
            ans[stack.pop()] = lst[i]

        stack.append(i)

    for s in stack:
        ans[s] = -1

n = int(input())
lst = list(map(int,input().split()))
stack = []
ans = [0]*len(lst)
play()
print(*ans)