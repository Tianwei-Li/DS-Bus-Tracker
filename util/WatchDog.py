'''
Created on Apr 27, 2014

@author: Qian Mao
'''

from threading import Timer


# Watchdog class for timeout detection
class Watchdog(object):
    
    def __init__(self, time, func):
        ''' Class constructor. The "time" argument has the units of seconds. '''
        self._time = time
        self._func = func
        return
        
    def startWatchdog(self):
        ''' Starts the watchdog timer. '''
        self._timer = Timer(self._time, self._watchdogEvent)
        self._timer.daemon = True
        self._timer.start()
        return
        
    def petWatchdog(self):
        ''' Reset watchdog timer. '''
        self.stopWatchdog()
        self.startWatchdog()
        return
            
        
    def _watchdogEvent(self):
        '''
        This internal method gets called when the timer triggers. A keyboard 
        interrupt is generated on the main thread. The watchdog timer is stopped 
        when a previous event is tripped.
        '''
        self._func()
        '''
        # timeout if don't receive askBusLoc from RSN
        LOGGER.info("timeout")
        RSN_timeout__message = {
                                 "SM" : "DRIVER_SM",
                                 "action" : "timeout",
                                 }
        offerMsg(RSN_timeout__message)
        '''
        #self.stopWatchdog()
        #thread.interrupt_main()
        return

    def stopWatchdog(self):
        ''' Stops the watchdog timer. '''
        self._timer.cancel()
        
        