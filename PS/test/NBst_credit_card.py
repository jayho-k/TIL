'''
deposit = []

500, -300, 500, 700, -1000, 500,500

ans
200,200,500,500
'''
deposit = [500, -300, 500, 700, -1000, 500,500]
stack = []

for depo in deposit:
    if depo>0:
        stack.append(depo)

    elif depo<0:
        st = stack.pop()
        tmp = st+depo
        while 1:
            if tmp>0:
                stack.append(tmp)
                break
            elif tmp==0:
                break
            st = stack.pop()
            tmp+=st
print(stack)
