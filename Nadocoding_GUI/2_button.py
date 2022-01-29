from tkinter import*

root =Tk()
root.title('Nadp GUI')

btn1 = Button(root, text='버튼1')
btn1.pack()

btn2 = Button(root, padx=5, pady=10, text='버튼2')  # 버튼 크기 padx 가로 pady세로  내용이 많아지면 너비가 넓어짐
btn2.pack()

btn3 = Button(root, padx=10, pady=5, text='버튼3')
btn3.pack()

btn4 = Button(root, width=10, height=3, text='버튼4') # 아예 크기를 정해버리는 경우 따라서 크기가 고정됨 
btn4.pack()

btn5 = Button(root, fg='red', bg='yellow', text='버튼5')
btn5.pack()

photo = PhotoImage(file ="Nadocoding_Python/Nadocoding_GUI/check.png")

btn6 = Button(root, image = photo)
btn6.pack()

# 버튼 동작만들기

def btncmd():
    print('버튼이 클릭되었어요')

btn7 = Button(root, text='동작하는 버튼', command=btncmd)
btn7.pack()

root.mainloop()   # 창이 닫히지 않게 해주는 것