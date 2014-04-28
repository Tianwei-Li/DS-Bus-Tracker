from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from polls.models import Poll, Choice
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt


import sys
sys.path += ['../']

import host.master as master

# Create your views here.
def index(reqest):
    return render_to_response('bus_tracker/index.html', {})

def visualization(request):
	return render_to_response('bus_tracker/visualization.html', {})

@csrf_exempt
def simulate(request):
	if 'auto_run' in request.POST:
		# launch master
		master.djangoMain()
		master.setupSim()
		
	return render_to_response('bus_tracker/visualization.html', {})


