# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from forms import *
from django.core.urlresolvers import reverse
from django.http import Http404

def index(request):
    return HttpResponse("Hello, world!")

def better_choice(request):
    refid = request.POST['refid']
    #ref = request.POST['ref']
    hyp = request.POST['hyp']
    return render(request, 'choice.html', {"hyp":hyp, "nbest":['one', 'two', 'three', 'four', 'five', 'six']})

def retype_ref(request):

    if request.method == 'POST':
        form = RetypeForm(request.POST)
        if form.is_valid():
            request.session['translated'] = form.cleaned_data['sentence']
            return HttpResponseRedirect(reverse('translation'))
    else:
        form = RetypeForm()
    
        return render(request, 'retype.html', {'form':form})

def translation(request):
    hyp = request.session['translated']
    return render(request, 'translation.html', {"hyp": hyp})

def input(request):
    return render(request, 'input.html')

def selected(request):
    try:
        action = request.POST['action']
        hyp = request.POST['hyp']
        choices = request.POST.getlist('choices')
        
        if len(choices) > 0:
            choice = request.POST.getlist('choices')[0]
        
        if action == 'translation':
            request.session['translated'] = choice
            ret = HttpResponseRedirect(reverse('translation'))
        elif action == 'retype':
            ret = HttpResponseRedirect(reverse('retype-ref'))
        elif action == 'ignore':
            request.session['translated'] = hyp
            ret = HttpResponseRedirect(reverse('translation'))
            
        return ret
        
    except KeyError:
        raise Http404
