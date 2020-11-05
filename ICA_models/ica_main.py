#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 09:42:40 2020

@author: saraborchers
"""
import gridlabd
import os
os.chdir("../ieee123")
# gridlabd.command("input_config.csv")
# gridlabd.command("ica_mod.glm")
gridlabd.command("../ieee123/ica_ieee123.glm")
gridlabd.start("wait")