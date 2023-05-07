"""
merge sort

컨셉 => 분할정복
[4,3,7,1,2,8,5,6]

divide
4,3,7,1 / 2,8,5,6
4,3 / 7,1 / 2,8 / 5,6
4 / 3 / 7 / 1 / 2 / 8 / 5 / 6

combine
3,4 / 1,7 / 2,8 / 5,6
1,3,4,7 / 2,5,6,8
1,2,3,4,5,6,7,8

"""

def merge_sort(lst):
    
    if len(lst)<=1:
        return lst
    
    mid = len(lst)//2
    left = merge_sort(lst[:mid])
    right = merge_sort(lst[mid:])
    merged = merge(left,right)
    
    return merged

def merge(lst1, lst2):
    
    merged = []

    # lst의 값이 존재한다면
    while len(lst1)>0 and len(lst2)>0:
        if lst1[0] <= lst2[0]:
            merged.append(lst1.pop(0))
        else:
            merged.append(lst2.pop(0))

    # 하나는 0이 되었지만 나머지 하나는 0이 아닐 것
    if len(lst1)>0:
        merged += lst1
    
    if len(lst2)>0:
        merged += lst2
    
    return merged




# # 최적화
# def merge_sort(l,r):

#     if l<r:
#         mid = (l+r)//2

#         # divide
#         merge_sort(l,mid)
#         merge_sort(mid+1,r)

#         # conquer, combine
#         tmp = []

#         # 나눴던 두 리스트의 시작 인덱스
#         ls = l
#         rs = mid+1

#         # compare
#         # 0,1 / 2,3 / 4,5 / 6,7
#         # 0,1,2,3 / 4,5,6,7
#         # 0,1,2,3,4,5,6,7
#         while ls<=mid and rs<=r:
#             if arr[ls] < arr[rs]:
#                 tmp.append(arr[ls])
#                 ls+=1
#             else:
#                 tmp.append(arr[rs])
#                 rs+=1
        
#         if ls <=mid:
#             tmp = tmp+arr[ls:mid+1]
#         else:
#             tmp = tmp+arr[rs:r+1]
        
#         for i in range(l,r+1):
#             arr[i] = tmp[i-l]


if __name__ == "__main__":
    arr = [4,3,7,1,2,8,5,6]
    print('정렬 전 : ', arr)
    arr = merge_sort(arr)
    # merge_sort(0,7)
    print()
    print('정렬 후 : ', arr)