'''
8 2
1 2 3 4 5 6 7 8

'''

n,k = map(int,input().split())

lst = list(map(int,input().split()))


if n == 1:
    if lst[0]%2:
        ans = 0
    else:
        ans = 1

else:

    # initialization
    st = 0
    end = 1
    odd_num = 0
    even_mx = 0

    if lst[st]%2==1:
        odd_num+=1
    else:
        even_mx += 1


    if lst[end]%2==1:
        odd_num+=1
    else:
        even_mx += 1

    mx = even_mx
    while end != len(lst)-1:
        
        if odd_num > k:
            if lst[st]%2:
                odd_num -= 1
            else:
                even_mx -= 1
            
            st += 1

        else:
            end+= 1

            if lst[end]%2==0:
                even_mx += 1
                mx = max(mx, even_mx)
            else:
                odd_num += 1
    ans = mx

print(ans)


