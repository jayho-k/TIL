'''
3 4
ohhenrie
charlie
baesangwook
obama
baesangwook
ohhenrie
clinton


n : 듣
m : 보
'''
import sys
def findNeverHS(never_h,never_s):
    return list(never_h.intersection(never_s))


input = sys.stdin.readline
n,m = map(int,input().split())
never_h = set(input().rstrip() for _ in range(n))
never_s = set(input().rstrip() for _ in range(m))

lst = findNeverHS(never_h, never_s)
lst.sort()
print(len(lst))
for l in lst:
    print(l)



# import sys
# def findNeverHS(never_h,never_s):
#     lst = []
#     for h in never_h:
#         if h in never_s:
#             lst.append(h)
#     return lst


# input = sys.stdin.readline
# n,m = map(int,input().split())
# never_h = set(input().rstrip() for _ in range(n))
# never_s = set(input().rstrip() for _ in range(m))
# lst = findNeverHS(never_h, never_s)
# lst.sort()
# print(len(lst))
# for l in lst:
#     print(l)
