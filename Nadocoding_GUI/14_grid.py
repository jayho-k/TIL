from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

# btn1 = Button(root, text = 'button1')
# btn2 = Button(root, text = 'button2')

# # btn1.pack(side = 'left')
# # btn2.pack(side = 'left')

# btn1.grid(row = 0, column = 0)
# btn2.grid(row = 1, column = 1)

# 계산기 모양 만들기
# 맨 윗줄
btn_f16 = Button(root, text = 'F16', width = 5, height = 2)  # 버튼에서 padx pady를 사용하면 버튼 자체가 커진다.
btn_f17 = Button(root, text = 'F17', width = 5, height = 2)
btn_f18 = Button(root, text = 'F18', width = 5, height = 2)
btn_f19 = Button(root, text = 'F19', width = 5, height = 2)

btn_f16.grid(row = 0, column = 0, sticky = N+E+W+S, padx=3, pady=3) #sticky는 동서남북으로 다 붙여라 라는 뜻  # 동서남북 news 
btn_f17.grid(row = 0, column = 1, sticky = N+E+W+S, padx=3, pady=3) # 그리드에서 padx pady를 사용하면 그리드 끼리 간격을 넓힌다.
btn_f18.grid(row = 0, column = 2, sticky = N+E+W+S, padx=3, pady=3)
btn_f19.grid(row = 0, column = 3, sticky = N+E+W+S, padx=3, pady=3)

# 두번째 줄
btn_clear = Button(root, text = 'clear', width = 5, height = 2)
btn_equal = Button(root, text = '=', width = 5, height = 2)
btn_div = Button(root, text = '/', width = 5, height = 2)
btn_mul = Button(root, text = '*', width = 5, height = 2)

btn_clear.grid(row = 1, column = 0, sticky = N+E+W+S, padx=3, pady=3)
btn_equal.grid(row = 1, column = 1, sticky = N+E+W+S, padx=3, pady=3)
btn_div.grid(row = 1, column = 2, sticky = N+E+W+S, padx=3, pady=3)
btn_mul.grid(row = 1, column = 3, sticky = N+E+W+S, padx=3, pady=3)

# 3번재
btn_7 = Button(root, text = '7', width = 5, height = 2)
btn_8 = Button(root, text = '8', width = 5, height = 2)
btn_9 = Button(root, text = '9',  width = 5, height = 2)
btn_sub = Button(root, text = '-', width = 5, height = 2)

btn_7.grid(row = 2, column = 0, sticky = N+E+W+S, padx=3, pady=3)
btn_8.grid(row = 2, column = 1, sticky = N+E+W+S, padx=3, pady=3)
btn_9.grid(row = 2, column = 2, sticky = N+E+W+S, padx=3, pady=3)
btn_sub.grid(row = 2, column = 3, sticky = N+E+W+S, padx=3, pady=3)

# 4번째
btn_4 = Button(root, text = '4', width = 5, height = 2)
btn_5 = Button(root, text = '5', width = 5, height = 2)
btn_6 = Button(root, text = '6', width = 5, height = 2)
btn_add = Button(root, text = '+', width = 5, height = 2)

btn_4.grid(row = 3, column = 0, sticky = N+E+W+S, padx=3, pady=3)
btn_5.grid(row = 3, column = 1, sticky = N+E+W+S, padx=3, pady=3)
btn_6.grid(row = 3, column = 2, sticky = N+E+W+S, padx=3, pady=3)
btn_add.grid(row = 3, column = 3, sticky = N+E+W+S, padx=3, pady=3)

# 5번째
btn_1 = Button(root, text = '1', width = 5, height = 2)
btn_2 = Button(root, text = '2', width = 5, height = 2)
btn_3 = Button(root, text = '3', width = 5, height = 2)
btn_enter = Button(root, text = 'enter', width = 5, height = 2)

btn_1.grid(row = 4, column = 0, sticky = N+E+W+S, padx=3, pady=3)
btn_2.grid(row = 4, column = 1, sticky = N+E+W+S, padx=3, pady=3)
btn_3.grid(row = 4, column = 2, sticky = N+E+W+S, padx=3, pady=3)
btn_enter.grid(row = 4, column = 3, rowspan=2, sticky = N+E+W+S, padx=3, pady=3)  # rowspan은 row 현재 위치에서 아래쪽으로 더함 

# 6번째
btn_0 = Button(root, text = '0', width = 5, height = 2)
btn_point = Button(root, text = '.', width = 5, height = 2)

btn_0.grid(row = 5, column = 0, columnspan = 2, sticky = N+E+W+S, padx=3, pady=3) # columnspan 은 오른쪽으로 2칸
btn_point.grid(row = 5, column = 2, sticky = N+E+W+S, padx=3, pady=3)



root.mainloop()   # 창이 닫히지 않게 해주는 것
