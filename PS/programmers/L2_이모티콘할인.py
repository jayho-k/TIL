def cal(discount,users,emoticons):
    # 1. u_dc보다 커야함, 2. u_cost
    emo_plus = 0
    sale = 0
    for u_dc,u_cost in users:
        total = 0
        for i in range(len(discount)):
            if u_dc <= discount[i]:
                total+=(emoticons[i]-(discount[i]*emoticons[i])//100)
        if total>=u_cost:
            emo_plus+=1
        else:
            sale+=total

    return (emo_plus,sale)
    

def dfs(d,n,v_lst,lst,users,emoticons):
    
    if d==n:
        ans_lst.append(cal(v_lst,users,emoticons))
        return
    
    for i in range(len(lst)):
        dfs(d+1,n,v_lst+[lst[i]],lst,users,emoticons)

def solution(users, emoticons):
    global ans_lst
    ans_lst = []
    rate = [10,20,30,40]
    dfs(0,len(emoticons),[],rate,users,emoticons)
    ans_lst.sort(key=lambda x : (-x[0],-x[1]))
    answer = list(ans_lst[0])
    return answer