

from collections import defaultdict
from itertools import combinations
def isSame(com):
    for i in [2,3,4]:
        for j in [2,3,4]:
            if com[0]*i == com[1]*j:
                return True
    return False

def play(set_weights,dic):
    ans = 0
    for com in combinations(set_weights,2):
        if isSame(com):
            ans+=dic[com[0]]*dic[com[1]]
    return ans

def com_cnt(num):
    return num*(num-1)/2

def solution(weights):
    
    ans = 0
    
    # setting dictionary
    dic = defaultdict(int)
    for i in range(len(weights)):
        dic[weights[i]]+=1
    
    # 같은 수 2이상 있는 경우 계산
    for v in dic:
        if dic[v]>=2:
            ans+=com_cnt(dic[v])
            
    # 서로 다른 weight계산
    set_weights = list(set(weights))
    ans += play(set_weights,dic)
    
    return ans