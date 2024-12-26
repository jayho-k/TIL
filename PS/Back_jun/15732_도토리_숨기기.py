"""

200 2 5
100 150 10
110 150 15

200 2 2
100 150 10
110 150 15

"""

def calculate(mid):
    calculatedNum = 0
    for box in boxList:
        boxStart, boxEnd, jump = box

        if boxStart <= mid:
            if boxEnd < mid:
                calculatedNum+=((boxEnd-boxStart)//jump)+1
            else:
                calculatedNum+=((mid-boxStart)//jump)+1
    #print(calculatedNum)
    return calculatedNum >= d


def biSearch(target,total):

    start, end = 1, total
    while start < end:
        mid = (start + end)//2

        if calculate(mid):
            #print("calculate(mid) < target:",start,mid,end)
            end = mid
        else:
            start = mid + 1
            #print("calculate(mid) > target:",start,mid,end)
            

    #print(start,mid,end)


    #print(start,mid,end)
    return end


n,k,d = map(int,input().split())

boxList = [tuple(map(int,input().split())) for _ in range(k)]


print(biSearch(d,n))



    # minValue = 1e9
    # ansValue = -1
    # for box in boxList:
    #     boxStart, boxEnd, jump = box
    #     x = boxStart
    #     while True:

    #         if minValue >= (mid - x):
    #             minValue = (mid - x)
    #             ansValue = x

    #         x += jump
    #         if x > boxEnd or x > mid:
    #             break
