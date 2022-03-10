x , y = map(int, input().split())

num = int(input())

garo = [0, x]
sero = [0, y]

for i in range(num):

    direc, cut_location = map(int, input().split())

    if direc == 0:
        # 세로끼리 비교
        sero.append(cut_location)

    else:
        # 가로끼리 비교
        garo.append(cut_location)

garo.sort()
sero.sort()

# print(garo)
# print(sero)

mx_g_cm = 0
for i in range(len(garo)-1):
    g_cm = garo[i+1] - garo[i]

    if mx_g_cm < g_cm:
        mx_g_cm = g_cm

# print(mx_g_cm)

mx_s_cm = 0
for i in range(len(sero)-1):
    s_cm = sero[i+1] - sero[i]

    if mx_s_cm < s_cm:
        mx_s_cm = s_cm

# print(mx_s_cm)

print(mx_s_cm * mx_g_cm)