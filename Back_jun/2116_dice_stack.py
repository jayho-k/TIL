def route():
    pass


num = int(input())

dices = []
for i in range(num):
    d = list(map(int, input().split()))
    dices.append(d)

# 경로 계산
dice = dices[0]

lst1 = [dice[0], dice[-1]]
lst2 = []
lst3 = []
lst4 = []
lst5 = []
lst6 = []
for dice in dices:
    f = 0
    b = -1
    for i in range(len(dice)-4):

        lst1.append(dice[f])
        lst1.append(dice[b])

        f += 1
        b -= 1

    


# lsttest = [2, 3, 1, 6, 5, 4]

# print(lsttest[0])         #2
# print(lsttest.index(2))   #0