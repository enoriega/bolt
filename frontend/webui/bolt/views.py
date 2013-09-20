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
from functions import persist_log, close_log_entry
from datetime import datetime
import pdb
import json
from bolt import intelligence
from bolt.templatetags.bolt_tags import filter_refhyp


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
    wav = request.session['wav']
    nbest = [' '.join(nb[2]) for nb in sausage.nbests][:4]

    # Log stuff
    #entry['nbest'] = nbest
    ####

    return render(request, 'choice.html', {"hyp":hyp, "nbest":nbest, 'wav':wav, 'initial_view':request.session['initial_view']})

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
        prev_entry = log[-1]
        prev_entry['end_time'] = datetime.now()
        prev_entry['action'] = 'retype'

        entry = {}
        entry['name'] = 'retype-ref'
        entry['start_time'] = datetime.now()
        log.append(entry)
        request.session['log'] = log
        ####

        form = RetypeForm()
        wav = request.session['wav']
    
        return render(request, 'retype.html', {'form':form, 'wav':wav, 'initial_view':request.session['initial_view']})

#@close_log_entry('retype-ref')
def translation(request):
    # Log
    log = request.session['log']
    entry = log[-1]
    if 'end_time' not in entry:
        entry['end_time'] = datetime.now()
    ####
    wav = request.session['wav']

    hyp = request.session['translated']
    # Write the log to the FS
    persist_log(log)
    #########################
    action = reverse(request.session['initial_view'])
    return render(request, 'translation.html', {"hyp": hyp, 'action':action, 'wav':wav, 'initial_view':request.session['initial_view']})

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
    data = { 'ref_num' : len(index)- 1, 'index':json.dumps(index), 'initial_view':request.session['initial_view']}
    return render(request, 'input.html', data)

#@close_log_entry('better choice')
def selected(request):
    # Log the entry
    log = request.session['log']
    entry = log[-1]
    entry['end_time'] = datetime.now()
    ####

    try:
        action = request.POST['action']
        hyp = request.POST['hyp']
        #choices = request.POST.getlist('choices')
        
        #if len(choices) > 0:
            # This line is for the select list, now we use radio buttons
            #choice = request.POST.getlist('choices')[0]
        if 'choices' in request.POST:
            choice = request.POST['choices']
        
        if action == 'close-enough':
            request.session['translated'] = choice
            ret = HttpResponseRedirect(reverse('translation'))
        elif action == 'retype':
            ret = HttpResponseRedirect(reverse('retype-ref'))
        elif action in ('perfect',):
            request.session['translated'] = choice
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
    wav = bolt.wavs[idx]
    request.session['sausage'] = sausage
    request.session['hyp'] = hyp
    request.session['ref'] = ref
    request.session['nbest'] = nbest
    request.session['wav'] = wav
    ret = {'ref': filter_refhyp(ref), 'hyp' : filter_refhyp(hyp), 'wav':wav, 'initial_view':request.session['initial_view'] }

    return HttpResponse(json.dumps(ret))

#@close_log_entry('input')
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

    if request.session['input-action'] in ('fix',): 
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
