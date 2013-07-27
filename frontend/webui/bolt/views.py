# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from forms import *
from django.core.urlresolvers import reverse
from django.http import Http404

def index(request):
    return HttpResponse("Hello, world!")

def better_choice(request):
    return render(request, 'choice.html', {"hyp":"This is a wrong hyp", "nbest":['one', 'two', 'three', 'four', 'five', 'six']})

def retype_ref(request):
    form = RetypeForm()
    
    return render(request, 'retype.html', {'form':form})

def translation(request):
    return render(request, 'translation.html', {"hyp": "This is the hyp"})

def input(request):
    return render(request, 'input.html')

def selected(request):
    try:
        action = request.POST['action']
        return HttpResponseRedirect(reverse('retype-ref')) if action == 'retype' else HttpResponseRedirect(reverse('translation'))
    except KeyError:
        raise Http404
