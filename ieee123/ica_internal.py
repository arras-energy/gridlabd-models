#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 12:17:43 2020

@author: saraborchers
"""


import pandas as pd
import re
import gridlabd
import pdb
import math

obj_list = []
prop_list = []
viol_val_list = []
viol_time_list = []


def on_init(t):
    print('\ninitializing\n')
    '''
    Based on user-selected options, thresholds are set for each relevant 
    property of each object. The violation data frame is populated with 
    properties to check with each commit, and their thesholds. 
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
    thresh_dict = {'underground_line':{'rating.summer.continuous':[1,'rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C'],
                                          'rating.winter.continuous':[1,'rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C']},
                         'overhead_line':{'rating.summer.continuous':[1,'rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C'],
                                          'rating.winter.continuous':[1,'rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C']},
                         'transformer':{'power_rating':[1,'rating','power_in','power_out'],
                                        'powerA_rating':[1,'rating','power_in_A','power_out_A'],
                                        'powerB_rating':[1,'rating','power_in_B','power_out_B'],
                                        'powerC_rating':[1,'rating','power_in_C','power_out_C'],
                                        'primary_voltage':[1,'deviation'],
                                        'secondary_voltage':[1,'deviation']},
                         'regulator':{'raise_taps':[1,'limit','tap_A','tap_B','tap_C'],
                                      'lower_taps':[1,'limit','tap_A','tap_B','tap_C'],
                                      'continuous_rating':[0,'rating','current_out_A','current_out_B','current_out_C','current_in_A','current_in_B','current_in_C']},
                         'substation':{'nominal_voltage':[0,'deviation']},
                         'triplex_meter':{'nominal_voltage':[0,'deviation', 'measured_voltage_1', 'measured_voltage_2', 'measured_voltage_12', 'measured_voltage_N']},
                         'meter':{'nominal_voltage':[0,'deviation']}}
    
    ###########################################################################
    ################# SET THRESHOLDS & FILL VIOLATION DATAFRAME ###############
    ###########################################################################

    object_list = gridlabd.get("objects")
    df_dict = {}

                                          
    for obj in object_list:
        
        obj_class = gridlabd.get_object(obj).get('class')
        if obj_class in thresh_dict:                                       
            
            thresh_class_dict = thresh_dict.get(obj_class)                        
            #TODO: Make sure obj names all either do or do not have ica_      
            
            # Make a list of properties to check for that class            
            init_prop_list = list(thresh_class_dict.keys())
                                                                                     
            # Iterate through those properties, appending to viol_df
            for init_prop in init_prop_list:
                
                # First, get the library value of the given property.
                if thresh_class_dict.get(init_prop)[0] == 0:
                    lib_val = gridlabd.get_value(obj, init_prop)
                else:
                    config = gridlabd.get_value(obj, 'configuration')
                    lib_val = gridlabd.get_value(config, init_prop)
                
                non_decimal = re.compile(r'[^\d.]+')
                lib_val = float(non_decimal.sub('',lib_val))
                
                # Then, use the user input to set the library value to a threshold
                user_input = gridlabd.get_global(obj_class + '.' + init_prop)
                thresh_min = 0.0
        

                # If the user input is a percentage, set the threshold to be a % or a +- range of its library value
                if '%' in user_input:
                    if 'taps' in init_prop:
                        gridlabd.warning('%s, class %s should not have a percentage as a threshold.' % (obj,obj_class))
                        continue

                    user_input = float(user_input.strip('%'))/100  
                    if user_input < 0:
                        gridlabd.warning('User input for %s, class %s must be a non-negative number or percentage, blank, or X.' % (obj,obj_class))
                        continue

                    if thresh_class_dict.get(init_prop)[1] == 'rating':
                        thresh_max = lib_val * user_input
                      
                    elif thresh_class_dict.get(init_prop)[1] == 'deviation':
                        thresh_max = lib_val * (1.0 + user_input)
                        thresh_min = lib_val * (1.0 - user_input)                        
                                        
                
                # If the user input a number, set the threshold to that number.
                elif user_input.isnumeric():
                    user_input = float(user_input)
                    if user_input < 0:
                        gridlabd.warning('User input for %s, class %s must be a non-negative number or percentage, blank, or X.' % (obj,obj_class))
                        continue

                    if 'taps' in init_prop:
                        gridlabd.warning('%s, class %s should not have a number as a threshold.' % (obj,obj_class))
                        continue
                                        
                    thresh_max = float(user_input)
                
                # If the user input is blank, set the threshold to the library value.
                elif user_input == '""':
                    thresh_max = lib_val
                
                # If the user input is an 'X', do not track violations for that property.
                elif user_input.lower() == 'x':
                    continue

                # Identify the commit properties associated with the obj's init properties
                commit_prop_list = thresh_class_dict.get(init_prop)[2:]
                # Append one row to the viol_df for each commit property for each obj                
                for idx, commit_prop in enumerate(commit_prop_list):
                    # print(pd.DataFrame({'Object':[str(obj)],'Class':str(obj_class),'Init Prop':init_prop,'Min Thresh':thresh_min,'Max Thresh':thresh_max,'Commit Prop':str(commit_prop)},index=[idx]))
                    df_dict[str(obj)+'.'+init_prop+'.'+commit_prop] = pd.DataFrame({'Object':[str(obj)],'Class':str(obj_class),'Init Prop':init_prop,'Min Thresh':thresh_min,'Max Thresh':thresh_max,'Commit Prop':str(commit_prop),'Violation Value':None, 'Violation Time':None})                                                      
    
    global viol_df 
    viol_df = pd.concat(list(df_dict.values()),ignore_index=True)
    viol_df.to_csv('viol_df_orig.csv', index=False)   

    return True
      

'''
ON_COMMIT
For each key in master dictionary, get the value for each property and compare it to the threshold.
If threshold is exceeded, record the object, property, and value, and exit.

Option 1: 
Record the first violation of each object within the violation dataframe. 
The entire dataframe, with all objects (violated or not) is saved to a csv.

Option 2:
Record the first violation of each object in a new dataframe, which only tracks
the object, the property violated, the value of the violation, and the time.

Option 3:
Same as Option 2, except ALL violations are recorded, rather than just the first.
            
'''

def on_commit(t):
    global obj_list
    global prop_list
    global viol_val_list
    global viol_time_list
    

    option = gridlabd.get_global('violation_option')

    for index, row in viol_df.iterrows():
        # Only check for a violation if object hasn't already had a violation
        if option == '3' or row['Violation Time'] == None:
            # Get the real-time value for the property
            str_value = gridlabd.get_value(row['Object'], row['Commit Prop'])

            if 'j' in str_value:
                c_val = complex(str_value[:-2])
                value = math.sqrt(c_val.real**2 + c_val.imag**2)
            else:
                value = float(re.sub("[^0-9]","",str_value))
            
            # Compare it against the min and max threshold
            if value > row['Max Thresh'] or value < row['Min Thresh']:
                print('obj %s IS violating'%(row['Object']))

                viol_df.at[index,'Violation Time'] = gridlabd.get_global("clock")
                viol_df.at[index,'Violation Value'] = value
                
                if option != '1':
                    obj_list.append(row['Object'])
                    prop_list.append(row['Init Prop'] + '|' + row['Commit Prop'])
                    viol_val_list.append(value)
                    viol_time_list.append(gridlabd.get_global("clock"))

    return True

def on_term(t):
    print("\nterminating")
    option = gridlabd.get_global('violation_option')

    
    if option == '1':
        viol_df.to_csv('viol_df_opt1.csv', index=False)   

    else:
        pd.DataFrame({'Object':obj_list, 'Property':prop_list, 'Violation Value':viol_val_list, 'Violation Time':viol_time_list}).to_csv('viol_df_opt'+option+'.csv', index=False) 
    
    return None

