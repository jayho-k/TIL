'''
4 7
20 15 10 17

5 20
4 42 40 26 46

'''
def get_tree(mid):
    gotten = 0
    for t in tree:
        tmp = t-mid
        if tmp > 0:
            gotten+=tmp
    return gotten

n,tree_length = map(int,input().split())
tree = list(map(int,input().split()))
start = 0
end = max(tree)
ans = 0
while start<=end:

    mid = (start+end)//2
    key = get_tree(mid)
    if key == tree_length:
        # ans = mid
        start = mid+1

    elif key > tree_length:
        start = mid+1

    else:
        end = mid-1

# print(ans)
print(end)



