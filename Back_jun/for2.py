
#1 a, b를 여러번 받기
N = int(input())

for i in range(N):
    A, B = map(int, input().split())
    print('Case{}: {}'.format(i+1, A+B))

#2 * 여러게 출력하기 왼쪽 오른쪽
n = int(input())
for i in range(n):
    i = i+1
    print( '*' * i)

n = int(input())
for i in range(n):
    i = i+1
    s = '*' * i
    print(str(s).rjust(5))

# 3. N개를 받아서 N개 수만큼 input 한번에 받기 --> list(map(int, input()))으로 한번에 받았음
#    그리고 X보다 작은수 뽑아내기
N, max = map(int, input().split())
data = list(map(int, input().split()))
new_data = []
for i in range(N):
    if data[i] < max:
        new_data.append(str(data[i]))

new_data2 = ' '.join(new_data)
print(new_data2)
