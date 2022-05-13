'''
조건 1.
무게제한, 2명

조건 2.



[70, 50, 80, 50]	100	3
[70, 80, 50]	100	3

'''

   

people = [70, 50, 80, 50]
limit = 0

n = len(people)
people.sort()

s = 0
e = n-1

cnt = 0
while s <= e:

    cnt += 1
    if people[s] + people[e] <= limit:
        s += 1
    e -= 1



