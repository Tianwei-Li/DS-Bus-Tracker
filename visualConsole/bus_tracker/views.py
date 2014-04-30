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
	if master.ISINIT == False:
		master.initialize("127.0.0.1", 2000)
		sleep(3)

	if 'auto_run' in request.POST:
		# launch master
		script = request.POST.get("auto_run_scripts")
		master.auto_run(script)

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
		
		master.launchSimulator(simulator_name, role, simulator_ip, simulator_port, message)
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
		message =  {"action" : "exit"}
		master.sendCmd(simulator_name, message)
	elif 'user_request' in request.POST:
		# user sends a query
		simulator_name = request.POST.get("simulator_name")
		route = request.POST.get("route")
		direction = int(request.POST.get("direction"))
		location = int(request.POST.get("location"))
		destination = int(request.POST.get("destination"))

		message = {
					"action" : "request", 
				    "route" : route, 
				    "direction" : direction, 
				    "destination" : destination, 
				    "location" : location
				  }

		master.sendCmd(simulator_name, message)
	elif 'terminate_all' in request.POST:
		master.terminate()

	simulator_list = master.getSimulatorNames()
	route_list = master.getRoutes()
	auto_run_script_list = master.getScripts()

	if route_list == None:
		route_list = []

	return render_to_response('bus_tracker/visualization.html', {"gsn_list" : simulator_list["GSN"], 
																 "driver_list" : simulator_list["DRIVER"],
																 "user_list" : simulator_list["USER"],
																 "route_list" : route_list,
																 "auto_run_script_list" : auto_run_script_list})


