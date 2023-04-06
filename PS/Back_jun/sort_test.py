

lst = [3,7,9,1,4,3,12,3,12,3,12,3,12,2,2,23,3]
# lst.sort()
# print(lst)
mx = 0
for i in range(len(lst)):
    if mx < lst[i]:
        mx = lst[i]
table = [0]*(mx+1)

for j in range(len(lst)):
    idx = lst[j]
    table[idx]+=1

sort_lst = [0]*len(lst)

loc = 0
for num in range(len(table)):
    while table[num]:
        sort_lst[loc]=num
        loc+=1
        table[num]-=1
 
print(sort_lst)
print(sorted(lst))
