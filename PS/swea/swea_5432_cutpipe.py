'''

2
()(((()())(())()))(())
(((()(()()))(())()))(()())

1
(()())
'''

for tc in range(1,int(input())+1):
    pipe = input()
    cnt = 0
    pipe_cnt = 0
    for i in range(len(pipe)):
        if pipe[i]=='(':
            cnt+=1

        else:
            if pipe[i-1]=='(':
                cnt-=1
                pipe_cnt+=cnt

            elif pipe[i-1]==')':
                cnt-=1
                pipe_cnt+=1

    print(f'#{tc}',pipe_cnt)
