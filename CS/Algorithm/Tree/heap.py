'''
최대 100개의 정수
최대 힙
'''
def enq(n):
    global last
    last +=1
    tree[last] = n # 완전 이진트리 유지
    c = last # 새로 추가된 자식
    p = c//2 # 그 자식의 부모
    
    while p>=1 and tree[p] < tree[c]: #부모가 있고, 자식의 키값이 더 크면 교환
        tree[p] , tree[c] = tree[c], tree[p]
        c = p
        p = c//2

def deq():
    global last
    tmp = tree[1]
    tree[1] = tree[last] # 마지막 값을 루트에 복사
    last -= 1 # 마지막 정점 삭제
    
    # 부모>자식 규칙유지
    p = 1
    c = p*2
    while c<= last: # 왼쪽 자식이 있으면
        
        if c+1<=last and tree[c] < tree[c+1]: # 오른쪽 자식노드도 있고 더크면
            c+= 1 # 그럼 오른쪽을 기준으로 할 것임
        
        if tree[p] < tree[c]: # 자식의 키값이 더 크면 교환
            tree[p],tree[c] = tree[c], tree[p]
            p = c
            c = p*2

        else:
            break
    
    return tmp



# 포화이진트리의 정점번호
tree = [0]*(101)
last = 0
