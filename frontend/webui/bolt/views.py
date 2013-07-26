# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from forms import *

def index(request):
    return HttpResponse("Hello, world!")

def better_choice(request):
    return render(request, 'choice.html', {"hyp":"This is a wrong hyp", "nbest":['one', 'two', 'three']})

def retype_ref(request):
    form = RetypeForm()
    
    return render(request, 'retype.html', {'form':form})

def translation(request):
    return render(request, 'translation.html', {"hyp": "This is the hyp"})

def input(request):
    return render(request, 'input.html')
