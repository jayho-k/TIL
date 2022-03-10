

T = int(input())
for tc in range(1, T+1):
    n = int(input())
    grid = [[0]*10 for _ in range(10)]
    for _ in range(n):
        x1, y1, x2, y2, col = map(int, input().split())

        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                if col == 1:
                    grid[y][x] += 10
                else:
                    grid[y][x] += 1

    lst = sum(grid, [])
    cnt = 0
    for r in lst:
        red, blu = divmod(r, 10)

        if red > 0 and blu > 0:
            cnt += 1

    print(f'#{tc} {cnt}')