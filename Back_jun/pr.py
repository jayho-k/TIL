
# def BubbleSort(a, n): # 정렬할 배열과 배열의 크기 
#     for i in range(n-1, 0, -1): # 정렬될 구간의 끝 # 만약 반대면 (0, n-1)
#         for j in range(0,i): # 비교할 원소 중 왼쪽 원소릐 인덱스
#             if a[j] > a[j+1]: # 왼쪽 원소가 더 크면
#                 a[j], a[j+1] = a[j+1], a[j] # 오른쪽 원소와 교환

#     return a

# arr = [43,2,4,1,2,32,3,4,1,5,21]

# # print(len(arr))

# print(BubbleSort(arr,len(arr)))


# counting sort
# n과k가 너무 떨어져 있다면 비효율적
# 따라서 이때는 사용하지 않는다



def counting_sort(arr, k):

    c_arr = [0] * (k+1) # 0부터 시작하기 때문에 +1을 더 해줘야한다.

    for i in arr:
        c_arr[i] += 1


    # 누적 카운츠를 만들어주는 과정
    for i in range(1, len(c_arr)):
        c_arr[i] += c_arr[i-1] 
        # counting_arr[i] = counting_arr[i] + counting_arr[i-1]
        # 나 자신이랑 그 전꺼 더해줘라는 뜻이다.


    result = [-1] * len(arr) # -1이 있으면 실패한거야 라는 뜻이기 때문에 -1울 넣어줌

    # for i in range(len(result)-1, -1, -1):  #0까지이기 때문에 -1
    #     c_arr[arr[i]] -= 1 # 원래값을 가져와서 
    #     result[c_arr[arr[i]]] = arr[i]
    #     print(result)

        # result[c_arr[arr[i]]- 1] = arr[i] 4번째야 라고 말하는 것
    print(c_arr)
    for i in arr:
        c_arr[i] -= 1  # 여기 이미 -1한 값이 들어가는 것임
        result[c_arr[i]] = i
        print(result)
    print(c_arr)
    return result
# i=1 => 1 => result[1] = 1

arr = [1,5,342,4,32,4,32,4,6,3]
print(counting_sort(arr, max(arr)))
    