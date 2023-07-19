from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'index.html')

def greeting(request):

    context ={
        'name':'Alice'
    }
    return render(request, 'greeting.html', context)

def foods(request):

    food_lst = ['chicken', 'hamberger', 'soup', 'taco']
    context ={
        'food_lst':food_lst
    }
    return render(request, 'foods.html', context)

def throw(request):
    return render(request, 'throw.html')

def catch(request):
    message = request.GET.get('message')
    context = {
        'message':message
    }

    return render(request, 'catch.html', context)

def hello(request, name, age):
    context = {
        'name': name,
        'age': age,
    }
    return render(request, 'hello.html', context)