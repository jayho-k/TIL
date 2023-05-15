'''
[[4,5],[4,8],[10,14],[11,13],[5,12],[3,7],[1,4]]

3

'''
def inter(t1,t2):
    if t1[1]>t2[0]:
        return (max(t1[0],t2[0]), min(t1[1],t2[1]))
    
    return None

def solution(targets):
    ans = 1
    targets.sort()
    comp = (-1,1e9+1)
    for target in targets:
        comp = inter(comp,target)
        if not comp:
            comp = target
            ans+=1
    return ans

target = [[4,5],[4,8],[10,14],[11,13],[5,12],[3,7],[1,4]]
print(solution(target))