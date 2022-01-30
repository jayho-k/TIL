from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

chkvar = IntVar() #  체크바에 인트형으로 값을 저장한다.
chkbox = Checkbutton(root, text = '오늘 하루 보지 않기', variable = chkvar)
# chkbox.select() # 자동으로 체크표시 되는 것
chkbox.pack()

chkvar2 = IntVar()
chkbox2 = Checkbutton(root, text = '일주일동안 하루 보지 않기', variable = chkvar2)
chkbox2.pack()

def btncmd():
    print(chkvar.get()) # 0일때 체크 헤제 / 1일때 체크
    print(chkvar2.get())



btn = Button(root, text='클릭', command=btncmd)
btn.pack()



root.mainloop()   # 창이 닫히지 않게 해주는 것
