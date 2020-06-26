import pandas as pd
import re

#In master_dict, key = obj, val = obj_dict
master_dict = {}
global recorder

def on_init(t):
    '''
    Based on user-selected options, thresholds are set for each relevant property of each object.
    A master dictionary is created with all objects, properties to check, and their thresholds.

    There are 2 options for how to read in a csv on initialization:
    1) Global thresholds are set through csv converter.
    2) Read config file directly into script, creating a global for each entry.
    
    Option 1 is currently default, Option 2 is commented out. 
    '''  
    
    #Option 2
#    config_globals = pd.read_csv("ica_config_file.csv")
#    for index in range(len(config_globals)):
#        gridlabd.set_global("ica_" + config_globals.iloc[index, 0], str(config_globals.iloc[index, 1]))

    #Create a dict of classes to check on_commit. Key = class. Value = information on how to find library properties of class.
        #RATING: set the threshold as a % of the max rating. DEVIATION: set the threshold as a +-% from the nominal rating.
    ica_class_dict = {'underground_line':{'configuration':1, 'rating.summer.continuous':'rating','rating.winter.continuous':'rating'},\
                         'overhead_line':{'configuration':1, 'rating.summer.continuous':'rating', 'rating.winter.continuous':'rating'},\
                         'transformer':{'configuration':1, 'power_rating':'rating', 'powerA_rating':'rating', 'powerB_rating':'rating', 'powerC_rating':'rating', 'primary_voltage':'deviation', 'secondary_voltage':'deviation'},\
                         'regulator':{'configuration':1, 'raise_taps':'limit', 'lower_taps':'limit'},\
                         'substation':{'configuration':0, 'nominal_voltage':'deviation'},\
                         'triplex_meter':{'configuration':0, 'nominal_voltage':'deviation'},\
                         'meter':{'configuration':0, 'nominal_voltage':'deviation'}}
    
    object_list = gridlabd.get("objects")
    
    #In obj_dict, key = property & val = threshold. One for each object.
    obj_dict = {}
    
    for obj in object_list:
        obj_dict.clear()
        #Get the class of the object
        obj_class = gridlabd.get_object(obj).get('class')
        
        if obj_class in ica_class_dict:
            class_dict = ica_class_dict.get(obj_class)
            #TODO: Make sure obj names all either do or do not have ica_
            #Make a list of properties to check for that class
            prop_list = list(class_dict.keys())
            del prop_list[0]

            #Iterate through those properties, appending to obj_dict
            for prop in prop_list:
                #First, get the library value of the given property.
                if class_dict.get('configuration') == 0:
                    lib_val = gridlabd.get_value(obj, prop)
                else:
                    config = gridlabd.get_value(obj, 'configuration')
                    lib_val = gridlabd.get_value(config, prop)
                
                non_decimal = re.compile(r'[^\d.]+')
                lib_val = float(non_decimal.sub('',lib_val))
                #Check if the user input a percentage
                thresh = gridlabd.get_global(obj_class + '.' + prop)

                #If so, set the threshold to be a % or a +- range of that property
                if '%' in thresh:
                    thresh = float(thresh.strip('%'))/100  
                    if class_dict.get(prop) == 'rating':
                        obj_dict[prop] = lib_val * thresh
                      
                    elif class_dict.get(prop) == 'deviation':
                        obj_dict[prop + '_max'] = lib_val * (1.0 + thresh)
                        obj_dict[prop + '_min'] = lib_val * (1.0 - thresh)
                                        
                    else:
                        gridlabd.warning('%s, class %s should not have a percentage as a threshold.' % (obj,obj_class))
                
                #If the user input a boolean, set the threshold to the library value
                elif class_dict.get(prop) == 'limit':
                        obj_dict[prop] = lib_val

                #If the user didn't input a % or a boolean, set the threshold to the user input
                else:
                    obj_dict[prop] = thresh
                    
            master_dict[obj] = obj_dict.copy()
            
    gridlabd.warning(str(master_dict))
    recorder = open("results.csv","w")
    recorder.write("time, object, property, value")
        

    return True
      

'''
ON_COMMIT
For each key in master dictionary, get the value for each property and compare it to the threshold.
If threshold is exceeded, record the object, property, and value, and exit.
'''

def on_commit(t):
    '''
    Note: This code is not complete! Needs to be restructured to reflect changes to on_init.
    This script should get current values for each property of interest for each object, and
    compare it to the thresholds created in on_init. 
    
    If threshold is exceeded, record the object, property, and value, and exit.
    
    '''
    
#    for obj in master_dict:
#        obj_dict = master_dict.get(obj)
#        for prop in obj_dict:
#            
#            #Get the current value for the given property
#            prop_check = prop.replace('_min','')
#            prop_check = prop_check.replace('_max','')
#            val = gridlabd.get_value(obj, prop_check)
#
#            #Convert the string to a float
#            non_decimal = re.compile(r'[^\d.]+')
#            val = float(non_decimal.sub('',val))
#            
##            gridlabd.warning(obj)
##            gridlabd.warning(prop_check)
##            gridlabd.warning(str(val))
#            
#
#            if '_min' in prop and val < obj_dict.get(prop):
#                pass
#                    #Record the time, object, property, and value.
#                #TODO: Check the keys in this dictionary - code below is placeholder
##                obj_props = gridlabd.get_object(obj)
##                recorder.write('%s,%s,%s\n' % (obj_props['time'],obj_props['name'],obj_props['property'],obj_props['value']))
#            if '_min' not in prop and val > obj_dict.get(prop):
#                pass
#            
#            
    return True

