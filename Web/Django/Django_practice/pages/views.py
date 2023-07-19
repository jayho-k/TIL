from multiprocessing import context
from django.shortcuts import render
import random
random.seed = 777

# Create your views here.
def lotto(request):
    context ={
        'lst' : random.sample(list(range(1,46)), 6)
    }
    return render(request, 'lotto.html', context)