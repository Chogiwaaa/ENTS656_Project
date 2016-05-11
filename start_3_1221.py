'''A Python application which will simulate the downlink behavior of a
    3-sectored basestation along a road.
    Author Ranjitha Ratchagan
    '''

import random
import numpy
import numpy as np
import math
from numpy import ndarray
from numpy import (array, dot, arccos)
from numpy.linalg import norm
import sys
'''The antenna discrimination values are given in dB and supplied by the
    manufacturer for each antenna model
'''
my_path ='/Users/ranjitha/Desktop/2SEM/ENTS656'
sys.path.append(my_path)
import modules_656project as md


#basic paramaeters
road_l=6 #km
del_t=1 #sec
tot_sim_t= 1 # 1 or more hrs, total simulation time
TOT_SIM_SEC = tot_sim_t*3600
p_call =1800

#each basestation may have the following propertities, some of which may be varied
hb= 50 #in m, this is the basestation anyenna height
# change to km loc_b = 20 # m west of the road at the midpoint of the road(3 km if the road is 6 km)
# 1 meter = 0.001 km
loc_b = 20

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
NO_USERS =160
lam = float(2)/float(3600) #  2calls per hour(on average) 1800 seconds 2/3600
h = 3#minutes/call (=180 seconds/call)
V_SPEED= 15#m/s (=54 kph = 33.553977 mph)
# direction 50/50 chance of heading north or south
path = "/Users/ranjitha/Downloads/antenna_pattern.txt"
s = numpy.loadtxt(path, unpack=True)


''' Data Structures to hold call details, active_users contains all the call attempts
user details has the details of the user active_users={517: [{'user_loc': 5500}, {'time': 50},
{'user_dir': 'south'}, {'user_distance': 1976.0684225631585}, {'sector': 'Beta'}, {'call_status': 'Call Established'}, {'call length': 5000}, {'rsl': -81.112321193743767}]}
    '''
global active_users
active_users={}
failed_users={}
user_non_active=[]
dropped_call={}
blocked_call=[]
global archieve_users
archieve_users=[]
user_Dir = ''
serving_sector=''
global u  

def user_makes_new_call(i,j):
    '''For each user that does not have a call up, a new call is made
    '''
    global active_users
    x = numpy.random.random_sample()
    p_call = 1.0/1800.0
    if x<= p_call:
        user_details =[]
        ''' Initiate a call
                '''
        '''determine the users location along the road
            '''
        user_loc = np.random.uniform(low=0.0, high=6000.0, size=None)
        user_details.append({"user_loc":user_loc})
        '''determine users direction (north or south)               '''
        user_dir = numpy.random.randint(2)
        if user_dir ==0:
            user_details.append({"user_dir":"north"})
        elif user_dir ==1:
            user_details.append({"user_dir":"south"})
        '''to determine distance between the mobile and base station
            '''
        user_details.append({"time":j})
        if user_loc < 3000:
            distance_user = 3000 - user_loc
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
        elif user_loc> 3000:
            distance_user = user_loc - 3000
            dist_mob2base = math.sqrt((loc_b**2 + distance_user**2))
            user_details.append({"user_distance":dist_mob2base})                  
            '''Find the RSL at the mobile from each sector
               md--->modules_656project.py '''
        rsl_sectorA,rsl_sectorB = md.rsl_eirp(dist_mob2base,user_loc)
        '''RSLSERVER is greater than or equal to the RSL threshold
            '''
        rsl_mob = max(rsl_sectorA,rsl_sectorB)
        call_length = int(numpy.random.exponential(scale=180))
        ''' If rsl is less than threshold then the call is dropped
            '''
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
            failed_users[i]=user_details
            return 0
        else:
            ''' maximum rsl among alpha and beta is taken as the serving sector
                '''
            if rsl_sectorA > rsl_sectorB:
                sector = "alpha"
                #user_details.append(sector)
                if md.NUM_CH_A >0 and md.NUM_CH_A <=15 :
                    user_details.append({"sector":sector})
                    md.NUM_CH_A -=1
                    user_details.append({"call_status":"Call Established"})
                    user_details.append({"call length":call_length})
                    user_details.append({"rsl":rsl_sectorA})
                    active_users[i]=user_details
                else:
                    user_details =[]
                    user_details.append({"sector": sector})
                    user_details.append({"call_status":"Call Failed"})
                    user_details.append({"call_blocked":sector})
                    user_details.append({"capacity":"Insufficent_Capacity"})
                    failed_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    if rsl_sectorB > RSL_T:
                        sector = "beta"
                        if md.NUM_CH_B >0 and md.NUM_CH_B <=15 :
                            user_details.append({"sector":sector})
                            md.NUM_CH_B = md.NUM_CH_B-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorB})
                            active_users[i]=user_details
                            
            else:
                sector = "beta"
                if md.NUM_CH_B >0 and md.NUM_CH_B <=15 :
                    user_details.append({"sector":sector})
                    md.NUM_CH_B = md.NUM_CH_B-1
                    user_details.append({"call_status":"Call Established"})
                    user_details.append({"call length":call_length})
                    user_details.append({"rsl":rsl_sectorB})
                    active_users[i]=user_details
                else:
                    user_details =[]
                    user_details.append({"sector": sector})
                    user_details.append({"call_status":"Call_Failed"})
                    user_details.append({"call blocked":sector})
                    user_details.append({"capacity":"Insufficent Capacity"})
                    failed_users[i]=user_details
                    '''other sector has sufficient signal strength to be
                        the serving sector and greater than threshold
                        '''
                    
                    if rsl_sectorA > RSL_T:
                        sector = "alpha"
                        if md.NUM_CH_A >0 and md.NUM_CH_A <=15 :
                            user_details.append({"sector":sector})
                            md.NUM_CH_A = md.NUM_CH_A-1
                            user_details.append({"call_status":"Call Established"})
                            user_details.append({"call length":call_length})
                            user_details.append({"rsl":rsl_sectorA})
                            active_users[i]=user_details
                    
