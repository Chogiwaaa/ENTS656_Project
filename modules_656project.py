# Application to Simulate the downlink behavior of a 3-sectored basesation

import random
import numpy
import numpy as np
import math
from numpy import ndarray

from numpy import (array, dot, arccos)
from numpy.linalg import norm

#basic paramaeters
ROAD_L=6 #km
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
shad_dict={}

def shadow_pre_cal():
    '''calculating a log-normal distribution for 10m i.e., 0,10,20,30.. 6000
        and round off the distance and ceil to the nearest ten's and pick
    up the corresponding shadowing value '''
    #converting km to m
    road_l_m = ROAD_L*1000
    for i in range (0,road_l_m,10):
        shad_dict[i]=numpy.random.normal(0.0, 2.0, size=None)
    

def boresight_angle(d,sector):
    if d >=3000:
        u = array([20,3000-d])
    if d <3000:
        u = array([20,3000-d])
    if sector == 860:
        v = array([0,1])
    elif sector == 865:
        v = array([0.866,-0.5])
        
    c = dot(u,v)/(norm(u)*norm(v))
    angle_boresight = int(np.degrees(arccos(c)))
    return s[1][angle_boresight]
    
    '''. The RSL will be determined by computing the EIRP in the direction of
    the user from each sector and subtracting the path loss obtained by modelling the communications channel for that sector.
        '''
def rsl_eirp(dist_mob2base,user_loc):
    eirp_bore_sight = POW_TX+AG_GAIN_TX-LOSS
    eirp1_loss=tot_path_loss(dist_mob2base,ALPHA_F)
    eirp_bore_alpha = boresight_angle(user_loc,ALPHA_F)
    eirp_alpha =  eirp_bore_sight - eirp_bore_alpha
    x,y,z = tot_path_loss(dist_mob2base,ALPHA_F)
    rsl_alpha = eirp_alpha - x +y +z
    eirp2_loss=tot_path_loss(dist_mob2base,BETA_F)
    eirp_bore_beta = boresight_angle(user_loc,BETA_F)
    x,y,z = tot_path_loss(dist_mob2base,BETA_F)
    eirp_beta =  eirp_bore_sight - eirp_bore_beta
    rsl_beta = eirp_beta - x+y+z
    return (rsl_alpha,rsl_beta)
    
    #no conversion needed of dbm and dbi
    
def tot_path_loss(dist_mob2base,freq):
    p_loss_V = propagation_loss(dist_mob2base,freq)
    shad_V = shadowing(dist_mob2base)
    fading_V = fading()
    return (p_loss_V , shad_V , fading_V)
    
    '''Use the Okamura-Hata model adjusted for a small city.
        Include the mobile height term as required by the model.
        Note that you will need to compute the distance from the mobile to
        the basestation to get the propagation loss.
        '''
def propagation_loss(d,f):
    d=float(d)/1000.00
    ah = (((1.1* math.log10(f) )-0.7)*hm) -((1.56*math.log10(f))-.8)
    oh = 69.55 + (26.16*math.log(f,10)) - (13.82*math.log(hb,10)) +((44.9-(6.55*math.log(hb,10)))*math.log(d,10)) -ah
    return oh


def shadowing(dist_mob2base):
    '''calculating a log-normal distribution for 10m i.e., 0,10,20,30.. 6000
        and round off the distance and ceil to the nearest ten's and pick
        up the corresponding shadowing value '''
  
    shad_key = int(math.ceil(dist_mob2base/10.0)*10)
    return shad_dict[shad_key]


def fading():
    '''compouted 10 fading values and choose the 2nd lowest value
        '''
    Rayleigh_array = []
    for i in range(10):
        n1=np.random.normal(0,1)
        n2=np.random.normal(0,1)
        Gaussian_RV=n1+(n2*(1j))
        Rayleigh_RV=np.absolute(Gaussian_RV)
        Rayleigh_array.append(Rayleigh_RV)
    Rayleigh_array.sort()   
    return 10*numpy.log10(Rayleigh_array[-2])

         
