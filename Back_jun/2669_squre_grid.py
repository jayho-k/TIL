# 1 2 4 4
# 2 3 5 7
# 3 1 6 5
# 7 3 8 6


area = [[0]*100 for _ in range(100)]

for _ in range(4):
    x1, y1, x2, y2 = map(int, input().split())

    for i in range(y1, y2):
        for j in range(x1, x2):
            area[i][j] = 1

sum_area = sum(sum(area, []))

print(sum_area)


