'''
123402

7755
'''

n = list(map(int,input()))

nn = len(n)
n2 = nn//2

div1 = []
div2 = []

# for i in range(nn):
#     if i <n2:
#         div1.append(n[i])
#     else:
#         div1.append(n[i])

div1 = n[:n2]
div2 = n[n2:]


sm1 = sum(div1)
sm2 = sum(div2)

if sm1 == sm2:
    print('LUCKY')
else:
    print('READY')




