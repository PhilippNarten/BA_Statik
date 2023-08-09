#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 18:09:00 2023

@author: philippnarten
"""
import numpy as np
import numpy.matlib

class Loesen:
    
    def __init__(self, elemente, fg_randbedingungen, knotenlasten, knotenliste):
        self.elemente = elemente
        self.rb = fg_randbedingungen
        self.knotenlasten = knotenlasten
        self.knotenliste = knotenliste
        
    def Assemblieren_ohneRB(self):
        
        #höchten Freiheitsgrad finden
        n_fg = 0
        for knoten in self.knotenliste[0]:
            for fg in knoten.fg:
                if fg > n_fg:
                    n_fg = fg
        
        
        #Nullmatrix erstellen mit dimension n_fg x n_fg
        K = np.zeros((n_fg, n_fg))
        F = np.matlib.zeros((n_fg,1))
           
         
        for element in self.elemente: 
     
            fg_liste = element.fg  
            K_el = element.K_el_g 
            f_el = element.f_el_g
            
            for i in range(6): #i läuft  die Einträge des fg Vektors ab
                fg_1 = fg_liste[i]-1 #systemfg bekommen und 1 abziehen für die zuordnung
                
                # Lastvektor assemblieren
                F[fg_1, 0] += f_el[i, 0]
                
                for j in range(i,6): #alle weiteren stellen ab der i-ten stelle im fg vektor
                    fg_2 = fg_liste[j]-1 #sys fg der weiteren stelle bekommen und 1 abziehen für zuordnung
                    
                    #die Einträge aus der Elementsteifigkeitsmatrix werden den passenden Systemfreiheitsgraden zugeordnet 
                    K[fg_1, fg_2] += K_el[i,j] #läuft die obere rechte Drieecksmatrix der Elementsteifikgeitsmatrix ab und ordnet der Systemmatrix zu
                    K[fg_2, fg_1] = K[fg_1, fg_2] #spiegeln,da symmetrisch                                                                                  
                
        for knotenlast in self.knotenlasten:
            #falls dem fg eine Last zugeordnet ist wird sie berücksichtigt
            if knotenlast[1] != 0:
                fg = knotenlast[0]
                last = knotenlast[1]
                F[fg-1, 0] += last
                
        return K, F
        
    def Assemblieren_mitRB(self):
        
        K, F = self.Assemblieren_ohneRB()
        
        #geht die alr randbedingungen durch und löscht die zeilen und spalten
        for list in self.rb:
            
            fg = list[0]
            fg_wert = list[1]
            
            #nullzeilen und spalten für den fg = 0
            K[fg-1, :] = fg_wert
            K[:, fg-1] = fg_wert
            K[fg-1, fg-1] = 1 #gleich 1 setzen damit d nicht beliebig groß wird
            
            #zugehöriger EIntrag im Lastvektor auf 0 setzen
            F[fg-1] = 0 
        
        return K, F
    
    def loesen(self):
        
        K, F  = self.Assemblieren_mitRB()
        
        U = np.linalg.solve(K,F)
        
        return U
           
        
    
    
        
    
   
        

