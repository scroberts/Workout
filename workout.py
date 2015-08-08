#!/usr/bin/env python3

import sys
import string
import re
from datetime import datetime, timedelta

units = {'km' : 1000.0, 'mile' : 1609.34, 'm' : 1.0, 'sec' : 1.0, 'min' : 60.0, 'hr' : 3600, 'time' : 1}
distUnit = ['km', 'mile', 'm']
timeUnit = ['sec', 'min', 'hr', 'time']

def getTime(deltastr):
    # we specify the input and the format...
    try:
        t = datetime.strptime(deltastr,"%H:%M:%S")
    except:
        try:
            t = datetime.strptime(deltastr,"%M:%S")
        except:
            exitstr = 'Error: unable to parse timedelta string: [ ' + deltastr + ']'
            sys.exit(exitstr)
    # ...and use datetime's hour, min and sec properties to build a timedelta
    delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    return(delta)

def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except:
            exitstr = 'Error: value is not a number in num: [ ' + s + ']'
            sys.exit(exitstr)

def procWSstr(wstr, fitness):
    # First substitute times for fitness paces
    wstr = RepFitRate(wstr, fitness)
   
def RepFitRate(wstr, fitness):
    for level,rate in fitness.items():
        try:
            wstr = wstr.replace(level,rate)
#                 print('Rate: level, rate, wstr',level, rate, wstr)
        except Exception:
            pass
    return(wstr)

def printNumUnit(mag, unit):
    mag = mag / units[unit['num']]
    try:
        mag = mag * units[unit['den']]
    except:
        pass        
#     if mag > 100 and (unit['num'] == 'sec' or unit['num'] == 'time'):
    if mag > 100 and unit['num'] == 'time':
        mag = str(timedelta(seconds=mag))
        if '.' in mag:
            mag = mag.rstrip('0')       
    try:
        print(mag, '[', unit['num'], '/', unit['den'], ']', end="")
    except:
        print(mag, '[', unit['num'], ']',end="")    
            
def parseNumUnit(nus):
    udic = {}
    # First part of str should be a number or a deltatime
    # Try deltatime first
    try:
#         print('nus = ', nus)
        dtregex = re.compile(r'\d+(\:+\d+){1,2}')
        tstr = dtregex.search(nus)
#         print('tstr = ', tstr.group())
        n = getTime(tstr.group()).total_seconds()
#         print('n = ', n)
        udic['num'] = 'time'
        unitstr = nus.replace(tstr.group(),'')
    # now assume its a decimal or floating point number
    except:
        numRegex = re.compile(r'\d+\.?\d*')
        match = numRegex.search(nus)
        n = num(match.group())
        unitstr = nus[match.span()[1]:].strip()
    
    # now process the units in the numerator and denominator
    unitstr = unitstr.split('/')
    
    # if there's no '/' then the first and only string will be the
    # numerator.  If there's a second string it will always be the
    # denominator
    
    for u in units.keys():
        if unitstr[0] == u:
            udic['num'] = u
            n = n * units[u]
        try:
            if unitstr[1] == u:
                udic['den'] = u
                n = n / units[u]
        except:
            pass
    return([n,udic]) 

def getTimeDist(v,r):
    if 'den' in r.Unit and (v.Unit['num'] in distUnit and (r.Unit['num'] in timeUnit and r.Unit['den'] in distUnit)):
        time = v.Amt * r.Rate
        dist = v.Amt
    elif v.Unit['num'] in distUnit and r.Unit['num'] in timeUnit:
        time = r.Rate
        dist = v.Amt   
    elif v.Unit['num'] in timeUnit and (r.Unit['num'] in timeUnit and r.Unit['den'] in distUnit):
        time = v.Amt
        dist = v.Amt / r.Rate
    else:
        print('getTimeDist: Unable to calculate time / distance')
        time = 0
        dist = 0  
    return([time, dist])   

def printTime(t):
    if t > 100:
        tstr = str(timedelta(seconds=t))
        tstr = tstr.lstrip('0:')
        if '.' in tstr:
            tstr = tstr.rstrip('0') 
        print(tstr,end="")
    else:
        print('{0:0.1} [sec] '.format(t),end='')
            
def printTimeDist(t,d):
    print('Time = ', end = '')
    printTime(t)
    print(', Dist = {0:0.1f} km'.format(d/units['km']),end='')  

def parseWS(WS, wstr, fitness):
    res = wstr.split('rep')
    WS.reps = 1
    if len(res) > 1:
        WS.reps = num(res[0])
    WS.wsteps = []
    WS.time = 0
    WS.dist = 0  
    res = res[-1].split('+')
    for str in res:
#         print('parseWS:',str.strip())
        ws_str = str.split('@')
#         print('parseWS lr:',ws_str[0].strip(), ws_str[1].strip())
#         step = []
        try:
            v = Vol(ws_str[0].strip())
            r = Rate(ws_str[1].strip(), fitness)
            [time, dist] = getTimeDist(v,r)
            WS.time += time
            WS.dist += dist
            WS.wsteps.append([v, r, time, dist])
