import random
import numpy
import numpy as np
import math
from numpy import ndarray

from numpy import (array, dot, arccos)
from numpy.linalg import norm
import sys
my_path ='/Users/ranjitha/Desktop/2SEM/ENTS656'
sys.path.append(my_path)
import modules_656project as md


#basic paramaeters
road_l=6 #km
del_t=1 #sec
tot_sim_t= 1 # 1 or more hrs, total simulation time
tot_sim_sec = tot_sim_t*3600
p_call =1800

#each basestation may have the following propertities, some of which may be varied
hb= 50 #in m, this is the basestation anyenna height
# change to km loc_b = 20 # m west of the road at the midpoint of the road(3 km if the road is 6 km)
# 1 meter = 0.001 km
loc_b = 0.02

POW_TX=43 # dBm TX Power
LOSS = 2# db line/connector losses
AG_GAIN_TX = 15 #dbi, antenna gain
NUM_CH_A = 15 #per sector, no of traffice channels
NUM_CH_B = 15 
ALPHA_F=860 #MHz
BETA_F= 865 #MHz

#the mobile will have the following properties, some of which may be varied
hm = 1.5 #in m, height of mobile
HOM = 3# db handoff margin
RSL_T = -102 #dBm mobile Rx Threshold

#users uniformly distributed
no_users =160
lam = float(2)/float(3600) #  2calls per hour(on average) 1800 seconds 2/3600
h = 3#minutes/call (=180 seconds/call)
V_SPEED= 15#m/s (=54 kph = 33.553977 mph)
# direction 50/50 chance of heading north or south
path = "/Users/ranjitha/Downloads/antenna_pattern.txt"
s = numpy.loadtxt(path, unpack=True)

active_users={}
failed_users={}
user_details =[]
user_non_active=[]
dropped_call={}
blocked_call=[]

user_Dir = ''
archieve_users =[]
serving_sector=''


def user_makes_new_call(i,j):
    x = numpy.random.random_integers(1,1800)
    p_call = 1800
    if p_call == x:
        user_details =[]
        print "I am inside"
        ''' Initiate a call
                '''
        '''determine the users location along the road
                '''
        user_loc = np.random.uniform(low=0.0, high=6000.0, size=None)
        user_details.append({"user_loc":user_loc})
        '''determine users direction (north or south)
                '''
        user_dir = numpy.random.randint(2)
        
        '''to determine distance between the mobile and base station
                              '''
        user_details.append({"time":j})
        if user_dir == 0:
            #North
            user_details.append({"user_dir":"north"})
            distance_user = 3000 - user_loc
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base
        elif user_dir == 1:
            user_details.append({"user_dir":"south"})
            distance_user = user_loc - 3000
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base
            user_details.append({"user_distance":dist_mob2base})
                   
            '''Find the RSL at the mobile from each sector
               md--->modules_656project.py '''
        rsl_sectorA,rsl_sectorB = md.rsl_eirp(dist_mob2base)
        '''RSLSERVER is greater than or equal to the RSL threshold
            '''
        rsl_mob = max(rsl_sectorA,rsl_sectorB)
        call_length = int(numpy.random.exponential(scale=180))

        if rsl_mob < RSL_T:
            
            '''call attempt failed due to signal strength less than threshold
                And move to the next user
                '''
            if rsl_sectorA > rsl_sectorB:
                sector = "alpha"
            else:
                sector = "beta"
            user_details.append({"sector": sector})
            user_details.append({"call_status":"Call Failed"})
            user_details.append({"Call Dropped":"Signal Strength"})
            active_users[i]=user_details
            return 0
        else:
            ''' maximum rsl among alpha and beta is taken as the serving sector
                '''
            if rsl_sectorA > rsl_sectorB:
                sector = "Alpha"
                #user_details.append(sector)
                if md.NUM_CH_A !=0:
                    user_details.append({"sector":sector})
                    md.NUM_CH_A -=1
                    user_details.append({"call_status":"Call Established"})
                    user_details.append({"call length":call_length})
                    user_details.append({"rsl":rsl_sectorA})
                    active_users[i]=user_details
                else:
                    user_details =[]
                    user_details.append({"call_status":"Call Failed"})
                    user_details.append({"call_blocked":sector})
                    user_details.append({"capacity":"Insufficent_Capacity"})
                    failed_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    if rsl_sectorB > RSL_T:
                        sector = "Beta"
                        if md.NUM_CH_B !=0:
                            user_details.append({"sector":sector})
                            md.NUM_CH_B = md.NUM_CH_B-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorB})
                            active_users[i]=user_details
                            
            else:
                sector = "Beta"
                #user_details.append(sector)
                if md.NUM_CH_B !=0:
                    user_details.append({"sector":sector})
                    md.NUM_CH_B = md.NUM_CH_B-1
                    user_details.append({"call_status":"Call Established"})
                    user_details.append({"call length":call_length})
                    user_details.append({"rsl":rsl_sectorB})
                    active_users[i]=user_details
                else:
                    user_details =[]
                    user_details.append({"call_status":"Call_Failed"})
                    user_details.append({"call blocked":sector})
                    user_details.append({"capacity":"Insufficent Capacity"})
                    failed_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    
                    if rsl_sectorA > RSL_T:
                        sector = "Aplha"
                        if md.NUM_CH_A !=0:
                            user_details.append({"sector":sector})
                            md.NUM_CH_A = md.NUM_CH_A-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorA})
                            active_users[i]=user_details
                    
    else:
        #print "call not made"
        return 0
    print active_users

