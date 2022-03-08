from django.shortcuts import render
from .models import Article

# Create your views here.
def index(request):

    # 이렇게 사용함으로써 순서를 반대로해줄 수 있음
    articles = Article.objects.all().order_by('-pk') 
    context ={
        'articles':articles
    }
    return render(request, 'articles/index.html', context)

def throw(request):
    context ={}
    return render(request, 'articles/throw.html', context)

def catch(request):
    title = request.GET.get('title')
    content = request.GET.get('content')

    # 왼쪽 Article에서  오른쪽 위에 title을 가져옴
    article = Article()
    article.title = title
    article.content = content

    # 이렇게 하면 모델에 저장이 되게 된다.
    article.save() 

    context ={
        'title':title,
        'content':content,
    }
    return render(request, 'articles/catch.html', context)