#             print('parseWS: WS.wsteps:',WS.wsteps)
        except:
            exitstr = 'Error: unable to parse: [ ' + str.strip() + ']'
            sys.exit(exitstr)  
            
def get_fitness(level):
    fitness = {}
    fitness['vdot50'] = {}
    fitness['vdot50'] = {'E' : '5:15/km', 'M' : '4:31/km', 'T' : '4:15/km', 'I' : '3:55/km', 'R' : '3:38/km'}
#     for intensity, rate in fitness[level].items():
#         print('get_fitness:',intensity, rate)
    return fitness[level]
        
class Workout:
    def  __init__(self, wstr, fitstr):
        print('\nWorkout: wstr, fitstr = ',wstr, fitstr)
        self.fitness = get_fitness(fitstr)
#         print('Workout __init__:fitness.fitness = ',self.fitness)
#         print('Workout __init__: Fitness = ', self.pace_for_fitness('E'))
        self.ws = WS(wstr, self.fitness)
        
    def displayWorkout(self):
#         print('displayWorkout: listing of Vol / Rate pairs')
        print('reps = ', self.ws.reps)
        for v,r,t,d in self.ws.wsteps:
            v.displayVol()
            print(' ',end='')
            r.displayRate()
            print(' ',end='')
            printTimeDist(t,d)
            print('')
        print('Total ',end = '')
        printTimeDist(self.ws.time, self.ws.dist)
        
#             try:
#                 if v.Unit['num'] in distUnit and (r.Unit['num'] in timeUnit and r.Unit['den'] in distUnit):
#                     print('Time = {0:.1f} {1:}'.format(v.Amt * r.Rate / units[r.Unit['num']], r.Unit['num']))
#                     print('Dist = ', v.Amt / units['m'], '[ m ]')
#             except:
#                 if v.Unit['num'] in distUnit and r.Unit['num'] in timeUnit:
#                     print('Time = {0:.1f} {1:}'.format(r.Rate / units[r.Unit['num']], r.Unit['num']))
#                     print('Dist = ', v.Amt / units['m'], '[ m ]')          
#         print('displayWorkout: End')
        
    def pace_for_fitness(self, id):
        return(self.fitness[id])
    
class WS:
    def __init__(self, wstr, fitness):
#         print('\nWS Entry')
#         print('WS __init__: Reading: ', wstr)
        self.wstr = wstr
        res = wstr.split('rep')
        try:
            parseWS(self, wstr, fitness)
        except:
            print('WS __init__: Error parsing input string')
            raise

class Vol:
    def __init__(self, VolStr):
#         print('Vol: VolStr = ', VolStr)
        self.VolStr = VolStr
        [self.Amt, self.Unit] = parseNumUnit(VolStr)
#         print('Vol __init__: Amt, Unit ', self.Amt, self.Unit)  
        
    def displayVol(self):
        print("Vol = ", end="")
        printNumUnit(self.Amt, self.Unit)
    
    
class Rate:
    def __init__(self, RateStr, fitness):
#         print('Rate: RateStr = ', RateStr)
        self.RateStr = RateStr
        for level,rate in fitness.items():
            try:
                RateStr = RateStr.replace(level,rate)
#                 print('Rate: level, rate, RateStr',level, rate, RateStr)
                self.RateStr = RateStr
            except Exception:
                pass

#         print('Rate: RateStr after fitness = ', RateStr)
        [self.Rate, self.Unit] = parseNumUnit(RateStr)
#         print('Rate __init__: Rate, Unit ', self.Rate, self.Unit)  
         
    def displayRate(self):
        print("Rate = ", end = "")
        printNumUnit(self.Rate, self.Unit)

w1str = '2 rep 1.2 km @ 4:32/km + 5 min @ 7:00/mile'
w2str = '60 min @ E + 20 min @ T + 5 min @ E + 10 min @ T + 5 min @ E + 5 min @ T'
w3str = '2 rep 1.2 km @ 4:32/km + 90 sec @ R + 500 m @ 120 sec + 200 m @ R'
w4str = 'a rep 1.2 km @ 5:00/mile'

nu = parseNumUnit('123.4 sec')
print('unit/num = ', nu)
printNumUnit(nu[0], nu[1])

nu = parseNumUnit('4:32/km')
print('unit/num = ', nu)
printNumUnit(nu[0], nu[1])

nu = parseNumUnit('12.0 km/hr')
print('unit/num = ', nu)

nu = parseNumUnit('10.0 mile')
print('unit/num = ', nu)

# nu = parseNumUnit('E')
# print('unit/num = ', nu)

wo1 = Workout(w1str,'vdot50')
wo1.displayWorkout()

wo2 = Workout(w2str,'vdot50')
wo2.displayWorkout()

wo3 = Workout(w3str,'vdot50')
wo3.displayWorkout()


# dt = getTime('1:01:01')
# print(dt.total_seconds())
# 
# dt = getTime('4:32')
# print(dt.total_seconds())
# 
# dt = getTime('4:3a')
# print(dt.total_seconds())

# a = Vol('5.0 km')
# b = Vol('4:32')
# a.displayVol()
# b.displayVol()