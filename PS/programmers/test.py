
from pprint import pprint
dic = {
    "A" : set(),
    "E" : set(),
    "I" : set(),
    "O" : set(),
    "U" : set()
}

def dfs(d,com,word,full):
    if d==5:
        if len(com)>0:
            dic[com[0]].add(com)
        return
    
    for i in range(5):
        dfs(d+1,com,word,full)
        dfs(d+1,com+full[i],word,full)


full = [ 'A', 'E', 'I', 'O', 'U']
word ='asdf'
dfs(0,'',word,full)
for f in full:
    dic[f] = [sorted(list(dic[f])),len(dic[f])]

print(dic["E"])



