'''
3
9
2 1 4 3 5 6 2 7 2

3
12
1 2 3 2 3 1 4 1 1 2 3 4

'''

case = int(input())
n = int(input())
lst = list(map(int,input().split()))

# 추천, 시간
stu = [[0,0] for _ in range(101)]

can_num = []
for s in lst:

    # 후보개수 올리기
    if s not in can_num:
        can_num.append(s)

    # 사진틀 부족
    if len(can_num)  == case+1:

        # 후보중 작은 값 찾기
        mn = 1e9
        for m in range(101):
            if mn>stu[m][0] and stu[m][0] != 0:
                mn = stu[m][0]

        # remove list (2명 이상일 수 있어서)
        rmv_lst =[]
        for j in range(101):
            if stu[j][0] == mn:
                rmv_lst.append(j)

        # 2명 이상? ==> 오래된 애들을 찾는다
        old = 0
        old_i = 0
        if len(rmv_lst) >= 2:
            for r in rmv_lst:
                if old < stu[r][1]:
                    old = stu[r][1]
                    old_i = r
        else:
            old_i = rmv_lst[0]

        # 삭제
        stu[old_i] = [0,0]
        can_num.remove(old_i)

    # 후보 올리기
    stu[s][0] += 1

    # 시간 재기
    for i in range(101):
        if stu[i][0] != 0:
            stu[i][1] += 1

ans = []
for a in range(101):
    if stu[a] != [0,0]:
        ans.append(a)

# print(stu)
print(*ans)
