from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

# 여러개 중에 하나를 고르는 것

Label(root, text = '메뉴를 선택하세요').pack()

burger_var = IntVar()
btn_burger1 = Radiobutton(root, text = '햄버거', value=1, variable=burger_var)
btn_burger2 = Radiobutton(root, text = '치즈햄버거', value=2, variable=burger_var)
btn_burger3 = Radiobutton(root, text = '치킨햄버거', value=3, variable=burger_var)

btn_burger1.pack()
btn_burger2.pack()
btn_burger3.pack()

Label(root, text = '음료 선택').pack()


drink_var = StringVar()  # 문자로 적었기 때문에
btn_drink1 = Radiobutton(root, text = '콜라', value='콜라', variable=drink_var)
btn_drink1.select() # 기본값 선택
btn_drink2 = Radiobutton(root, text = '사이다', value='사이다', variable=drink_var)

btn_drink1.pack()
btn_drink2.pack()

def btncmd():
    print(burger_var.get())  # 버거 중에서 선택된 라디오 항목의 값을 출력
    print(drink_var.get())
    




btn = Button(root, text='주문', command=btncmd)
btn.pack()



root.mainloop()   # 창이 닫히지 않게 해주는 것
