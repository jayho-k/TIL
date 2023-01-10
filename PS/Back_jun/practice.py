'''
2
superaquatornado
2
abcdefghijklmnopqrstuvwxyz
5
'''

# # 4659번 비밀번호 발음하기
# def is_right(word):
#     Nothing = True
#     vowel_cnt = 0
#     cons_cnt = 0
#     j = 1
#     for i in range(len(word)):
#         # 1
#         if word[i] in vowel:
#             Nothing = False
#             vowel_cnt+=1
#             cons_cnt = 0        
#         else:
#             vowel_cnt=0
#             cons_cnt+=1
#         # 2
#         if vowel_cnt>=3 or cons_cnt>=3:
#             return False

#         # 3
#         if i != len(word)-1:
#             if word[i]==word[j] and word[i]!='e' and word[i]!='o':
#                 return False
#             j+=1

#     if Nothing:
#         return False
    
#     return True


# vowel = set(['a','e','i','o','u'])
# # consonant = set([bcdfghjklnmpqrstvwxyz])

# while True:
#     word = input()
#     if word == 'end':
#         break
#     if is_right(word):
#         print(f'<{word}> is acceptable.')
#     else:
#         print(f'<{word}> is not acceptable.')
        

# def is_group(first,sp):
#     tmp = set()
#     tmp.add(first)
#     for i in range(1,len(sp)):
#         if sp[i]==sp[i-1]:
#             continue
#         if sp[i] in tmp:
#             return False
#         tmp.add(sp[i])

#     return True

# cnt = 0
# n = int(input())
# for _ in range(n):
#     sp = input()
#     first = sp[0]
#     if len(sp)==1:
#         cnt+=1
#         continue
#     if is_group(first,sp):
#         cnt += 1
# print(cnt)



# # 16171_나는 친구가 적다 (Small)
# nums = set()
# for i in range(10):
#     nums.add(str(i))
# sp = input()
# comp = input()
# new_sp = ''
# for j in range(len(sp)):
#     if sp[j] in nums:
#         continue
#     new_sp+=sp[j]
# if comp in new_sp:
#     print(1)
# else:
#     print(0)


# # 20154 이 구역의 승자는 누구야?!
# ans = {
#     0:"You're the winner?",
#     1:"I'm a winner!"
# }
# board ={}
# alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# nums = [3,2,1,2,3,3,3,3,1,1,3,1,3,3,1,2,2,2,1,2,1,1,2,2,2,1]
# for i in range(len(alph)):
#     board[alph[i]]=nums[i]
# total = 0
# sp = input()
# for s in sp:
#     total += board[s]
# print(ans[total%2])


# def caculate(mode,compare):
#     lst = []
#     for i in range(0,len(compare),2):
#         if mode == 'start':
#             tmpNo = board[compare[i]]+board[compare[i+1]]
#         else:
#             tmpNo = compare[i]+compare[i+1]

#         if tmpNo>10:
#             tmpNo%=10
#         lst.append(tmpNo)
#     return lst


# ans = {
#     0:"You're the winner?",
#     1:"I'm a winner!"
# }
# board ={}
# alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# nums = [3,2,1,2,3,3,3,3,1,1,3,1,3,3,1,2,2,2,1,2,1,1,2,2,2,1]
# for i in range(len(alph)):
#     board[alph[i]]=nums[i]
# sp = input()
# n = len(sp)
# if n%2:
#     spTmp = sp[-1]
#     game = caculate('start',sp[:-1])
#     game.append(board[spTmp])
#     n = len(game)
# else:
#     game = caculate('start',sp)
#     n = len(game)

# while 1:
#     if n <= 2:
#         # print(game)
#         break

#     if n%2:
#         numTmp = game[-1]
#         game = caculate('others',game[:-1])
#         game.append(numTmp)
#         n = len(game)
#     else:
#         game = caculate('others',game)
#         n = len(game)

# print(ans[sum(game)%2])


# # 10798 세로 읽기
# board = [list(input()) for _ in range(5)]
# ans = ''
# for x in range(15):
#     for y in range(5):
#         if len(board[y])<=x:
#             continue
#         ans+=board[y][x]
# print(ans)


# # 4344
# T = int(input())
# for _ in range(1,T+1):
#     n,*lst = map(int,input().split())
#     avg = sum(lst)/n
#     total = 0
#     for i in range(n):
#         if lst[i]>avg:
#             total+=1
#     print("{:.3f}%".format(total/n*100))



# # 3029_경고

# ch,cm,cs = map(int,input().split(':'))
# bh,bm,bs = map(int,input().split(':'))
# t1 = ch*3600+cm*60+cs
# t2 = bh*3600+bm*60+bs
# if t1==t2:
#     print('24:00:00')
# else:
#     lst = []
#     if t1>t2:
#         t=(t2-t1)+(24*3600)
#     else:
#         t=(t2-t1)
#     lst.append(t//3600)
#     lst.append((t//60)%60)
#     lst.append(t%60)

#     ans = ''
#     for i in range(3):
#         if lst[i]<10:
#             ans+='0'+str(lst[i])
#         else:
#             ans+= str(lst[i])
#         if i<2:
#             ans+=':'
#     print(ans)




# 11365_!밀비 급일
# while 1:
#     sp = input()
#     if sp == 'END':
#         break
#     print(''.join(reversed(list(sp))))
    
# def flip(sp):
#     tmp = ''
#     for s in sp:
#         tmp = s+tmp
#     return tmp

# while 1:
#     sp = input()
#     if sp == 'END':
#         break
#     print(flip(sp))


