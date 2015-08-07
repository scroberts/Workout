#!/usr/bin/env python3

import sys
import string
import re
from datetime import datetime, timedelta

units = {'km' : 1000.0, 'mile' : 1609.34, 'm' : 1.0, 'sec' : 1.0, 'min' : 60.0}

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

            
def parseNumUnit(nus):
    udic = {}
    # First part of str should be a number or a deltatime
    # Try deltatime first
    try:
        print('nus = ', nus)
        dtregex = re.compile(r'\d+(\:+\d+){1,2}')
        tstr = dtregex.search(nus)
        print('tstr = ', tstr.group())
        n = getTime(tstr.group()).total_seconds()
        print('n = ', n)
        udic['numerator'] = 'sec'
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
            udic['numerator'] = u
        try:
            if unitstr[1] == u:
                udic['denominator'] = u
        except:
            pass
    return([n,udic]) 

def parseWS(WS, wstr, fitness):
    res = wstr.split('rep')
    if len(res) > 1:
        WS.reps = num(res[0])
    WS.wsteps = []  
    res = res[-1].split('+')
    for str in res:
        print('parseWS:',str.strip())
        ws_str = str.split('@')
#         print('parseWS lr:',ws_str[0].strip(), ws_str[1].strip())
        step = []
        try:
            step.append(Vol(ws_str[0].strip()))
            step.append(Rate(ws_str[1].strip(), fitness))
            step[0].displayVol()
            step[1].displayRate()
            WS.wsteps.append(step)
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
        print('Workout __init__:fitness.fitness = ',self.fitness)
        print('Workout __init__: Fitness = ', self.pace_for_fitness('E'))
        self.ws = WS(wstr, self.fitness)
        
    def displayWorkout(self):
        print('displayWorkout: listing of Vol / Rate pairs')
        for v,r in self.ws.wsteps:
            v.displayVol()
            r.displayRate()
        print('displayWorkout: End')
        
    def pace_for_fitness(self, id):
        return(self.fitness[id])
    
class WS:
    def __init__(self, wstr, fitness):
        print('\nWS Entry')
        print('WS __init__: Reading: ', wstr)
        self.wstr = wstr
        res = wstr.split('rep')
        try:
            parseWS(self,wstr, fitness)
        except:
            print('WS __init__: Error parsing input string')
            raise

    def displayWS(self):
        try:
            print('displayWS: reps = ', self.reps)
            displayVol(self)
            displayRate(self)
        except:
            print('displayWS: single rep')

class Vol:
    def __init__(self, VolStr):
        print('Vol: VolStr = ', VolStr)
        self.VolStr = VolStr
#         try:
#             VolStr = 
        try:
            self.Amt = getTime(VolStr).total_seconds()
            self.Unit = 'sec'
        except:
            self.Amt = VolStr
            self.Unit = 'Unknown'
        
    def displayVol(self):
        print("displayVol: Volume = ", self.Amt, self.Unit)
    
    
class Rate:
    def __init__(self, RateStr, fitness):
        print('Rate: RateStr = ', RateStr)
        self.RateStr = RateStr
        for level,rate in fitness.items():
            try:
                RateStr = RateStr.replace(level,rate)
#                 print('Rate: level, rate, RateStr',level, rate, RateStr)
                self.RateStr = RateStr
            except Exception:
                pass

        print('Rate: RateStr after fitness = ', RateStr)

        [self.Rate, self.Unit] = parseNumUnit(RateStr)
#         rstr = RateStr.split('/')
#         print('Rate split = ',rstr)
#         try:
#             self.Rate = getTime(rstr[0]).total_seconds()
#         except:
#             self.Rate = rstr[0]
#         self.Unit = rstr[1]
#         self.Rate = self.Rate / units[rstr[1]]
            
        print('Rate __init__: Rate, Unit ', self.Rate, self.Unit)  
                  
#         if RateStr.find('/km'):
#             self.Unit = 'km'
#             rs = RateStr.replace('/km','')   
#             print('Rate __init__: rs = ',rs)  
#             try:
#                 self.Rate = getTime(rs).total_seconds()/1000.0
#                 self.Unit = 'sec/m'
#                 print('Rate __init__: self.Rate: ', self.Rate)
#             except:
#                 exitstr = 'Error: unable to determine rate from: [ ' + rs + ']'
#                 sys.exit(exitstr) 
#         else:
#             self.Unit = 'Unknown'
#             self.Rate = 'Unknown'
         
    def displayRate(self):
        print("displayRate: Rate, Unit =", self.Rate, self.Unit)
    


w1str = '2 rep 1.2 km @ 4:32/km + 5 min @ 7:00/mile'
w2str = '60 min @ E + 20 min @ T + 5 min @ E + 10 min @ T + 5 min @ E + 5 min @ T'
w3str = '2 rep 1.2 km @ 4:32/km + 90 sec @ R + 500 m @ 120 sec + 200 m @ R'
w4str = 'a rep 1.2 km @ 5:00/mile'

nu = parseNumUnit('123.4 sec')
print('unit/num = ', nu)

nu = parseNumUnit('4:32/km')
print('unit/num = ', nu)

nu = parseNumUnit('10.0 km')
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