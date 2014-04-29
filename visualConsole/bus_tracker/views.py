from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

from time import sleep



import sys
sys.path += ['../']

import host.master as master

# Create your views here.
@csrf_exempt
def index(reqest):
    return render_to_response('bus_tracker/index.html', {})

@csrf_exempt
@never_cache
def visualization(request):
	simulator_list = master.getSimulatorNames()
	if simulator_list == None:
		simulator_list = []
	return render_to_response('bus_tracker/visualization.html', {"simulator_list" : simulator_list})

@csrf_exempt
@never_cache
def simulate(request):
	if master.ISINIT == False:
		master.initialize("127.0.0.1", 2000)
		sleep(3)

	if 'auto_run' in request.POST:
		# launch master
		master.auto_run()

	elif 'launch_simulator' in request.POST:
		# launch a simulator
		role = request.POST.get("roleRadios")
		simulator_name = request.POST.get("simulator_name")
		localName = request.POST.get("localName")
		id = request.POST.get("id")
		simulator_ip = request.POST.get('simulator_ip')
		simulator_port = int(request.POST.get('simulator_port'))
		host_ip = request.POST.get('host_ip')
		host_port = int(request.POST.get('host_port'))

		message = {
					"action" : "initialize", 
					"localName" : localName, 
					"role" : role, 
					"id" : id, 
					"localIP" : host_ip, 
					"localPort" : host_port
		}
		
		master.launchSimulator(simulator_name, simulator_ip, simulator_port, message)
	elif 'start_bus' in request.POST:
		# start a bus
		simulator_name = request.POST.get("simulator_name")
		route = request.POST.get("route")
		direction = int(request.POST.get("direction"))
		location = int(request.POST.get("location"))
		message = {
					"action" : "start", 
					"route" : route, 
					"direction" : direction, 
					"location" : location
				  }
		master.sendCmd(simulator_name, message)
	elif 'exit' in request.POST:
		# quit a simulator
		simulator_name = request.POST.get("simulator_name")
		messge =  {"action" : "exit"}
		master.sendCmd(simulator_name, message)

	simulator_list = master.getSimulatorNames()
	if simulator_list == None:
		simulator_list = []
	return render_to_response('bus_tracker/visualization.html', {"simulator_list" : simulator_list})


