# def total_cnt(k,d):
#     squ_d = d**2
#     total = 0
#     for i in range(0,d+1,k):
#         for j in range(i,d+1,k):
#             if squ_d>=(i**2)+(j**2):
#                 if i==j:
#                     total+=1
#                 else:
#                     total+=2
#             break
        
            
#     return total

'''
효율성에 관한 문제이다
x = int(math.sqrt(d*d-y*y)) 
total+=(x//k)+1
위 부분이 핵심이다
'''


import math
def total_cnt(k, d):
    total = 0
    for y in range(0,d+1,k):
        x = int(math.sqrt(d*d-y*y))
        total+=(x//k)+1
    return total

def solution(k, d):
    
    total = total_cnt(k, d)
                    
    return total