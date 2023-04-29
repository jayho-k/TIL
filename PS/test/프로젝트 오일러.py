'''

값

'''
def play():
    ans = 1
    a_sum = 1
    for n in range(1,10000):
        st_store = set()
        st_n = n
        st_store.add(st_n)

        while 1:
            tmp = 0

            while n!=0:
                equ,rem = n//10, n%10
                tmp += (rem**2)
                n = equ

            if tmp in st_store:
                break

            elif tmp==1:
                ans+=1
                a_sum+=st_n
                break

            st_store.add(tmp)
            n=tmp
    
    return ans,a_sum

ans,a_sum = play()
print(ans*a_sum)
