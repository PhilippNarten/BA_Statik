#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  1 12:04:47 2023

@author: philippnarten
"""

def get_fg(fg = []):
     fg_el = fg
     for j in range(3): 
         fg_el.append(fg_el[-1]+1)
    
     fg_el[0:3] = []
    
     return fg_el
            
    