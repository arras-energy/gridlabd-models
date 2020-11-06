#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 09:42:40 2020

@author: saraborchers
"""
import gridlabd
import os

print('running ica_main.py')

# Run glm that modifies the IEEE model
gridlabd.command('../ICA_models/ica_mod.glm')

# Run the IEEE model
# os.chdir("../")
print(os.getcwd())
gridlabd.command("../ieee123/model/ieee123.glm")

print('Ran both glm files')
gridlabd.start("wait")

'''
Question: I shouldn't have to have ica_config.glm in ICA_models
for this to run, right? It should be created by the input file.
But it doesn't run without it... different error when it is 
included. 
'''

# play around with removing os, might be causing error

# os.chdir("../ieee123")
