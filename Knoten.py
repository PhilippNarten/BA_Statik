#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 12:38:54 2023

@author: philippnarten
"""

class Knoten:
    def __init__(self, id, x, y, fg, canvas_coord, id_show, angle):
        self.id = id
        self.x = x
        self.y = y
        self.fg = [int(x) for x in fg]
        self.canvas_coord = canvas_coord
        self.id_show = id_show
        self.angle = angle
    
    
        
        