# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from forms import *
from django.core.urlresolvers import reverse
from django.http import Http404
from sausages import Sausage
import bolt
import json
from classification import *
from functions import persist_log
from datetime import datetime
import pdb
import json
from bolt import intelligence

def index(request):
    return HttpResponse("Hello, world!")

def better_choice(request):

    # Log the transition
    log = request.session['log']
    entry = {}
    entry['name'] = 'better choice'
    entry['start_time'] = datetime.now()
    log.append(entry)
    request.session['log'] = log
    ####

    
    hyp = request.session['hyp']
    sausage = request.session['sausage']
    nbest = [' '.join(nb[2]) for nb in sausage.nbests][:4]

    # Log stuff
    #entry['nbest'] = nbest
    ####

    return render(request, 'choice.html', {"hyp":hyp, "nbest":nbest})

def retype_ref(request):

    # Log
    log = request.session['log']
    ####


    if request.method == 'POST':
        form = RetypeForm(request.POST)
        if form.is_valid():
            # Log
            entry = log[-1]
            entry['retyped'] = form.cleaned_data['sentence']
            ####

            request.session['translated'] = form.cleaned_data['sentence']
            return HttpResponseRedirect(reverse('translation'))
    else:
        # Log
        entry = {}
        entry['name'] = 'retype-ref'
        entry['start_time'] = datetime.now()
        log.append(entry)
        request.session['log'] = log
        ####

        form = RetypeForm()
    
        return render(request, 'retype.html', {'form':form})

def translation(request):
    # Log
    log = request.session['log']
    entry = log[-1]
    if 'end_time' not in entry:
        entry['end_time'] = datetime.now()
    ####

    hyp = request.session['translated']
    # Write the log to the FS
    persist_log(log)
    #########################
    action = reverse(request.session['initial_view'])
    return render(request, 'translation.html', {"hyp": hyp, 'action':action})

def input(request, index = None, name=None):
    request.session.clear()
    # Initialize the log entry
    log = [] 
    entry = {}
    entry['name'] = 'input'
    entry['start_time'] = datetime.now()
    log.append(entry)
    
    request.session['log'] = log
    #############################
    request.session['initial_view'] = name

    data = { 'ref_num' : bolt.ref_num - 1, 'index':json.dumps(index)}
    return render(request, 'input.html', data)

def selected(request):
    # Log the entry
    log = request.session['log']
    entry = log[-1]
    entry['end_time'] = datetime.now()
    ####

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
        elif action in ('perfect', 'close-enough'):
            request.session['translated'] = hyp
            ret = HttpResponseRedirect(reverse('translation'))
            

        # Log stuff
        entry['action'] = action
        if 'choice' in locals():
            entry['choice'] = choice
        ####

        return ret
        
    except KeyError:
        raise Http404

def read_sausage(request, idx):
    idx = int(idx)
    sausage_path = bolt.sausages[idx]
    sausage = Sausage.from_file(sausage_path, nbest_file=bolt.nbests[idx])
    ref = bolt.refs[idx]
    hyp = bolt.hyps[idx]
    nbest = bolt.nbests[idx]
    request.session['sausage'] = sausage
    request.session['hyp'] = hyp
    request.session['ref'] = ref
    request.session['nbest'] = nbest
    ret = {'ref': ref, 'hyp' : hyp }

    return HttpResponse(json.dumps(ret))

def logistic_classification(request):

    # Update the last log entry
    log = request.session['log']
    entry = log[-1]
    entry['end_time'] = datetime.now()
    ####

    idx = int(request.POST['refid'])                                     
    hyp = bolt.hyps[idx]
    sausage = Sausage.from_file(bolt.sausages[idx], bolt.nbests[idx])
    ref = bolt.refs[idx]
    nbest = bolt.nbests[idx]
    request.session['idx'] = idx
    request.session['sausage'] = sausage
    request.session['hyp'] = hyp
    request.session['ref'] = ref
    request.session['nbest'] = nbest
    request.session['input-action'] = request.POST['action']

    # Log stuff
    entry['ref'] = ref
    entry['hyp'] = hyp
    entry['index'] = idx
    entry['id'] = bolt.names[idx]
    entry['action'] = request.session['input-action']
    ####

    if request.session['input-action'] in ('classification',): 
        if intelligence:
            # Classify in order to move on to the corresponding step
            vector = logistic_vectors[idx] #create_feature_vector_logistic(hyp, sausage, nbest)
            result = ok_or_error(vector)[0]
        
            # Change this to correctly handle a numpy array
            if result == 0:
                request.session['translated'] = hyp
                return HttpResponseRedirect(reverse('translation'))
            else:
                return HttpResponseRedirect(reverse('linear-regression'))
        else:
            return HttpResponseRedirect(reverse('better-choice'))
    else:
        request.session['translated'] = hyp
        return HttpResponseRedirect(reverse('translation'))


def linear_regression(request):
    threshold = 4
    idx = request.session['idx']
    hyp = request.session['hyp']
    sausage = request.session['sausage']
    nbest = request.session['nbest']

    vector = linear_vectors[idx] #create_feature_vector_linear(hyp, sausage, nbest)
    result = predicted_wer(vector)

    # Change this to correctly handle a numpy array
    if result <= threshold:
        return HttpResponseRedirect(reverse('better-choice'))
    else:
        #request.session['translated'] = hyp
        return HttpResponseRedirect(reverse('retype-ref'))
