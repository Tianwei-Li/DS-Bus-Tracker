import time
import pygmaps
import webbrowser

def display():
    mymap = pygmaps.maps(40.437822, -79.933101, 15)
    #mymap.setgrids(37.42, 37.43, 0.001, -122.15, -122.14, 0.001)
    #mymap.addradpoint(37.429, -122.145, 95, "#FF0000")
    stations = [(40.444632, -79.942993),(40.443897, -79.938852),(40.437822, -79.933101),(40.438051, -79.927844),(40.438051, -79.919368),(40.438002, -79.913145)]
    stationCnt = len(stations)
    
    mymap.addpath(stations,"#00FF00")
    url = '/Volumes/HDD/Dropbox/CMU_course/18842_distributed_systems/Bus_Tracker/host/mymap.html'

    for i in range(stationCnt):
        mymap.addpoint(stations[i][0], stations[i][1], "#0000FF")
        
    pathes = [(40.444632, -79.942993), (40.444322, -79.941147), (40.443897, -79.938852), (40.442673, -79.937649), (40.440566, -79.935696), (40.437822, -79.933101), (40.437822, -79.930675), (40.438051, -79.927844), (40.438051, -79.919368), (40.438132, -79.916084), (40.438002, -79.913145)]

    for i in range(len(pathes)):
        if i > 0:
            mymap.delpoint()
        mymap.addpoint(pathes[i][0], pathes[i][1], "#FF0000")

        mymap.draw('./mymap.html')
        browser = webbrowser.get("safari")
        browser.open(url)
        time.sleep(2)

if __name__ == '__main__':
    display()   
