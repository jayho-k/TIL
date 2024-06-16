"""
3 6
antarctica
antahellotica
antacartica

숫자를 앞에부터 세다가 숫자보다 넘어가면 

1. 가운데만 읽는다
2. a,n,t,i,c 는 무조건 포함된다. => 5개 / 즉 k는 5개 이상이어야한다.
3. 가장 긴 단어는 15이다. 15-8 = 7
    즉 7개의 알파벳이 다르면서 8 (5개의 알파벳)개의 포함되지 않는다면
    12개의 알파벳을 안다면 모든 단어를 다 알 수 있음


n,k

if k가 5개 이상일 경우 진행
    dic = {단어 : cnt, }

    for 문
        length
        constCnt = k - 5
        dic = {알파벳, 개수} => a,n,t,i,c 1씩

        input
            - 단어의 개수 파악
            - k >= 5 + len(단어) - 8
                k>=len(단어)-3 => 합격

                
        [함수]
        for (4~길이-5):
            
            if (dic[알파벳] 0인 경우):
                cnt -= 1
                dic[알파벳] += 1
                cnt가 0보다 밑인지 확인
                    만약 0보다 밑이면 실패

        else:
            끝까지 갔어! => 성공
            
else:
    0개

1 6
antacartica

"""


# def play():

#     passCnt = 0

#     for _ in range(n):

#         alpha_dup = set(['a','n','t','i','c'])

#         pass_fail_flag = 1
#         length = 0
#         cnt = k-5

#         st = input()

#         length = len(st)

#         if k>=length-3:
#             passCnt += 1
#             continue

#         for i in range(4,length-5):
#             if (st[i] not in alpha_dup):
#                 cnt -= 1
#                 alpha_dup.add(st[i])
#                 if cnt < 0:
#                     pass_fail_flag = 0
#                     break
        
#         # 끝까지 갔으면 pass_fail_flag 이 1임
#         if pass_fail_flag:
#             print("pass")
#             passCnt+=1

#     return passCnt


import string
import sys

sys.setrecursionlimit(10000)

alpha = []
check_alpha = set(['a','n','t','i','c'])

for al in string.ascii_lowercase:
    if al in check_alpha:
        continue
    alpha.append(al)

def dp(m,r,st):

    if m==len(alpha):
        if len(st) == r:
            for s in st:
                pass

            print(st)
        return

    st += alpha[m]
    dp(m+1,r,st)

    st = st[:-1]
    dp(m+1,r,st)


n,k = input().split()
n,k = int(n),int(k)

word_lst = []
for _ in range(n):
    word = input()
    tmp = ''
    for i in range(4,len(word)-4):
        if word[i] in check_alpha:
            continue
        tmp+=word[i]

    word_lst.append(set(tmp))

# dp(0,k-5,'')



# def play():




#     return 0

# def can_not_play():
#     for _ in range(n):
#         input()
#     return 0

# n,k = input().split()
# n,k = int(n),int(k)

# if (k>=5):
#     print(play())

# else:
#     print(can_not_play())
    





