#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 12:01:39 2023

@author: philippnarten
"""
from Knoten import Knoten
from Timoshenko_red import Timoshenkobalken_reduziert
from Bernoulli_Balkenelement import  Balkenelement
from Loesen import Loesen
import numpy as np
import matplotlib.pyplot as plt
import os

#Elementgrößen
EI = 64000
GA_s = 1666667
EA = 1000
element_lasten = [0, 0]
anfang = [0,0]
ende = [10,0]

#Bernoulli mit einem Element
fg_randbedingungen_b = [[1, 0],[2, 0], [3, 0]] #Einspannung
knotenlasten_b = [[5, 10]] #F_z 10kn
b_knoten = []
b_knoten.append(Knoten(1, anfang[0], anfang[1], [1,2,3], [0,0], 1, 0))
b_knoten.append(Knoten(2, ende[0], ende[1], [4,5,6], [0,0], 1,0 ))

knotenliste_b = [b_knoten, 0]
b_elemente = []
b_elemente.append(Balkenelement(1, 1, b_knoten,EI, EA, element_lasten ))
System = Loesen(b_elemente, fg_randbedingungen_b, knotenlasten_b, knotenliste_b)
U_b = System.loesen()
phi_b = U_b[-1,-1]
w_b = U_b[-2,-1]

#mehrere Elemente erstellen 
n = 100# von 1 bis n Elemente berechnen
start_x = anfang[0]
ende_x = ende[0]
start_y = anfang[1]
ende_y = ende[1]
platzhalter = 0
winkel = 0
U_list = [] #Lösungen 

for i in range(1,n+1):
    sys_knoten = []
    elemente = []
    steps_x = np.linspace(start_x, ende_x , i+1) # x-Werte
    steps_y = np.linspace(start_y, ende_y , i+1) # y-Werte
    
    n_knoten = len(steps_x)
    
    fg_node = [1,2,3]
    n_node = 0
    
    for k in range(n_knoten):

        sys_knoten.append(Knoten(platzhalter, steps_x[k], steps_y[k], fg_node, platzhalter, platzhalter, winkel))
            
        for fg in range(3):
            fg_node[fg] +=3
                
        
            
    for n_element in range(n_knoten-1):
        elemente.append(Timoshenkobalken_reduziert(platzhalter, platzhalter, [sys_knoten[n_element], sys_knoten[n_element+1]], EI, EA, GA_s, element_lasten))
            
      
    fg_randbedingungen = [[1, 0],[2, 0], [3, 0]] #Einspannung
    
    knotenlasten = [[elemente[-1].fg[-2], 10]] # vorletzter FG w mit Knotenlast von 10 belasten
    knotenliste_t = [sys_knoten, platzhalter]
    System = Loesen(elemente, fg_randbedingungen, knotenlasten, knotenliste_t)
    U_list.append(System.loesen())


phi_list = []
w_list = []
x_val = []
for u in U_list:
           
    phi_list.append((u[-1,-1]))
    w_list.append((u[-2,-1]))
    
for i in range(len(U_list)):
    x_val.append(i+1)
    

plt.xlabel("Elementanzahl", weight = "bold")
plt.plot(x_val, phi_list, color="orange", linestyle="dashdot", label="\u03C6 Timoshenko lockingfrei")
plt.plot(x_val, [phi_b]*len(x_val), color="orange", label="\u03C6 Euler-Bernoulli")
plt.plot(x_val, w_list, color="blue", linestyle='dashdot', label="w Timoshenko lockingfrei")
plt.plot(x_val, [w_b]*len(x_val), color="blue", label="w Euler-Bernoulli")
plt.legend(loc="right")
plt.xlim(x_val[0], x_val[-1])
plt.axhline(0, color="black", linewidth=0.5)
plt.yticks([phi_b, w_b, 0]) 
plt.subplots_adjust(left=0.145)
plt.show()

#plot speichern
datei_name = "timoshenko_kragarm_konvergenz" + ".pdf"
ordner_pfad = os.path.join(os.path.dirname(__file__), "Plots")
datei_pfad = os.path.join(ordner_pfad, datei_name)
plt.savefig(datei_pfad)


    
            