def user_has_call(time):
    '''Update the user’s location. We assume users will continue in the
        same direction for the duration of their call.
        '''
for each_users in active_users:
    for details in range (0,len(active_users[each_users])-1):
        ''' To obtain the 'direction of the user'''
        ''' if active list is item, successful call has been done
            '''
        if len(active_users[each_users]) == 0:
            continue
        else:
            
            for key,value in active_users[each_users][details].iteritems():
                if key == 'user_dir':
                    user_Dir = value
            '''To find the serving sector
            '''
            for key,value in active_users[each_users][details].iteritems():
                if key == 'sector':
                    serving_sector = value
                    print serving_sector
                    
        
            for key,value in active_users[each_users][details].iteritems():
                if key == 'user_loc':
                    if user_Dir == 'north' and value >0 :
                        active_users[each_users][details][key]=value-V_SPEED
                        print "Go Terps"
                    elif user_Dir == 'south' and value <6000 :
                        active_users[each_users][details][key]=value+V_SPEED
                    if value <0 or value >6000:
                        active_users[each_users].append({"Call_exit_status":"Successful call"})
                        #change list to dict if you want call number
                        archieve_users= active_users[each_users]
                        active_users[each_users] = []
                        print "due to end of road",archieve_users
                        print active_users
                        
                
                if key == 'call length':
                    print key
                    
                    if value > 0:
                        active_users[each_users][details][key]=value-1
                    else:
                        active_users[each_users].append({"Call_exit_status":"Successful call"})
                        #change list to dict if you want call number
                        archieve_users= active_users[each_users]
                        active_users[each_users] = []
                        #print archieve_users
                        #print active_users
                        if serving_sector == 'alpha':
                            NUM_CH_A +=1
                        else:
                            NUM_CH_B +=1
            '''Calculating the new RSL
                '''
            if len(active_users[each_users]) == 0:
                    continue
            else:                           
                for key,value in active_users[each_users][details].iteritems():
                    if key == 'user_loc':
                        new_user_loc = value

                        rsl_sectorA,rsl_sectorB = md.rsl_eirp(new_user_loc)
                        '''RSLSERVER is greater than or equal to the RSL threshold
                            '''
                        rsl_mob = max(rsl_sectorA,rsl_sectorB)
                        
                        if rsl_mob < RSL_T:
            
                            '''call attempt failed due to signal strength less than threshold
                            And move to the next user
                            '''
                            if rsl_sectorA > rsl_sectorB:
                                sector = "alpha"
                            else:
                                sector = "beta"
                            active_users[each_users].append({"sector": sector})
                            active_users[each_users].append({"call_status":"Call Failed"})
                            active_users[each_users].append({"Call Dropped":"Signal Strength"})
                            archieve_users= active_users[each_users]
                            active_users[each_users] = []
                            if serving_sector == 'alpha':
                                NUM_CH_A +=1
                            else:
                                NUM_CH_B +=1

                        else:
                            if serving_sector == 'alpha':
                                if rsl_sectorB >= rsl_sectorA + HOM:
                                    active_users[each_users].append({"hand_off": serving_sector})
                                    if NUM_CH_B >0:
                                        active_users[each_users]["sector"] = "beta"
                                        active_users[each_users]["rsl"] = rsl_sectorB
                                        active_users[each_users].append({"hand_off_status": "Successful"})
                                        NUM_CH_A -=1
                                        NUM_CH_B +=1
                                    else:
                                        active_users[each_users].append({"hand_off_status": "Failure"})
                            else:
                                if rsl_sectorA >= rsl_sectorB + HOM:
                                    active_users[each_users].append({"hand_off": serving_sector})
                                    if NUM_CH_A >0:
                                        active_users[each_users]["sector"] = "alpha"
                                        active_users[each_users]["rsl"] = rsl_sectorA
                                        active_users[each_users].append({"hand_off_status": "Successful"})
                                        NUM_CH_A +=1
                                        NUM_CH_B -=1
                                    else:
                                        active_users[each_users].append({"hand_off_status": "Failure"})
                                        
                    
''' For each user that does not have a call up
    '''

''' Probablity of a call = λ*ΔT ; probability of a call is taken from 1 to 1800
    which will be 1 in 1800 and checked with a random number say 1800 
    '''

#time
print "Welcome to Python application which will simulate the downlink behavior of a 3-sectored basestation"

'''Initial simulation of 1 hour
    '''
#def user_has_call(j):

    
#    return 0

#for i in range (tot_sim_sec):
active=0
for i in range (100):

    '''160 users always on the road
time        '''
    #for j in range (no_users):
    
    for j in range (no_users):

            
        if active > 0:
            '''There is a proble here, prefrence should be given to the
                active calls but not that all calls in the acctive calls should be serviced and then new call is initated
                '''

            user_has_call(i)
            active-=1
        else:

            user_makes_new_call(i,j)
            active+=1
        


        
