


def rotateRight(self, z):

    if z == None:
        return
    x = z.left
    if x == None:
        return
    b = x.right # 이부분을 조금더 이해할 필요가 있음  # 1

    #2
    x.parent = z.parent
    if z.parent != None:
        if z.parent.left == z:
            z.parent.left = x
        else:
            z.parent.right = x
    #3
    x.right = z
    #4
    z.parent = x
    z.left = b
    if b != None:
        b.parent = z

    if self.root == z:
        self.root = x