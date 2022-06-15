'''
20
7
23
19
10
15
25
8
13

140
40 두명

'''

total = 0
lst = []
for i in range(9):
    tmp = int(input())
    total += tmp
    lst.append(tmp)

lst.sort()
lier = total -100
strt = 0
end = len(lst)-1

while strt <= end:

    if lst[strt]+lst[end] < lier:
        strt += 1
    
    elif  lst[strt]+lst[end] > lier:
        end -= 1
    
    else:
        lst[strt]
        lst[end]
        break


for i in range(len(lst)):
    if i == strt or i == end:
        continue
    print(lst[i])





# heights = []
# answer_height = []
# for i in range(9):
#     height = int(input())
#     heights.append(height)
#     answer_height.append(height)
# # heights = [20, 7, 23, 19, 10, 15, 25, 8, 13]
# # answer_height = [20, 7, 23, 19, 10, 15, 25, 8, 13]

# test = []
# total_heights = sum(answer_height)

# for st_h in answer_height:

#     test.append(st_h)
#     heights.remove(st_h)

    
#     for add_h in heights:
#         test.append(add_h)
#         sum_height = sum(test)

#         if sum_height == total_heights - 100:
#             lier = test
#             break
#         test.remove(add_h)

#     test = []

# for i in lier:
#     answer_height.remove(i)

# answer_height.sort()

# for i in answer_height:
#     print(i)


# # 이중 for문을 이용해서 하나씩 다 더해본다
# # 하나는 고정 나머지 더함
# # 그렇게 더하고 sum - 100의 값이 나오면 두개 당첨



# heights = [20, 7, 23, 19, 10, 15, 25, 8, 13]

# test = []
# total_heights = sum(heights)

# cnt = 0
# for i in range(len(heights)):
#     cnt += 1
#     test.append(heights[i])

#     for j in range(cnt, len(heights)):
#         test.append(heights[j])
#         sum_height = sum(test)

#         if sum_height == total_heights - 100:
#             lier = test
#             print(lier)
#             break

#         test.remove(heights[j])
        
#     test = []