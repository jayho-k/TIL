def dfs(d,com,word,full):
    
    if d==5:
        print(com)
        return
    
    for i in range(5):
        # dfs(d+1,com,word,full)
        dfs(d+1,com+full[i],word,full)

full = ['A','E','I','O','U']
word ='asdf'
dfs(0,'',word,full)
