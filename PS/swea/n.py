# import math

# def mk_bst(lst,s):
#     if s == h:
#         print(tree)
#         return

#     m = len(lst)//2
#     tree[s].append(lst[m])
    
#     mk_bst(lst[:m],s+1)
#     mk_bst(lst[m+1:],s+1)


# T = 1
# for tc in range(1, T+1):
#     n = int(input())
#     lst = list(range(1,n+1))
#     h = math.ceil(math.log2(len(lst)))
#     tree = [[] for _ in range(h)]

#     mk_bst(lst,0)

#     print(tree)



lst = []
sset = set()
n = 100
print('insert')
tmp = -1
for i in range(n):
    c = lst.__sizeof__()
    sc = sset.__sizeof__()
    print('sc : ',sc)
    lst.append(i)
    sset.add(i)
    n = lst.__sizeof__()
    dif = n-c
    if tmp!=dif and dif!=0:
        print(dif)
        tmp = dif
print()
print(lst.__sizeof__())
print(sset.__sizeof__())
