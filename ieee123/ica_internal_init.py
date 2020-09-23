#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 12:17:43 2020

@author: saraborchers
"""


import pandas as pd
import re
import gridlabd


viol_df = pd.DataFrame(columns = ['Object','Class','Init Prop','Min Thresh','Max Thresh','Commit Prop','Value','Violation?','Time'])


def on_init(t):
    '''
    Based on user-selected options, thresholds are set for each relevant 
    property of each object. A master dictionary is created with all objects, 
    properties to check, and their thresholds.
    '''  
    
    ###########################################################################
    ######################### READ USER INPUTS ################################
    ###########################################################################
    
    '''
    There are 2 options for how to read in a csv on initialization:
    1) Global thresholds are set through csv converter.
    2) Read config file directly into script, creating a global for each entry.
    
    Option 1 is currently default, Option 2 is commented out. 
    '''
    
    # Option 2
    # config_globals = pd.read_csv("ica_config_file.csv")
    # for index in range(len(config_globals)):
    #     gridlabd.set_global("ica_" + config_globals.iloc[index, 0], \
    #                         str(config_globals.iloc[index, 1]))

    ###########################################################################
    ######################### CREATE MASTER DICTIONARY ########################
    ###########################################################################

    # In thresh_dict, key = class, val = dictionary w/ info to set thresh
    #   rating: set the threshold as a % of the max rating
    #   deviation: set the threshold as a +-% from the nominal rating.

    #Todo: add commit props as list for init props
    thresh_dict = {'underground_line':{'configuration':1,
                                          'rating.summer.continuous':['rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C'],
                                          'rating.winter.continuous':['rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C']},
                         'overhead_line':{'configuration':1,
                                          'rating.summer.continuous':['rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C'],
                                          'rating.winter.continuous':['rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C']},
                         'transformer':{'configuration':1,
                                        'power_rating':['rating','power_in','power_out'],
                                        'powerA_rating':['rating','power_in_A','power_out_A'],
                                        'powerB_rating':['rating','power_in_B','power_out_B'],
                                        'powerC_rating':['rating','power_in_C','power_out_C'],
                                        'primary_voltage':['deviation'],
                                        'secondary_voltage':['deviation']},
                         'regulator':{'configuration':1,
                                      'raise_taps':['limit','tap_A','tap_B','tap_C'],
                                      'lower_taps':['limit','tap_A','tap_B','tap_C']},
                         'substation':{'configuration':0,
                                       'nominal_voltage':['deviation']},
                         'triplex_meter':{'configuration':0,
                                          'nominal_voltage':['deviation']},
                         'meter':{'configuration':0,
                                  'nominal_voltage':['deviation']}}
    
    
    ###########################################################################
    ################# SET THRESHOLDS & FILL VIOLATION DATAFRAME ###############
    ###########################################################################

    global viol_df
    object_list = gridlabd.get("objects")
                                          
    for obj in object_list:
        
        obj_class = gridlabd.get_object(obj).get('class')                     
                                                                                   
        if obj_class in thresh_dict:                                       
            
            thresh_class_dict = thresh_dict.get(obj_class)                        
            #TODO: Make sure obj names all either do or do not have ica_      
            
            # Make a list of properties to check for that class            
            init_prop_list = list(thresh_class_dict.keys())                               
            del init_prop_list[0]                                                                             
                                                                                     
            # Iterate through those properties, appending to viol_df
            for init_prop in init_prop_list:
                
                
                # First, get the library value of the given property.
                if thresh_class_dict.get('configuration') == 0:
                    lib_val = gridlabd.get_value(obj, init_prop)
                else:
                    config = gridlabd.get_value(obj, 'configuration')
                    lib_val = gridlabd.get_value(config, init_prop)
                
                non_decimal = re.compile(r'[^\d.]+')
                lib_val = float(non_decimal.sub('',lib_val))
                
                # Then, use the user input to set the library value to a threshold
                user_input = gridlabd.get_global(obj_class + '.' + init_prop)
                #Todo: Set min_thresh to a reasonable value
                thresh_min = -1000000
        
                # If the user input is a percentage, set the threshold to be a % or a +- range of its library value
                if '%' in user_input:
                    user_input = float(user_input.strip('%'))/100  
                    if thresh_class_dict.get(init_prop)[0] == 'rating':
                        thresh_max = lib_val * user_input
                      
                    elif thresh_class_dict.get(init_prop)[0] == 'deviation':
                        thresh_max = lib_val * (1.0 + user_input)
                        thresh_min = lib_val * (1.0 - user_input)                        
                                        
                    else:
                        gridlabd.warning('%s, class %s should not have a percentage as a threshold.' % (obj,obj_class))
                
                #TODO: I don't remember meaning of raise/lower taps being a limit
                # If the user input a boolean, set the threshold to the library value
                elif thresh_class_dict.get(init_prop)[0] == 'limit':
                    thresh_max = lib_val

                # If the user didn't input a % or a boolean, set the threshold to the user input
                else:
                    thresh_max = user_input
                    
                # Identify the commit properties associated with the obj's init properties
                commit_prop_list = thresh_class_dict.get(init_prop)
                del commit_prop_list[0]
                
                # Append one row to the viol_df for each commit property for each obj                
                for commit_prop in commit_prop_list:                                                                        
                    viol_df = viol_df.append({'Object':str(obj),'Class':str(obj_class),'Init Prop':init_prop,'Min Thresh':thresh_min,'Max Thresh':thresh_max,'Commit Prop':str(commit_prop)})                                                                                               
                    
    return True
      

'''
ON_COMMIT
For each key in master dictionary, get the value for each property and compare it to the threshold.
If threshold is exceeded, record the object, property, and value, and exit.
'''

def on_commit(t):

    # 1. Threshold value -> master ica_dictionary (set by user)
    # 2. Simulation result -> object in GridLAB-D-> dictionary
    # 3.

    '''
    Note: This code is not complete! Needs to be restructured to reflect changes to on_init.
    This script should get current values for each property of interest for each object, and
    compare it to the thresholds created in on_init. 
    
    If threshold is exceeded, record the object, property, and value, and exit.



    '''
    '''
    
     for node in nodes:
        set the current value to the maximum with no violation 
        set the voltage value to the maximum with no violation
            
            Simplified: 
                Load setting (Voltage and current)
                at this node reduce this specific load
                
                gridlabd.set(inverter)['voltaje'] = 2000
        
        and runs the power flow simulation for the next node to be analyzed
     
        ICA a current and voltage value 
    
    '''
#     print('Commit model start')
#     for obj in master_dict:
#         obj_dict = master_dict.get(obj)
#         for prop in obj_dict:
#         #Get the current value for the given property
#             print(prop) #This is a strg
#             # prop_check = prop.replace('_min','') Commented out new variable defined prop_check
#             prop.replace('_min', '')
#             #print(prop)
#             #possible if statement missing CHECK
#             #prop_check = prop_check.replace('_max','')  #Commented out associated with prop_check
#             #val = gridlabd.get_value(obj, prop_check)  #Commented out associated with prop_check

#             #Convert the string to a float
#             #non_decimal = re.compile(r'[^\d.]+')    #Commented out to avoid fatal error in run
#             #val = float(non_decimal.sub('',val))

# #            gridlabd.warning(obj)
# #            gridlabd.warning(prop_check)
# #            gridlabd.warning(str(val))

# #   Comented out fatal error in run
# #             if '_min' in prop and val < obj_dict.get(prop):
# #                 pass
# #                    #Record the time, object, property, and value.
# #                #TODO: Check the keys in this dictionary - code below is placeholder
# # #                obj_props = gridlabd.get_object(obj)
# # #                recorder.write('%s,%s,%s\n' % (obj_props['time'],obj_props['name'],obj_props['property'],obj_props['value']))
# #             #if 'n_min' not in prop and val > obj_dict.get(prop):  #typo in the line
# #             if '_min' not in prop and val > obj_dict.get(prop):
# #                 pass

#         # Run the model until al the power injection sequences are completed
#         # Run the model until the previous ica value is the same as the last calculated
    return True

###DUMP###
#    
#            if 'ica_' == obj_class[0:4]:
#                print('it has ica_ prefix')
#            else:
#                print('no ica_ prefix')          
#           
    # info_test = open("master_dictionary.csv","w") # Dump to a file checking purposes 
    # info_test.write(str(master_dict))
    # gridlabd.warning(str(master_dict)) 
    # recorder = open("results.csv","w")
    # recorder.write("time, object, property, value")
 
