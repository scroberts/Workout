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
        except Exception:
            pass
    return(wstr)
    
def printTime(t):
    if t > 100:
        tstr = str(timedelta(seconds=t))
        tstr = tstr.lstrip('0:')
        if '.' in tstr:
            tstr = tstr.rstrip('0') 
        print(tstr,end="")
    else:
        print('{0:0.1f} [sec] '.format(t),end='')
            
def printTimeDist(t,d):
    print('Time = ', end = '')
    printTime(t)
    print(', Dist = {0:0.1f} km'.format(d/units['km']),end='')  

def printNumUnit(mag, unit):
    mag = mag / units[unit['num']]
    try:
        mag = mag * units[unit['den']]
    except:
        pass         
    if unit['num'] == 'time':
        printTime(mag)
        if 'den' in unit:
            print(' [/', unit['den'], ']', sep = '', end='')
    elif 'den' in unit:
        print(mag, ' [', unit['num'], '/', unit['den'], ']', sep = '', end='')
    else:
        print(mag, ' [', unit['num'], ']',sep = '', end='')    
            
def parseNumUnit(nus):
    udic = {}
    # First part of str should be a number or a deltatime
    # Try deltatime first
    try:
        dtregex = re.compile(r'\d+(\:+\d+){1,2}')
        tstr = dtregex.search(nus)
        n = getTime(tstr.group()).total_seconds()
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
            
def get_fitness(level):
    fitness = {}
    fitness['vdot50'] = {}
    fitness['vdot50'] = {'E' : '5:15/km', 'M' : '4:31/km', 'T' : '4:15/km', 'I' : '3:55/km', 'R' : '3:38/km'}
    return fitness[level]
        
class TrainingPlan:
    def __init__(self, planName):
        print('\Workout Plan:', planName)
        self.name = planName
        self.list = []
        
    def addWorkout(self, Dict, WorkoutName):
        try:
            wo = Dict.list[WorkoutName]
            self.list.append(wo)
        except:
            print("Couldn't find WorkoutName in Dict")
            
    def printTrainingPlan(self):
        print('\nTraining Plan:', self.name)
        for wo in self.list:
            wo.displayWorkout()

class WorkoutDict:
    def __init__(self, DictName):
        print('\nWorkout Dictionary:')
        print('\nName = ', DictName)
        self.name = DictName
        self.list = {}
        
    def addWorkout(self, WorkoutName, wslist, fitstr):
        wo = Workout(WorkoutName, wslist, fitstr)
        self.list[WorkoutName] = wo
        
    def listdict(self):
        for key,wo in self.list.items():
            print(wo.name)
        

class Workout:
    def  __init__(self, name, wslist, fitstr):
        self.name = name
        self.wslist = wslist
        self.fitstr = fitstr
        self.fitness = get_fitness(fitstr)
        self.wsegs = []
        self.time = 0
        self.dist = 0
        for wstr in wslist:
            wseg = WSeg(wstr, self.fitness)
            self.wsegs.append(wseg)
            self.time += wseg.time
            self.dist += wseg.dist
                 
    def displayWorkout(self):
        print('\nWorkout:')
        print('\tName = ', self.name)
        print('\twstr = ', self.wslist)
        print('\tfitstr = ', self.fitstr)
        for wseg in self.wsegs:
            print('\t\treps = ', wseg.reps)
            for v,r,t,d in wseg.wsteps:
                print('\t\t\t{',end='')
                v.displayVol()
                print(' @ ',end='')
                r.displayRate()
                print('} ',end='')
                printTimeDist(t,d)
                print('')
            print('\t\tWSEG: ',end = '')
            printTimeDist(wseg.time, wseg.dist)
            print('')
        print('\tWorkout: ',end = '')
        printTimeDist(self.time, self.dist)
        print('')
               
    def pace_for_fitness(self, id):
        return(self.fitness[id])

    
class WSeg:
    def __init__(self, wstr, fitness):
        self.wstr = wstr
        res = wstr.split('rep')
        try:
            self.parseWS(wstr, fitness)
        except:
            print('WS __init__: Error parsing input string')
            raise
            
    def parseWS(self, wstr, fitness):
        res = wstr.split('rep')
        self.reps = 1
        if len(res) > 1:
            self.reps = num(res[0])
        self.wsteps = []
        self.time = 0
        self.dist = 0  
        res = res[-1].split('+')
        for str in res:
            ws_str = str.split('@')
            try:
                v = Vol(ws_str[0].strip())
                r = Rate(ws_str[1].strip(), fitness)
                [time, dist] = getTimeDist(v,r)
                self.time += time
                self.dist += dist
                self.wsteps.append([v, r, time, dist])
            except:
                exitstr = 'Error: unable to parse: [ ' + str.strip() + ']'
                sys.exit(exitstr)  
        self.time *= self.reps
        self.dist *= self.reps

class Vol:
    def __init__(self, VolStr):
        self.VolStr = VolStr
        [self.Amt, self.Unit] = parseNumUnit(VolStr)
        
    def displayVol(self):
        printNumUnit(self.Amt, self.Unit)
       
class Rate:
    def __init__(self, RateStr, fitness):
        self.RateStr = RateStr
        for level,rate in fitness.items():
            try:
                RateStr = RateStr.replace(level,rate)
                self.RateStr = RateStr
            except Exception:
                pass
        [self.Rate, self.Unit] = parseNumUnit(RateStr)
         
    def displayRate(self):
        printNumUnit(self.Rate, self.Unit)

w1str = ['2 rep 1.2 km @ 4:32/km + 5 min @ 7:00/mile']
w2str = ['60 min @ E + 20 min @ T + 5 min @ E + 10 min @ T + 5 min @ E + 5 min @ T']
w3str = ['2 rep 1.2 km @ 4:32/km + 90 sec @ R + 500 m @ 120 sec + 200 m @ R']
w4str = ['10 min @ E', '2 rep 1.2 km @ T + 90 sec @ E', '10 min @ E']

plan = TrainingPlan('halfMarathon')
dict = WorkoutDict('woDict')

dict.addWorkout('workout 1', w1str, 'vdot50')
dict.addWorkout('workout 2', w2str, 'vdot50')
dict.addWorkout('workout 3', w3str, 'vdot50')
dict.addWorkout('workout 4', w4str, 'vdot50')
dict.listdict()

plan.addWorkout(dict,'workout 1')
plan.addWorkout(dict,'workout 3')

plan.printTrainingPlan()
