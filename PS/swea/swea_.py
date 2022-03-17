'''
5 3 2
4 1
5 2
3 3
'''




# def d(r,l):




#     pass



T = 1
for tc in range(1,T+1):
    # n = 총 노드 개수, m = 리프노드의 개수, l출력할 노드
    n, m, l = map(int, input().split())
    l_nodes = [list(map(int, input().split())) for _ in range(m)]
    tree = [0]*(n+1)

    l_nodes.sort(reverse=True)
    for l_node in l_nodes:
        l_n, l_v = l_node
        tree[l_n] = l_v
    
    print(tree)
    ntree = len(tree)
    p_loc = ntree//2
    for i in range(-1,-ntree,-2):
        cr = tree[i]
        cl = tree[i-1]
        p = cr + cl
        tree[p_loc] = p
        
        


        print(i)



    
    # while 1:
    #     ch1_v = tree[-2]
    #     ch2_v = tree[-1]
    #     p_v = ch1_v + ch2_v
        
    #     p = ntree//2
    #     tree[p] = p_v



    
