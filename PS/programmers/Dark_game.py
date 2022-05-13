'''
1. 기회 3번
2. 점수 : 0 10
3. s 1   d 2    t 3 
4. 스타상(*) 해당 점수와 바로 전에 얻은 점수를 각 2배 , 아차상(#) 해당 점수 마이너스
5. 
스타상(*)은 첫 번째 기회에서도 나올 수 있다. 이 경우 첫 번째 스타상(*)의 점수만 2배가 된다. (예제 4번 참고)
스타상(*)의 효과는 다른 스타상(*)의 효과와 중첩될 수 있다. 이 경우 중첩된 스타상(*) 점수는 4배가 된다. (예제 4번 참고)
스타상(*)의 효과는 아차상(#)의 효과와 중첩될 수 있다. 이 경우 중첩된 아차상(#)의 점수는 -2배가 된다. (예제 5번 참고)


1	1S 2D* 3T  	11 * 2 + 22 * 2 + 33


1S*2T*3S
'''

dartResult = '1D2S3T*'
lst = list(dartResult)
nums = list(map(str, range(0,11)))

n_lst = [lst[0]]
for i in range(1,len(lst)):
    if n_lst[-1] in nums and lst[i] in nums:
        t = n_lst.pop()
        t = t+lst[i]
        n_lst.append(t)
    else:
        n_lst.append(lst[i])

lst = n_lst
b = {'S':1,'D':2,'T':3}
n = len(lst)

bonus = 0
total = 0
tmp = 0
stack = 0
shap = 0 

for i in range(n-1,-1,-1):
    v = lst[i]
    if v == '*':
        stack += 2

    elif v == '#':
        shap += 1
    else:        
        if v in b:
            bonus = b[v]

        elif v in nums:
            score = int(v)
            if stack == 0:
                if shap == 0:
                    total +=  (score**bonus)
                else:
                    total +=  (score**bonus)*(-1)
                    shap -= 1
            else:
                if shap == 0:
                    if stack > 2:
                        total += (score**bonus)*4
                        stack -= 2
                    else:
                        total +=  (score**bonus)*2
                        stack -= 1

                else:
                    total +=  (score**bonus)*2*(-1)
                    stack -= 1
                    shap -= 1

                    
print(total)











# dartResult = '1S2D*3T'
# lst = list(dartResult)
# nums = list(map(str, range(0,11)))
# b = {'S':1,'D':2,'T':3}

# n = len(lst)

# cnt = lst.count('*')
# score = 0
# total = 0
# tmp = 0

# for i in range(n):


#     v = lst[i]

#     if v == '*':
#         total += tmp*(cnt*2)
#         tmp = 0
#         cnt -= 1

#     elif v == '#':
#         if cnt != 0:
#             total += tmp* (-1)*cnt
#         else:
#             total += tmp* (-1)
#         tmp = 0

#     else:
#         if tmp != 0:
#             total += tmp
#             tmp = 0

#         if v in b:
#             bonus = b[v]
#             tmp =  score**bonus
#             score = 0

#         elif v in nums:
#             score = int(v)

#     print('total',total)
#     # print('tmp',tmp)
#     # print('score',score)
#     # print('*'*30)

# print(total+tmp)