'''

두번쨰
1. 0번을 뽑으면 그자리에 그대로
2. 1번을 뽑으면 앞에 있는 학생의 앞으로 간다

3번째
뽑은 번호만큼 앞자리로 간다
[1,2,3]

1. 0 = 그대로
2. 1 = 1번자리로
3. 2 = 0번자리로
'''

st = int(input())
st_lst = list(range(1,st+1))
num_lst = list(map(int, input().split()))
lst = []

for i in range(len(st_lst)):
    stu_lo = len(lst) - num_lst[i]
    lst.insert(stu_lo, st_lst[i])

print(' '.join(map(str,lst)))
