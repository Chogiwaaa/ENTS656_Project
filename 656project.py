# Application to Simulate the downlink behavior of a 3-sectored basesation

import random
import numpy
import numpy as np
import math
from numpy import ndarray

from numpy import (array, dot, arccos)
from numpy.linalg import norm

#basic paramaeters
road_l=6 #km
del_t=1 #sec
tot_sim_t= 1 # 1 or more hrs, total simulation time

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
no_u =160
lam = float(2)/float(3600) #  2calls per hour(on average) 1800 seconds 2/3600
h = 3#minutes/call (=180 seconds/call)
v= 15#m/s (=54 kph = 33.553977 mph)
# direction 50/50 chance of heading north or south
path = "/Users/ranjitha/Downloads/antenna_pattern.txt"
s = numpy.loadtxt(path, unpack=True)

def boresight_angle(d,sector):
    u = array([20,d])
    if sector == 860:
        v = array([0,1])
    elif sector == 865:
        v = array([math.sqrt(3)/2,-1/2])
        
    c = dot(u,v)/(norm(u)*norm(v))
    angle_boresight = int(np.degrees(arccos(c)))
    print "angle",s[1][angle_boresight]
    return s[1][angle_boresight]
    
       
def rsl_eirp(dist_mob2base):
    eirp_bore_sight = POW_TX+AG_GAIN_TX-LOSS
    print "eirp_bore_sight=",eirp_bore_sight
    # caculating eirp for alpha sector
    eirp1_loss=tot_path_loss(dist_mob2base,ALPHA_F)
    eirp_bore_alpha = boresight_angle(dist_mob2base,ALPHA_F)
    eirp_alpha =  eirp_bore_sight - eirp_bore_alpha
    rsl_alpha = eirp_alpha - tot_path_loss(dist_mob2base,ALPHA_F)
    # calculating eirp for beta sector
    eirp2_loss=tot_path_loss(dist_mob2base,BETA_F)
    eirp_bore_beta = boresight_angle(dist_mob2base,BETA_F)
    eirp_beta =  eirp_bore_sight - eirp_bore_beta
    rsl_beta = eirp_beta - tot_path_loss(dist_mob2base,BETA_F)
    return (rsl_alpha,rsl_beta)

    
    
    #no conversion needed of dbm and dbi
    
def tot_path_loss(dist_mob2base,freq):
    p_loss_V = propagation_loss(dist_mob2base,freq)
    #print "p_loss",p_loss_V
    shad_V = shadowing(dist_mob2base)
    #print shad_V
    fading_V = fading()
    #print fading_V
    return (p_loss_V + shad_V + fading_V)
    

def propagation_loss(d,f):
    d=float(d)/1000.00
    ah = (((1.1* math.log10(f) )-0.7)*hm) -((1.56*math.log10(f))-.8)
    oh = 69.55 + (26.16*math.log(f,10)) - (13.82*math.log(hb,10)) +((44.9-(6.55*math.log(hb,10)))*math.log(d,10)) -ah
    
    print "oh =",oh
    return oh


def shadowing(dist_mob2base):
    '''calculating a log-normal distribution for 10m i.e., 0,10,20,30.. 6000
        and round off the distance and ceil to the nearest ten's and pick
        up the corresponding shadowing value '''
    #converting km to m
    road_l_m = road_l*1000
    #shad_array [road_l_km /10]
    shad_dict={}
    for i in range (0,road_l_m,10):
        shad_dict[i]=numpy.random.lognormal(mean=0.0, sigma=2.0, size=None)
        #print shad_dict
    shad_key = int(math.ceil(dist_mob2base/10.0)*10)
    return shad_dict[shad_key]

def fading():
    '''compouted 10 fading values and choose the 2nd lowest value
        '''
    #Rayleigh_RV=[]
    Rayleigh_array = []
    
    for i in range(10):
        n1=np.random.normal(0,1)
        n2=np.random.normal(0,1)
        Gaussian_RV=n1+(n2*(1j))
        
        Rayleigh_RV=np.absolute(Gaussian_RV)
        Rayleigh_array.append(Rayleigh_RV)
        
    Rayleigh_array.sort()
    return 10*numpy.log10(Rayleigh_array[1])

#shadowing(10)
    
active_user={}
user_details =[]
user_non_active=[]
dropped_call={}
blocked_call=[]

#for each user that does not have a call up
#while
for i in range (2):
    p_call = lam*del_t
    x=numpy.random.random_sample()/1000
    
    if x < p_call:
        #determine the users location along the road
        user_loc = numpy.random.uniform(low=0.0, high=6000.0, size=None)
        user_details.append(user_loc)
        
        #determine users direction (north or south)
        user_dir = numpy.random.randint(2)
        user_details.append(user_dir)

        #to determine distance between the mobile and base station
        if user_dir == 0:
            #North
            distance_user = 3000 - user_loc
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base

        elif user_dir == 1:
            distance_user = user_loc - 3000
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base

        #total path loss

        call_length = int(numpy.random.exponential(scale=180) )
        #chech channel avialablity here 
        while (call_length):
            if (dist_mob2base >6000 or dist_mob2base< 0) or call_length <=0 :
                break
            rsl_mobA,rsl_mobB = rsl_eirp(dist_mob2base)
            #print "rsl=",rsl_mob6
            rsl_mob = max(rsl_mobA,rsl_mobB)
            if rsl_mobA > rsl_mobB:
                sector = "alpha"
                al_sector = "beta"
            else:
                sector = "beta"
                al_sector= "alpha"
                
            if rsl_mob >RSL_T:
                
                user_details.append(sector)
                print "rsl=",rsl_mob
                user_details.append(rsl_mob)
                if NUM_CH_A!=0:
                    user_details.append("Allocated")
                    NUM_CH_A-=1
                    active_user[i] = user_details
                else:
                    blocked_call[i]="blocked_capacity"
                    if rsl_mobB >RSL_T:
                        user_details.append(al_sector)
                        if NUM_CH_B !=0:
                            NUM_CH_B-=1
                            active_user[i] = user_details
                            #allocate channel
    
                        else:
                            blocked_call[i]="blocked_capacity"
                   
            else:
                dropped_call[i]="dropped_strength"
                break #break for loop
        call_length-=1
        #doubt north or south -15 or +15
        if user_dir == 0:
            dist_mob2base-=15
        else:
            dist_mob2base+=15

    else:
        user_non_active.append(i)
            
        
        
        

        
            
            
            

    
    

    




         
