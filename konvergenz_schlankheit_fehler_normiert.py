#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 30 12:01:39 2023

@author: philippnarten
"""
from Knoten import Knoten
from Timoshenko_red import Timoshenkobalken_reduziert
from Timoshenkobalken import Timoshenkobalken
from Timoshenko_exakt import Timoshenkobalken_exakt
from Bernoulli_Balkenelement import  Balkenelement
from Loesen import Loesen
import numpy as np
import matplotlib.pyplot as plt
import os

#Elementgrößen


EA = 1000
element_lasten = [0, 0]
anfang = [0,0]
#ende = [10,0]
ende = [10, 0]
l=10
h_list = [10,9.5,9,8.5,8,7.5,7,6.5,6,5.5,5,4.5,4,3.5,3, 2.5, 2, 1.5, 1, 0.5]#, 0.1] 
n = 1
fg_randbedingungen = [[1, 0],[2, 0], [3, 0]] #Einspannung
#knotenlasten = [[5, 10]] #F_z 10kn
platzhalter = 0
w_b = []
w_t = []
l_h = []
w_te = []
w_tl = []
w_tl2 = []
#realistische annahmen oder hauptsache zeigen worum es geht?


for h in h_list:
    EI = 30000000* 1*h**3/12 #realistisch E = 30000000, G = 12500000
    GA_s = 12500000*5/6*1*h
    l_h.append(l/h)
    #bernoulli
    knoten = []
    x_steps = np.linspace(0, ende[0], n+1)
    fg = [1,2,3]
    for i, x in enumerate(x_steps):
        if i==0:
            fg = fg
        else:
            fg = [value+3 for value in fg]
        knoten.append(Knoten(1, x, anfang[1], fg, [0,0], 1, 0))
    
    knotenliste = [knoten, 0]
    knotenlasten = [[knoten[-1].fg[-2], 30]]
    b_elemente = []
    t_elemente = []
    tl_elemente = []
    te_elemente = []
    tl2_elemente = []
    
    for i in range(n):
        knoten_el = [knoten[i], knoten[i+1]]
        b_elemente.append(Balkenelement(1, 1, knoten_el,EI, EA, element_lasten))
        t_elemente.append(Timoshenkobalken(platzhalter, platzhalter, knoten_el, EI, EA, GA_s, element_lasten))
        te_elemente.append(Timoshenkobalken_exakt(platzhalter, platzhalter, knoten_el, EI, EA, GA_s, element_lasten))
        tl_elemente.append(Timoshenkobalken_reduziert(platzhalter, platzhalter, knoten_el, EI, EA, GA_s, element_lasten))
        
    #Bernoulli
    System_b = Loesen(b_elemente, fg_randbedingungen, knotenlasten, knotenliste)

    U_b = System_b.loesen()
    w_b.append(U_b[-2,-1]/U_b[-2,-1])
    print(U_b[-2, -1])
    #Timoshenko locking
   
    System_t = Loesen(t_elemente, fg_randbedingungen, knotenlasten, knotenliste)
    U_t = System_t.loesen()
    w_t.append(U_t[-2,-1]/U_b[-2,-1])
    
    #Timoshenko exakt
    
    System_te = Loesen(te_elemente, fg_randbedingungen, knotenlasten, knotenliste)
    U_te = System_te.loesen()
    w_te.append(U_te[-2,-1]/U_b[-2,-1])
    
    #Timoshenko lockingfrei
    System_tl = Loesen(tl_elemente, fg_randbedingungen, knotenlasten, knotenliste)
    U_tl = System_tl.loesen()
    w_tl.append(U_tl[-2,-1]/U_b[-2,-1])
    




x_val = l_h
plt.xlabel(r"$\mathbf{\frac{l}{h}}$")
plt.ylabel(r"$\mathbf{\frac{w}{w_{EB}}}$")
plt.plot(x_val, w_b, color="black", label="Euler-Bernoulli")
plt.plot(x_val, w_t, color="blue", label="Timoshenko locking")
plt.plot(x_val, w_tl, color="orange", label="Timoshenko lockingfrei")
plt.plot(x_val, w_te, color="green", label="Timoshenko exakt")
plt.legend(loc="upper right")
plt.xlim(x_val[0], x_val[-1])
plt.axhline(0, color="black", linewidth=0.5)
plt.subplots_adjust(left=0.145)
plt.xlim(x_val[0], x_val[-1])
plt.show()

    

#plot speichern
datei_name = "timoshenko_kragarm_konvergenz_n1" + ".pdf"
ordner_pfad = os.path.join(os.path.dirname(__file__), "Plots")
datei_pfad = os.path.join(ordner_pfad, datei_name)
plt.savefig(datei_pfad)

    
            
