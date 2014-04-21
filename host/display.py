import matplotlib.pyplot as plt 
import numpy as np
#import scipy.misc

im = plt.imread("/Volumes/HDD/Dropbox/CMU_course/18842_distributed_systems/Bus_Tracker/host/map.png")
implot = plt.imshow(im)

#fig, ax = plt.subplots()

x = [1, 20, 30, 40,50,60,70,80,90,100]
y = [3, 4, 3, 3,3,3,3,3,3,3]

ti = 0
while True:
    t = ti % 10
    if t == 0:
        points, = plt.plot(x[t], y[t], marker='*')
    else:
        new_x = x[t]
        new_y = y[t]
        points.set_data(new_x, new_y)
    plt.pause(2)
    ti = ti + 1
