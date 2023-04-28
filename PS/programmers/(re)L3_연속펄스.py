'''
양수가 나올 수 밖에 없음
왜냐하면 -1과 1을 번갈아가면서 곱하게 된다.
즉 -1일 수도 있고 아닐 수도 있기 때문
'''
def solution(sequence):
    ans = 0
    p = -1
    tmp1 = 0
    tmp2 = 0

    for i in range(len(sequence)):

        # 조건을 봐주는 것
        if tmp1+sequence[i]*p>=0:
            tmp1+=sequence[i]*p
            if ans<tmp1:
                ans=tmp1
        else:
            tmp1=0
        
        p*=-1
        
        if tmp2+sequence[i]*p>=0:
            tmp2+=sequence[i]*p
            if ans<tmp2:
                ans=tmp2
        else:
            tmp2=0
            
    return ans

sequence = [2, 3, -6, 1, 3, -1, 2, 4]	
print(solution(sequence))
