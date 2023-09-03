#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 12:20:08 2023

@author: philippnarten
"""

import numpy as np
import numpy.matlib



class Balkenelement: 
    
    def __init__(self, id_show , id , knoten = [], EI = float, EA =float, element_lasten = []): 
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
                           [0, 12*self.EI/self.l**3, -6*self.EI/self.l**2, 0, -12*self.EI/self.l**3, -6*self.EI/self.l**2],
                           [0, -6*self.EI/self.l**2, 4*self.EI/self.l, 0, 6*self.EI/self.l**2, 2*self.EI/self.l],
                           [-self.EA/self.l, 0, 0, self.EA/self.l, 0, 0],
                           [0, -12*self.EI/self.l**3, 6*self.EI/self.l**2, 0, 12*self.EI/self.l**3, 6*self.EI/self.l**2],
                           [0, -6*self.EI/self.l**2, 2*self.EI/self.l, 0, 6*self.EI/self.l**2, 4*self.EI/self.l]])
            
        
        
        
        K_el_g = np.transpose(T) @ K_el_l @ T #auf globale Koordinaten transformieren
        
        #Berücksichtigen der Knotenverdrehungen
        T_node = self.node_transormation()
        K_el_g_node = np.transpose(T_node) @ K_el_g @ T_node
        
        return K_el_g_node
        
    
    
    def Elementlastvektor(self):
        
        T = self.Transformationsmatrix()
        

        f_el_l = np.array([[0.5 * self.n*self.l],
                           [0.5 * self.q*self.l],
                           [-self.q*self.l**2/12],
                           [0.5 * self.n*self.l],
                           [0.5 * self.q*self.l], 
                           [self.q*self.l**2/12]])
        
        f_el_g = np.transpose(T) @ f_el_l
        
        T_node = self.node_transormation()
        f_el_g_node = np.transpose(T_node) @ f_el_g 
        
        return f_el_g_node
    
    #bei der Rückrechnung wieder die Knoten berücksichtigen    
    def Biegelinie(self, x, U):
        
        N = np.array([[1.0-x/self.l],
                      [1.0 - 3.0*(x/self.l)**2.0 + 2.0 *(x/self.l)**3.0],
                      [-x+2.0*x**2.0/self.l - x**3.0/self.l**2.0],
                      [x/self.l],
                      [3.0*(x/self.l)**2.0 - 2.0 *(x/self.l)**3.0],
                      [x**2.0 /self.l - x**3.0 /(self.l**2.0)]])
                      
   
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1] 
        
        d_el_l = self.Transformationsmatrix() @ d_el_g #auf globale fg 
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
        
        
        
        w_h = 0.0
        for j in [1,2,4,5]:
            w_h += N[j] * d_el_l[j]
            
        w_p = 0.0
        
        if self.q != 0 :
            w_p += (self.q*(self.l**2.0))/(24.0*self.EI) * (x**2.0) * (1.0 - 2.0 *(x/self.l) + (x/self.l)**2.0)
            
        w = w_h + w_p
        
        return w
        
    def Moment(self, x, U):
        
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1] 
        
        d_el_l = self.Transformationsmatrix() @ d_el_g
        
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
            
        ddN = np.array([[0],
                        [-6/self.l**2+12*x/self.l**3],
                        [4/self.l-6*x/self.l**2],
                        [0],
                        [6/self.l**2-12*x/self.l**3],
                        [2/self.l - 6*x/self.l**2]])
        
        M_h = 0.0
        for j in [1,2,4,5]:
            M_h += - self.EI *(ddN[j] * d_el_l[j])
        
        M_p = 0.0
        if self.q != 0:
            
            M_p +=  -self.EI*self.q*self.l**2/(24*self.EI)*(2 -12*x/self.l+12*(x**2/self.l**2))
        
        M = M_h + M_p
        
        return M
    
    def Querkraft(self, x, U):
        
        d_el_g = np.matlib.zeros((6,1))
        
        for i in range(6):
            fg = self.fg[i]
            d_el_g[i,0] = U[fg-1] 
        
        d_el_l = self.Transformationsmatrix() @ d_el_g
        
        #auf Knotenausrichtung
        d_el_l = self.node_transormation() @d_el_l
        
        dddN = np.array([[0],
                         [12/(self.l**3)],
                         [-6/self.l**2],
                         [0],
                         [-12/self.l**3],
                         [-6/self.l**2]])
        
        V_h = 0.0
        for j in [1,2,4,5]:
            V_h += -self.EI * (dddN[j] * d_el_l[j])
        
        V_p = 0.0
        if self.q != 0:
            V_p += -self.EI*self.q*self.l**2/(24*self.EI)* 12/self.l**2 * (2*x-self.l)
            
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
        
            
        
        
            
            
        
         
          
        
        
            
            
            
            
        
        
            
        
        
  
        
        
        
        
        
        
        
        
        
        

