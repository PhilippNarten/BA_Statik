#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 19:26:35 2023

@author: philippnarten
"""

import numpy as np
import numpy.matlib


class Timoshenkobalken_reduziert:
    
    def __init__(self, id_show , id, knoten = [], EI = float, EA =float, GA_s = float, element_lasten = []): 
       self.knoten_1 = knoten[0]
       self.knoten_2 = knoten[1]
       self.id = id
       self.x_Ko_anfang = knoten[0].x
       self.x_Ko_ende = knoten[1].x
       self.y_Ko_anfang = knoten[0].y
       self.y_Ko_ende = knoten[1].y
       self.l_x = self.x_Ko_ende - self.x_Ko_anfang
       self.l_y = self.y_Ko_ende - self.y_Ko_anfang
       self.l   = float(np.sqrt(self.l_x**2 + self.l_y**2))
       self.EI = EI
       self.EA = EA
       self.GA_s = GA_s
       self.n = float(element_lasten[1])
       self.q = float(element_lasten[0])
       self.K_el_g = self.Elementsteifigkeitsmatrix()
       self.f_el_g = self.Elementlastvektor()
       self.fg_knoten1 = knoten[0].fg
       self.fg_knoten2 = knoten[1].fg
       self.fg = self.fg_knoten1 + self.fg_knoten2
       self.id_show = id_show
       
       
    def node_transormation(self):
         
        #Winkel in Bogenmaß umwandeln
        b = np.deg2rad(self.knoten_1.angle)
        g = np.deg2rad(self.knoten_2.angle)
        # wi
        #Transformationsmatrix für knoten
        T_node = np.array([[np.cos(b), np.sin(b), 0, 0, 0, 0],
                           [-np.sin(b), np.cos(b), 0, 0, 0, 0],
                           [0, 0, 1, 0, 0, 0,],
                           [0, 0, 0, np.cos(g), np.sin(g), 0],
                           [0, 0, 0, -np.sin(g), np.cos(g), 0],
                           [0, 0, 0, 0, 0, 1]]) 
        return T_node
    
    def Transformationsmatrix(self):
        
        #Für Fallunterscheidung arctan2
        alpha = np.arctan2(self.l_y, self.l_x)
        sin_alpha = np.sin(alpha)
        cos_alpha = np.cos(alpha)
        
        T = np.array([[cos_alpha, sin_alpha, 0, 0, 0, 0],
                     [-sin_alpha, cos_alpha, 0, 0, 0, 0],
                     [0, 0, 1, 0, 0, 0,],
                     [0, 0, 0, cos_alpha, sin_alpha, 0],
                     [0, 0, 0, -sin_alpha, cos_alpha, 0],
                     [0, 0, 0, 0, 0, 1]])
        
        return T
    
    def Elementsteifigkeitsmatrix(self):  
        
        T = self.Transformationsmatrix()
        
        K_el_l = np.array([[self.EA/self.l, 0, 0, -self.EA/self.l, 0, 0],
                           [0, self.GA_s/self.l, -0.5 * self.GA_s, 0, -self.GA_s/self.l, -0.5 * self.GA_s],
                           [0, -0.5 * self.GA_s, 1/4 * self.GA_s * self.l +self.EI/self.l, 0, 0.5 * self.GA_s, 1/4*self.GA_s*self.l - self.EI/self.l],
                           [-self.EA/self.l, 0, 0, self.EA/self.l, 0 , 0],
                           [0, -self.GA_s/self.l, 0.5*self.GA_s, 0, self.GA_s/self.l, 0.5 * self.GA_s],
                           [0, -0.5 * self.GA_s, 1/4*self.GA_s*self.l - self.EI/self.l, 0, 0.5 * self.GA_s, 1/4 * self.GA_s * self.l +self.EI/self.l ]])
        
        K_el_g = np.transpose(T) @ K_el_l @ T
        #Berücksichtigen der Knotenverdrehungen
        T_node = self.node_transormation()
        K_el_g_node = np.transpose(T_node) @ K_el_g @ T_node
        
        return K_el_g_node
    
    def Elementlastvektor(self):
        
        T = self.Transformationsmatrix()
        
        f_el_l = np.array([[0.5 * self.n*self.l],   
                           [ self.q * self.l/2],
                           [0],
                           [0.5 * self.n*self.l],
                           [self.q * self.l/2],
                           [0]])
        
        f_el_g = np.transpose(T) @ f_el_l
        T_node = self.node_transormation()
        f_el_g_node = np.transpose(T_node) @ f_el_g 
        
        return f_el_g_node
    
    #partikuläre Anteile überprüfen
    
    def Biegelinie(self, x, U):
        
        N = np.array([[1- x/self.l],
                      [x/self.l]])
        
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1]
            
        d_el_l = self.Transformationsmatrix() @ d_el_g
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
        
        w_h = N[0] * d_el_l[1] + N[1] * d_el_l[4]
        w_p = 0
        if self.q != 0:
            w_p = (self.q * self.l) / (2 * self.GA_s) * (x- (x**2/self.l)) + (self.q*(self.l**2.0))/(24.0*self.EI) * (x**2.0) * (1.0 - 2.0 *(x/self.l) + (x/self.l)**2.0)
        w = w_p + w_h
        return w
    
    def Moment(self, x, U):
        
        dN = np.array([[-1/self.l],
                      [1/self.l]])
        
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1]
            
        d_el_l = self.Transformationsmatrix() @ d_el_g
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
        
        M_h = self.EI * (dN[0] * d_el_l[2] + dN[1] * d_el_l[5]) #kappa_h * EI
        #partikulärer Anteil, siehe goodnotes datei
        M_p = 0
        if self.q != 0:
            M_p = self.EI * ((- self.q * self.l**2) / (24 * self.EI)) * (2- 12 * x/self.l + 12* (x**2 / self.l**2))
        M = M_h + M_p
        return M
        
    
    def Querkraft(self, x, U):
        
        #in balkenmitte nehmen
        x_h = self.l/2
        
        N = np.array([[1- x_h/self.l],
                      [x_h/self.l]])
        
        dN = np.array([[-1/self.l],
                      [1/self.l]])
        
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1]
            
        d_el_l = self.Transformationsmatrix() @ d_el_g
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
        
        phi_h = N[0] * d_el_l[2] + N[1] * d_el_l[5] 
        
        dw_h = dN[0] * d_el_l[1] + dN[1] * d_el_l[4]
        
        V_h = self.GA_s * (dw_h + phi_h)
        V_p = 0
        if self.q != 0:
            V_p = (self.q * self.l) / (2 * self.GA_s) * (1-2* (x/self.l)) * self.GA_s
        V = V_h + V_p
        return V
        
    def Normalkraft(self, x, U):
        
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1]
        
        d_el_l = self.Transformationsmatrix() @ d_el_g
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
            
            #Nur die für Normalkraft relevanten Formfunktionen
        dN = np.array([[-1.0/self.l],
                       [1.0/self.l]])
            
        N_h = self.EA * (dN[0] * d_el_l[0] + dN[1] * d_el_l[3])
        
        #partikulärer Anteil: 
        N_p = 0
        if self.n != 0: 
            N_p = (- self.n * x + self.n * self.l/2)
        
        N = N_h + N_p
        return N
    
    
    
    def Längsverschiebung(self, x, U):
        
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1]
            
        d_el_l = self.Transformationsmatrix() @ d_el_g
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
        
        N = np.array([[1.0 - x/self.l],
                       [x/self.l]])
        u_h = N[0] * d_el_l[0] + N[1] * d_el_l[3]
        
        #partikuläre Lösung
        u_p = 0
        if self.n != 0: 
            u_p = 1/self.EA * (-self.n * x**2 / 2 + self.n * self.l/2 * x)
        
        u = u_h + u_p
        
        return  u
    
    
    
    
    
    