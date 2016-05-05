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
hom = 3# db handoff margin
RSL_T = -102 #dBm mobile Rx Threshold

#users uniformly distributed
no_users =160
lam = float(2)/float(3600) #  2calls per hour(on average) 1800 seconds 2/3600
h = 3#minutes/call (=180 seconds/call)
v= 15#m/s (=54 kph = 33.553977 mph)
# direction 50/50 chance of heading north or south
path = "/Users/ranjitha/Downloads/antenna_pattern.txt"
s = numpy.loadtxt(path, unpack=True)

active_users={}
user_details =[]
user_non_active=[]
dropped_call={}
blocked_call=[]

def user_makes_new_call(j):
    x = numpy.random.random_integers(1,1800)
    x = 1800
    if p_call == x:
        user_details =[]
        print "I am inside"
        ''' Initiate a call
                '''
        '''determine the users location along the road
                '''
        user_loc = np.random.uniform(low=0.0, high=6000.0, size=None)
        user_details.append(user_loc)
        '''determine users direction (north or south)
                '''
        user_dir = numpy.random.randint(2)
        user_details.append(user_dir)
        '''to determine distance between the mobile and base station
                '''
        if user_dir == 0:
            #North
            distance_user = 3000 - user_loc
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base
        elif user_dir == 1:
            distance_user = user_loc - 3000
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base
                   
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
            user_details.append("Call Failed")
            user_details.append({"Call Dropped":"Signal Strength"})
            active_users[i]=user_details
            return 0
        else:
            ''' maximum rsl among alpha and beta is taken as the serving sector
                '''
            if rsl_sectorA > rsl_sectorB:
                sector = "Alpha"
                user_details.append(sector)
                if md.NUM_CH_A !=0:
                    user_details.append(sector)
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
                    inactive_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    if rsl_sectorB > RSL_T:
                        sector = "Beta"
                        if md.NUM_CH_B !=0:
                            user_details.append(sector)
                            md.NUM_CH_B = md.NUM_CH_B-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorB})
                            active_users[i]=user_details
                            
            else:
                sector = "Beta"
                user_details.append(sector)
                if md.NUM_CH_B !=0:
                    user_details.append(sector)
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
                    inactive_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    
                    if rsl_sectorA > RSL_T:
                        sector = "Aplha"
                        if md.NUM_CH_A !=0:
                            user_details.append(sector)
                            md.NUM_CH_A = md.NUM_CH_A-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorA})
                            active_users[i]=user_details
                    
    else:
        print "call not made"
    print active_users

        


''' For each user that does not have a call up
    '''

''' Probablity of a call = λ*ΔT ; probability of a call is taken from 1 to 1800
    which will be 1 in 1800 and checked with a random number say 1800 
    '''


print "Welcome to Python application which will simulate the downlink behavior of a 3-sectored basestation"

'''Initial simulation of 1 hour
    '''
def user_has_call(i):
    return 0

#for i in range (tot_sim_sec):
for i in range (1):

    '''160 users always on the road
        '''
    #for j in range (no_users):
    for j in range (2):
        if len(active_users) != 0:

             user_has_call(j)
        else:

            user_makes_new_call(j)


        
