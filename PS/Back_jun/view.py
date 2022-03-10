'''
1. 오른쪽 왼쪽 둘다 두칸이 자신보다 작아야함
2. 즉 5칸씩 계속 비교를 해주면 된다

2 시야확보
2-1 자신보다 큰 수가 있을때 까지 찾아
2-2 자신보다 큰 수가 있으면 그거 빼고 나머지들중에서
    가장 큰수와 뺀다
2-3 

100
0 0 225 214 82 73 241 233 179 219 135 62 36 13 6 71 179 77 67 139 31 90 9 37 93 203 150 69 19 137 28 174 32 80 64 54 18 0 158 73 173 20 0 102 107 48 50 161 246 145 225 31 0 153 185 157 44 126 153 233 0 201 83 103 191 0 45 0 131 87 97 105 97 209 157 22 0 29 132 74 2 232 44 203 0 51 0 244 212 212 89 53 50 244 207 144 72 143 0 0 

'''

n = int(input())
x = list(map(int, input().split()))
lst = []

mx1 = []
mx2 = []

shrt1 = 0
for i in range(2, len(x)-1):

    if x[i] > x[i-1] and x[i] > x[i-2] and x[i] > x[i+1] and x[i] > x[i+2]:
        mx1.append(x[i-1])
        mx1.append(x[i-2])
        mx2.append(x[i+1])
        mx2.append(x[i+2])
        shmx1 = max(mx1) 
        shmx2 = max(mx2)
        # print('shmx1', shmx1)
        # print('shmx2', shmx2)
        # print('x[i]', x[i])
        # print('='* 30)

        if shmx1 >= shmx2:
            imx = x[i] - shmx1
            lst.append(imx)
            
        else:
            imx = x[i] - shmx2
            lst.append(imx)

        mx1 = []
        mx2 = []


print(sum(lst))
                


