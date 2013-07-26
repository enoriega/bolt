# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

def index(request):
    return HttpResponse("Hello, world!")

def better_choice(request):
    return render(request, 'choice.html')

def retype_ref(request):
    return render(request, 'retype.html')

def translation(request):
    return render(request, 'translation.html', {"hyp": "This is the hyp"})

def input(request):
    return render(request, 'input.html')
