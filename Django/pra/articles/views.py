from django.shortcuts import render

# Create your views here.
def index(request):
    context ={}
    return render(request, 'articles/index.html', context)

def throw(request):
    context ={}
    return render(request, 'articles/throw.html', context)

def catch(request):
    data = request.GET.get('content')
    context ={
        'data':data,
    }
    return render(request, 'articles/catch.html', context)