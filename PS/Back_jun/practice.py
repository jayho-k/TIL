'''
5
5 50 50 70 80 100
7 100 95 90 80 70 60 50
3 70 90 80
3 70 90 81
9 100 99 98 97 96 95 94 93 91
'''



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


