# Application to Simulate the downlink behavior of a 3-sectored basesation

import random
import numpy
import math

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
loss = 2# db line/connector losses
AG_GAIN_TX = 15 #dbi, antenna gain
n_ch = 15 #per sector, no of traffice channels
alpha_f=860 #MHz
beta_f= 865 #MHz

#the mobile will have the following properties, some of which may be varied
hm = 1.5 #in m, height of mobile
hom = 3# db handoff margin
rsl_t = -102 #dBm mobile Rx Threshold

#users uniformly distributed
no_u =160
lam = 1800 #  2calls per hour(on average) 1800 seconds
h = 3#minutes/call (=180 seconds/call)
v= 15#m/s (=54 kph = 33.553977 mph)
# direction 50/50 chance of heading north or south


        
def eirp(dist_mob2base):
    eirp1_loss=tot_path_loss(dist_mob2base,alpha_f)
    eirp2_loss=tot_path_loss(dist_mob2base,beta_f)

    eirp_bore_sight = POW_TX*AG_GAIN_TX
    #no conversion needed of dbm and dbi
    
def tot_path_loss(dist_mob2base,freq):
    p_loss_V = propagation_loss(dist_mob2base,freq)
    shad_V = shadowing(dist_mob2base)
    fading_V = fading()
    return p_loss_V + shad_V + fading_V
    

def propagation_loss(d,f):
    ah = (((1.1* math.log10(f) )-0.7)*hm) -((1.56*math.log10(f))-.8)
    oh = 69.55 + (26.16*math.log(f,10)) - (13.82*math.log(hb,10)) +((44.9-(6.55*math.log(hb,10)))*math.log(d,10)) -ah
    
    print "oh =",oh


def shadowing(dist_mob2base):
    #converting km to m
    road_l_km = road_l*1000
    #shad_array [road_l_km /10]
    shad_dict={}
    for i in range (0,road_l_km/10,10):
        shad_dict[i]=numpy.random.lognormal(mean=0.0, sigma=2.0, size=None)
        #print shad_dict
    shad_key = math.ceil(dist_mob2base/10.0)*10
    return shad_dict[shad_key]

def fading():
    Rayleigh_RV [10]
    for i in range(0,10):
        n1=np.random.normal(0,1)
        n2=np.random.normal(0,1)
        Gaussian_RV=n1+(n2*(1j))
        Rayleigh_RV[i]=np.absolute(Gaussian_RV)
    Rayleigh_RV.sort()
    return 20*numpy.log10(Rayleigh_RV[1])

#shadowing(10)
    
        
'''
#for each user that does not have a call up
for i in range (no_u):
    p_call = lam*del_t
    x=random.random()
    if x < p_call:
        #determine the users location along the road
        user_loc = numpy.random.uniform(low=0.0, high=6.0, size=None)
        #determine users direction (north or south)
        user_dir = numpy.random.randint(2)

        #to determine distance between the mobile and base station
        if user_dir == 0:
            #North
            distance_user = 3 - user_loc
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base

        elif user_dir == 1:
            distance_user = user_loc - 3
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            print dist_mob2base

        #total path loss

            eirp_mob = eirp(dist_mob2base)
'''          