'''For each user who DOES have a call up
    '''
def user_has_call():
    user_dir =''
    serving_sector =''
    new_user_loc=0
    global active_users
    global archieve_users
    ''' Computing location, new rsl , call length for every caller
        '''
    for each_users in active_users:

        is_handoff=2
        if len(active_users[each_users]) == 0:
            break
        else:
            ''' Obtaing the user direction, sector, user location
                '''
            for details2 in active_users[each_users]:
                for k,v in details2.items():
                    if k == 'user_dir':
                        user_dir = v
            for details3 in active_users[each_users]:
                for key,value in details3.items():
                    if key == 'sector':
                        serving_sector = value
            '''Re calculating the user location as he travels
                '''
            for details4 in active_users[each_users]:
                for key,value in details4.items():
                    if key == 'user_loc':
                        if user_dir == 'north' and value >0 :
                            details4[key]=value-V_SPEED
                        elif user_dir == 'south' and value <6000 :
                            details4[key]=value+V_SPEED
                        '''user’s location has moved beyond the ends of the road.
                            If so, then we assume the user has handed off to another basestation
                            further down the road. Record this as a successful call on this sector 
                            And a channel is made free in the sector
                            '''
                        if value <0 or value >6000:
                            active_users[each_users].append({"Call_exit_status":"Successful call"})
                            archieve_users.append(active_users[each_users])
                            del active_users[each_users]
                            #active_users[each_users] = []
                            if serving_sector == 'alpha':
                                md.NUM_CH_A +=1
                            else:
                                md.NUM_CH_B +=1
                            
            '''If the user’s call timer has run out, then the call completes normally.
                Record this as a successful call on that sector
                '''
            try:
                for details5 in active_users[each_users]:
                    for key,value in details5.items():
                        if key == 'call length':
                            if value > 0:
                                details5[key]=value-1
                            elif value == 0:
                                active_users[each_users].append({"Call_exit_status":"Successful call"})
                                archieve_users.append(active_users[each_users])
                                del active_users[each_users] 
                                #active_users[each_users] = []
                                if serving_sector == 'alpha':
                                    md.NUM_CH_A +=1
                                else:
                                    md.NUM_CH_B +=1
            except KeyError:
                    break
                            
            '''Calculate the RSLSERVER. This will be at a new location,
                with new EIRP, path loss, shadowing and fading values.
                '''
            try:
                for details1 in active_users[each_users]:
                    for key,value in details1.items():
                        if key == 'user_loc':
                            new_user_loc = value
            except KeyError:
                break
            if new_user_loc > 3000:
                dist2mobbase_new = new_user_loc - 3000
            else:
                dist2mobbase_new = 3000-new_user_loc
            dist_mob2base_send = math.sqrt((loc_b**2 + dist2mobbase_new**2))
            rsl_sectorA,rsl_sectorB = md.rsl_eirp(dist_mob2base_send,new_user_loc)
            '''RSLSERVER is greater than or equal to the RSL threshold                               '''
            if serving_sector == "alpha":
                rsl_mob = rsl_sectorA
            else:
                rsl_mob = rsl_sectorB
            for details8 in active_users[each_users]:
                for key,value in details8.items():
                    if key == 'rsl':
                        details8[key]=rsl_mob
            
            '''If RSLSERVER < RSLTHRESH the call drops.
                Record this as a dropped call due to signal strength for the
                serving sector. 
                '''
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
                failed_users[each_users]=(active_users[each_users])
                #active_users[each_users] = []
                del active_users[each_users]
                if serving_sector == 'alpha':
                    md.NUM_CH_A +=1
                else:
                    md.NUM_CH_B +=1
                '''If RSLSERVER ≥ RSLTHRESH, compute the RSL for the other sector,
                RSLOTHER. If RSLOTHER > RSLSERVER +HOm, then there is a
                potential handoff.
                    '''
                '''Hand off initiated at alpha sector to beta
                    '''
            else:
                if is_handoff >1:
                    if serving_sector == 'alpha':
                        if rsl_sectorB >= rsl_sectorA + HOM:
                            #print "handoff happenning"
                            active_users[each_users].append({"hand_off": serving_sector})
                            if md.NUM_CH_B >0 and md.NUM_CH_B <=15:
                                for details6 in active_users[each_users]:
                                    for key,value in details6.items():
                                        if key == 'sector':
                                            details6[key]="beta"
                                        if key == 'rsl':
                                            details6[key] = rsl_sectorB
                                                
                                active_users[each_users].append({"hand_off_status": "Successful"})
                                is_handoff +=1
                                md.NUM_CH_A +=1
                                md.NUM_CH_B -=1
                            else:
                                active_users[each_users].append({"hand_off_status": "Failure"})
                                is_handoff +=1
                        '''Hand off initiated beta sector to alpha
                            '''
                    else:
                        if rsl_sectorA >= rsl_sectorB + HOM:
                            #print "handoff happenning"
                            active_users[each_users].append({"hand_off": serving_sector})
                            if md.NUM_CH_A >0 and md.NUM_CH_A <=15:
                                for details7 in active_users[each_users]:
                                    for key,value in details7.items():
                                        if key == 'sector':
                                            details7[key]="alpha"
                                        if key == 'rsl':
                                            details7[key] = rsl_sectorA
                                active_users[each_users].append({"hand_off_status": "Successful"})
                                is_handoff +=1
                                md.NUM_CH_A -=1
                                md.NUM_CH_B +=1
                            else:
                                active_users[each_users].append({"hand_off_status": "Failure"})
                                is_handoff +=1

