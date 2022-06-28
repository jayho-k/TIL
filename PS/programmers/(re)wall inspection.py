'''

12	[1, 5, 6, 10]	[1, 2, 3, 4]	2
12	[1, 3, 4, 9, 10]	[3, 5, 7]	1
'''


# n = 12
# weak = [1, 5, 6, 10]
# dist = [1, 2, 3, 4]


n = 12
weak = [1, 5, 6, 10]
dist = [1, 2, 3, 4]



def tmp():
    person = 0
    cnt = 0
    st = weak[-1] -n
    # print(st)
    for di in ndist:
        for i in range(di):
            if arr[-i+st] == 1:
                cnt -= 1
        
            if -cnt == len(weak):
                print(person)
                return person

        person += 1
        st = weak[cnt-1]-n


ndist = sorted(dist, reverse=True)
arr = [0]*12

for w in weak:
    arr[w] = 1

ans = tmp()
if ans==None:
    answer = -1
else:
    answer = ans

