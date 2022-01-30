import time
import tkinter.ttk as ttk
from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

# progressbar = ttk.Progressbar(root, maximum = 100, mode = 'indeterminate') # 언제 끝날지 모르는 모드
# progressbar.start(10) # 10ms 마다 움직임
# progressbar.pack()

# progressbar2 = ttk.Progressbar(root, maximum = 100, mode = 'determinate') # 언제 끝날지 아는 모드
# progressbar2.start(10) # 10ms 마다 움직임
# progressbar2.pack()

# btn = Button(root, text='중지', command=btncmd2)
# btn.pack()


# def btncmd():
#     progressbar.stop()
#     progressbar2.stop()

p_var3 = DoubleVar()
progressbar3 = ttk.Progressbar(root, maximum = 100, length = 150, variable = p_var3) # 바의 길이를 길게 하고 싶을 때 length를 잡아준다. 
progressbar3.pack()

def btncmd2():
    for i in range(101):
        time.sleep(0.01) # 0.01초 대기

        p_var3.set(i) # progress
        progressbar3.update()
        print(p_var3.get())



btn = Button(root, text='시작', command=btncmd2)
btn.pack()








root.mainloop()   # 창이 닫히지 않게 해주는 것
