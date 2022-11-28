n = int(input())
lst = [int(input()) for _ in range(n)]
lst.sort(reverse=True)

mx = 0
for i in range(len(lst)):
    mx = max(mx, lst[i]*(i+1))
print(mx)


