# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from forms import *
from django.core.urlresolvers import reverse
from django.http import Http404
from sausages import Sausage
import bolt
import json

def index(request):
    return HttpResponse("Hello, world!")

def better_choice(request):
    refid = request.POST['refid']
    #ref = request.POST['ref']
    hyp = request.POST['hyp']
    nbest = [' '.join(nb[2]) for nb in request.session['sausage'].nbests]
    return render(request, 'choice.html', {"hyp":hyp, "nbest":nbest})

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
    data = { 'ref_num' : bolt.ref_num }
    return render(request, 'input.html', data)

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

def read_sausage(request, idx):
    idx = int(idx)
    sausage_path = bolt.sausages[idx]
    sausage = Sausage.from_file(sausage_path, nbest_file=bolt.nbests[idx])
    ref = bolt.refs[idx]
    hyp = bolt.hyps[idx]
    request.session['sausage'] = sausage
    ret = {'ref': ref, 'hyp' : hyp }

    return HttpResponse(json.dumps(ret))
