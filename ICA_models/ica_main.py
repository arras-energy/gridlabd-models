#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 09:42:40 2020

@author: saraborchers
"""
import gridlabd
import os

# Uncomment for IEEE-123 - works!
filepath = "../ieee123"
model = "model/ieee123.glm"

## Uncomment for IEEE-13 - Throws error
# filepath = "../"
# model = "IEEE-13.glm"

## Uncomment for IEEE-4 - Throws error 
# filepath = '../'
# model = 'powerflow_IEEE_4node.glm'

# Run the modification file
print(os.getcwd())
gridlabd.command("../ICA_models/ica_mod.glm")

# Run the IEEE model
os.chdir(filepath)
gridlabd.command(model)
gridlabd.start("wait")
