# Queue

## BFS

```python
# BFS 구현

def BFS(G,v,n):
    visited = [0]*(n+1)
    q = []
    q.append(v)
    visited[v] = 1
    while q:
        tmp = q.pop(0)
        
        for i in G[tmp]:
            if not visited[i]:
                q.append(i)
                visited[i] = 1
                
```

```python
# BFS 구현

def BFS(G,v,n):
    visited = [0]*(n+1)
    q = []
    q.append(v)
    visited[v] = 1
    while q:
        tmp = q.pop(0)
        
        for i in G[tmp]:
            if not visited[i]:
                q.append(i)
                visited[i] = visited[t] + 1
                # 이런식으로 하는 이유
                # 그룹에서 얼마만큼 떨어져 있는지 알아보기 위해서
                # 그래서 그 전 그룹에서의 값(?)을 더해주게 된다
```