''' Probablity of a call = λ*ΔT ; probability of a call is taken from 1 to 1800
    which will be 1 in 1800 and checked with a random number say 1800 
    '''
'''Function for the flow of program from initiating a new call to servicing an existing call
    '''

def main():
    print "Welcome to Python application which will simulate the downlink behavior of a 3-sectored basestation"
    no_calls_can_make = 0
    active=0
    md.shadow_pre_cal()
    NO_USERS = 160
    archieve_users_list=[]
    num=0
    '''Initial simulation of 1 hourTOT_SIM_SEC
        '''
    for i in range (1,(3600+1)*6):
        if (i==3600 or i==3600*2 or i==3600*3 or i==3600*4 or i==3600*5 or i==3600*6):
            print "Statistics for ",i/3600,"hour"
            fo='file'+str(i)
            stats_num_of_call("beta")
            stats_num_of_call("alpha")
            f = open( fo, 'w' )
            f.write(repr(active_users))
            f.close()
            
        '''160 users always on the road
        time        '''
        if(len(active_users)!=0):
            user_has_call()
        for j in range (NO_USERS):
            user_makes_new_call(num,i)
            num+=1

'''Function to print out the stats of the user calls
    '''
def stats_num_of_call(sector_name):
    global active_users
    global archieve_users
    number_calls_active=0
    number_calls_archieve=0
    tot_calls=0
    hand_off=0
    success_call=0
    hand_off_F = 0
    hand_off_S_A = 0
    hand_off_S_Ar = 0
    drop_capacity = 0
    drop_strength =0
    sector_found=''
    sector_found1=''
    '''the number of channels currently in use 
        '''
    if sector_name == "alpha":
        no_ch_use = 15 - md.NUM_CH_A
    else:
        no_ch_use = 15 - md.NUM_CH_B
    '''the number of active calls, successful calls, hand offs, dropped calls
        '''
    for each_users in active_users:
        for details2 in active_users[each_users]:
            for key,value in details2.items():
                if key == 'sector' and value == sector_name:
                    number_calls_active +=1
                    sector_found = value
                if key =='hand_off_status' and value == 'Successful'and sector_found == sector_name :
                    hand_off_S_A = hand_off_S_A+1
                if key =='hand_off_status' and value == 'Failure'and sector_found == sector_name :
                    hand_off_F = hand_off_F+1
                if key =='capacity' and value == 'Insufficent_Capacity'and sector_found == sector_name :
                    drop_capacity +=1
                if key =='Call Dropped"' and value == 'Signal Strength' and sector_found == sector_name :
                    drop_strength +=1
    '''To find the sector and then extract the number of dropped calls in each sector
        '''
    for each_users in failed_users:
        for details1 in failed_users[each_users]:
            for key,value in details1.items():
                if key == 'sector':
                    sector_found1 = value
        for details9 in failed_users[each_users]:
            for key,value in details1.items():
                if key =='capacity' and sector_found1 == sector_name :
                    drop_capacity +=1
                if key =='Call Dropped"' and value == 'Signal Strength' and sector_found1 == sector_name :
                    drop_strength +=1
    '''The number of active calls in archieved list
        '''
    for each_users in range(0,len(archieve_users)):
        for details3 in archieve_users[each_users]:
            for key,value in details3.items():
                if  key == 'sector' and value == sector_name:
                    sector_found = value
                    number_calls_archieve +=1
                if key =='hand_off_status' and value == 'Successful'and sector_found == sector_name :
                    hand_off_S_Ar = hand_off_S_Ar+1
                if key =='hand_off_status' and value == 'Failure'and sector_found == sector_name :
                    hand_off_F = hand_off_F+1
                if key =='capacity' and value == 'Insufficent_Capacity'and sector_found == sector_name :
                    drop_capacity +=1   
                if key =='Call Dropped' and value == 'Signal Strength' and sector_found == sector_name :
                    drop_strength +=1
    tot_calls = number_calls_active + number_calls_archieve
    print "*************", sector_name , "**************"
    print ("The number of channels currently ",no_ch_use)
    print ("The number of call attempts ",tot_calls)
    print ("The number of successful calls",number_calls_archieve)
    print ("The number of successful handoffs ", hand_off_S_A+hand_off_S_Ar)
    print ("The number of handoff failures into and out of each sector",hand_off_F)
    print ("The number of call drops  due to capacity",drop_capacity )
    print ("The number of call drops due to low signal strength ",drop_strength )

    

'''Function call to the main function to intiate a call and service it
    '''
main()
'''Function calls to calculate the stats of the base station according to the sector
    '''
#stats_num_of_call("beta")
#stats_num_of_call("alpha")


'''Writing the respective variables active_users , archieve_users and
    failed_users into a file in the current directory
    '''
f = open( 'file1.txt', 'w' )
f.write(repr(archieve_users))
f.close()
f = open( 'file2.txt', 'w' )
f.write(repr(active_users))
f.close()
f = open( 'file3.txt', 'w' )
f.write(repr(failed_users))
f.close()

 
                
            
                
        


        
