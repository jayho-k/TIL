from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

Label(root, text= '메뉴를 선택해 주세요').pack(side= 'top')

Button(root, text = '주문하기').pack(side = 'bottom')




frame_burger = Frame(root, relief = 'solid', bd= 1)
frame_burger.pack(side = 'left', fill = 'both', expand = True)

Button(frame_burger, text = '헴버거').pack()
Button(frame_burger, text = '치즈버거').pack()
Button(frame_burger, text = '치킨버거').pack()

frame_drink = LabelFrame(root, text = '음료')
frame_drink.pack(side = 'right', fill = 'both', expand = True)

Button(frame_drink, text = '콜라').pack()
Button(frame_drink, text = '사이다').pack()

root.mainloop()   # 창이 닫히지 않게 해주는 것
