'''
필요한 


'''

n, cls = map(int,input().split())


grads= [1,2,3,4,5,6]
rm_m = [0,0,0,0,0,0]
rm_w = [0,0,0,0,0,0]

cnt = 0
for _ in range(n):
    
    s, y = map(int,input().split())

    if s == 0: # 여
        for i in range(len(grads)):
            if grads[i] == y:

                if rm_w[i] == 0:
                    cnt += 1
                rm_w[i] += 1
                
                if rm_w[i] == cls:
                    rm_w[i] = 0
                    
    else: # 남
        for i in range(len(grads)):
            if grads[i] == y:

                if rm_m[i] == 0:
                    cnt += 1
                rm_m[i] += 1

                if rm_m[i] == cls:
                    rm_m[i] = 0
                    
    
print(cnt)


