from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

label1 = Label(root, text = '안녕하세요')
label1.pack()

photo = PhotoImage(file = 'Nadocoding_Python/Nadocoding_GUI/check.png')
label2 = Label(root, image = photo)
label2.pack()

def change():
    label1.config(text='또 만나요')  # 클릭을 하면 또 만나요라고 글자가 나타나게 됨

    global photo2  # 전역 변수로 선언을 해주어야함
    photo2 = PhotoImage(file = 'Nadocoding_Python/Nadocoding_GUI/X.png')
    label2.config(image = photo2)



btn1 = Button(root, text='클릭', command=change)
btn1.pack()





root.mainloop()   # 창이 닫히지 않게 해주는 것