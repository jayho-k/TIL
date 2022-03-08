
from django.urls import path,include
from articles import views

# 너는 articles라는 별명을 써 ==> app용
app_name = 'articles'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('index/', views.index, name = 'index'), # path용
    path('throw/', views.throw, name = 'throw'),
    path('catch/', views.catch, name = 'catch'),
]
