#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  8 18:46:44 2023

@author: philippnarten
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import os
from Knoten import Knoten
from Bernoulli_Balkenelement import Balkenelement
from Loesen import Loesen
from Timoshenkobalken import Timoshenkobalken
from Timoshenko_red import Timoshenkobalken_reduziert
from Timoshenko_ans_dsg import Timoshenkobalken_ans_dsg
from Timoshenko_exakt import Timoshenkobalken_exakt

class MainWindow(tk.Tk):
    
    def __init__(self):
        
        super().__init__()
        self.title("GUI")
        self.resizable(False, False)
        
        #erstes Frame
        self.frame1 = tk.Frame(self, padx = 20, pady= 20, borderwidth=2)
        self.frame1.grid(row= 0, column=0, sticky = "nsew")

        self.canvas = tk.Canvas(self.frame1, width= 650, height= 650, bg="white")
        self.canvas.grid(row=0, column=0,columnspan= 4, sticky = "nsew", )
        self.draw_grid()
        
        self.erstellen_label = ttk.Label(self.frame1, text="System:")
        self.erstellen_label.grid(row =1, column = 0, pady=10, sticky = "w")
        self.erstellen_label.configure(font=("Arial", 16,"bold"))
        
        self.draw_button = ttk.Button(self.frame1, text="Zeichnen", command= self.acitvate_drawing)    
        self.calc_button = ttk.Button(self.frame1, text="Berechnen", command= self.berechnen)
            
        self.draw_button.grid(row=2, column=1, sticky="w")
        self.calc_button.grid(row=2, column=2, sticky = "w")
        
        # Label zur Anzeige der Mausposition
        self.pos_label = ttk.Label(self.frame1, text="Mausposition: (0, 0)")
        self.pos_label.grid(row=2, column=0, sticky = "w")
        self.pos_label.configure(font=("Arial",14, ""))
        self.canvas.bind('<Motion>', self.update_mouse_position)
        
        self.delete_button = ttk.Button(self.frame1, text ="löschen", command=self.delete)
        self.delete_button.grid(row=2, column= 3, sticky="w")
        
        self.erstellen_label = ttk.Label(self.frame1, text="Plotten:")
        self.erstellen_label.grid(row =3, column = 0, pady=10, sticky= "w")
        self.erstellen_label.configure(font=("Arial", 16,"bold"))
        
        self.moment_button = ttk.Button(self.frame1, text="Moment", command=self.Moment)
        self.moment_button.grid(row=4, column=1, sticky="w")
        self.querkraft_button = ttk.Button(self.frame1, text="Querkraft", command=self.Querkraft)
        self.querkraft_button.grid(row=4, column=2, sticky="w")
        self.normalkraft_button = ttk.Button(self.frame1, text="Normalkraft", command=self.Normalkraft)
        self.normalkraft_button.grid(row=4, column=3, sticky="w")
        
        self.verformtesSystem_button = ttk.Button(self.frame1, text="Systemverformung", command=self.Gesamtverformung)
        self.verformtesSystem_button.grid(row=4, column=0, sticky="w")
        
        self.combobox_theorie = ttk.Combobox(self.frame1)
        self.combobox_theorie["width"] = 21
        self.combobox_theorie.grid(row=1, column=1, sticky="w", columnspan=2)
        self.combobox_theorie.insert(0,"Theorie wählen")
        self.combobox_theorie["values"]=["Bernoulli", "Timoshenko mit Locking", "Timoshenko reduzierte Integration", "Timoshenko ANS/DSG", "Timoshenko exakt"]
        self.combobox_theorie.configure(state="readonly")
        
        self.load_sys = ttk.Button(self.frame1, text ="load json", command=self.load_system)
        self.load_sys.grid(row=1, column= 2, columnspan = 2) 
        self.save_sys = ttk.Button(self.frame1, text ="save json", command=self.save_system_json)
        self.save_sys.grid(row=1, column= 3, sticky="e")#, columnspan = 2)
        
        #SGR,
        self.info_frame = tk.Frame(self, padx=20, pady=20, borderwidth=2)#, relief="groove")
        self.info_frame.grid(row=0, column=1,sticky="nsew")
        self.fig = plt.Figure(figsize=(4, 4), dpi=150)
        self.plot_frame = tk.Frame(self.info_frame)
        self.plot_frame.grid(row= 0, column = 0, columnspan= 3)
        
        self.canvas_info = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_info.draw()
        self.canvas_info.get_tk_widget().pack()
        self.toolbar = NavigationToolbar2Tk(self.canvas_info, self.plot_frame)
        self.toolbar.update()
        self.toolbar._buttons['Save'].pack_forget()
        self.toolbar.pack(side= tk.LEFT)
        
        self.save_figure_button = ttk.Button(self.plot_frame, text="save plot", command=self.save_figure_name)
        self.save_figure_button.pack(side=tk.RIGHT)
        
        self.element_result = ttk.Label(self.info_frame, text = "Elemente:")
        self.element_result.grid(row =2, column = 0, sticky = "w")
        self.element_result.configure(font=("Arial", 16,"bold"))
        
        self.combobox0 = ttk.Combobox(self.info_frame)
        self.combobox0.grid(row=3, column=0, sticky="w")
        self.combobox0.insert(0,"Element wählen")
        self.combobox0.configure(state="readonly")
        
        self.combobox1 = ttk.Combobox(self.info_frame)
        self.combobox1.grid(row=3, column=1, sticky="w")
        self.combobox1.insert(0,"Elementgröße wählen")
        self.combobox1.configure(state="readonly")
        
        self.button_anzeigen = ttk.Button(self.info_frame, text= "Ergebnisse anzeigen", command=self.create_element_table)
        self.button_anzeigen.grid(row = 3, column=2, sticky="w")
        
        self.node_result = ttk.Label(self.info_frame, text = "Knoten:")
        self.node_result.grid(row =4, column = 0, sticky = "w")
        self.node_result.configure(font=("Arial", 16,"bold"))
        
        self.combobox2 = ttk.Combobox(self.info_frame)
        self.combobox2.grid(row=5, column=0, sticky="w")
        self.combobox2.insert(0,"Knoten wählen")
        self.combobox2.configure(state="readonly")
        
        
        self.button_anzeigen1 = ttk.Button(self.info_frame, text= "Ergebnisse anzeigen", command=self.create_node_table)
        self.button_anzeigen1.grid(row = 5, column=2, sticky="w")
        
        #Skalierung der Verschiebungsfigur
        self.label_scale = ttk.Label(self.info_frame, text= "Skalieren:")
        self.label_scale.grid(row=6, column= 0, sticky = "w")
        self.label_sys = ttk.Label(self.info_frame, text= "Systemverformung:")
        self.label_sys.grid(row=7, column= 0, sticky = "w")
        self.label_sys.configure(font=("Arial",14,""))
        self.label_scale.configure(font=("Arial", 16,"bold"))
        self.scale_var_sys = tk.DoubleVar()
        self.scale_sys = ttk.Scale(self.info_frame, from_=1.0, to=400.0, variable=self.scale_var_sys, command= self.scale_changed)
        self.scale_sys.grid(row = 7, column = 2)
        self.scale_value =ttk.Label(self.info_frame, text= "Faktor 100")
        self.scale_value.configure(font=("Arial",14,""))
        self.scale_value.grid(row = 7, column = 1)
        self.scale_sys.set(100)
        
        #Skalierung der SGR
        self.label_sgr = ttk.Label(self.info_frame, text= "Schnittgrößen:")
        self.label_sgr.grid(row=8, column= 0, sticky = "w")
        self.label_sgr.configure(font=("Arial",14,""))
        self.scale_var_sgr = tk.DoubleVar()
        self.scale_sgr = ttk.Scale(self.info_frame, from_=1.0, to=50, variable=self.scale_var_sgr, command= self.scale_changed_sgr)
        self.scale_sgr.grid(row = 8, column = 2)
        self.scale_value_sgr =ttk.Label(self.info_frame, text= "Faktor 1/20")
        self.scale_value_sgr.configure(font=("Arial",14,""))
        self.scale_value_sgr.grid(row = 8, column = 1)
        self.scale_sgr.set(10)
        
        #Knoten speichern 
        self.n_node = 0
        self.knoten_liste=[ [], [] ] #für Knoten und Canvas Koordinaten
        self.create_element_knoten = [ [], [] ]
        self.node_id_show=0
        
        self.n_el = 0 #Anzahl Elemente
        self.System = []
        self.el_id_show = 0
        self.doppelter_knoten_id = 0
        
        self.doppelter_knoten_id_show =100 #doppelter Knoten hat id 100,101,102...
        
        #Randbedingungen für Loesen
        self.alr_rb = []
        self.knotenlasten = []
        
        
        self.u_sys = None
        self.Ergebnisse = None
        self.node_results = None
        self.plot = None
        self.theorie = None
        self.allow_draw = True
        
    def save_figure_name(self):
        
        self.figure_tl = tk.Toplevel()
        self.figure_tl.geometry("200x100")
        self.figure_tl.title("Plot speichern")
        self.figure_tl_label = ttk.Label(self.figure_tl, text="Name der Datei:")
        self.figure_tl_label.pack()
        self.figure_tl_entry = ttk.Entry(self.figure_tl)
        self.figure_tl_entry.pack()
        self.figure_tl_button = ttk.Button(self.figure_tl, text="Save", command=self.save_figure)
        self.figure_tl_button.pack()
        self.figure_tl.grab_set()

    def save_figure(self):
        datei_name = self.figure_tl_entry.get() + ".pdf"
        ordner_pfad = os.path.join(os.path.dirname(__file__), "Plots")
        datei_pfad = os.path.join(ordner_pfad, datei_name)
        self.fig.savefig(datei_pfad)
        self.figure_tl.destroy()
     
        
    def save_system_json(self):
        system = {} 
        
        elemente_list = []
        #jedes Element ablaufen
        for element in self.System:
            
            element_vars = vars(element).copy() #copy stellt sicher, dass das ursprüngliche element nicht verändert wird
            node_1 = element_vars["knoten_1"]
            node_2 = element_vars["knoten_2"]
            node_1_vars = vars(node_1)
            node_2_vars = vars(node_2)
            element_vars["knoten_1"] = node_1_vars
            element_vars["knoten_2"] = node_2_vars
            elemente_list.append(element_vars)
            
        alr_rb = self.alr_rb
        knotenlasten = self.knotenlasten
        knotenliste = {"knoten": [], "canvas_kor": []}
        for i in range(len(self.knoten_liste[0])):
            knotenliste["knoten"].append(vars(self.knoten_liste[0][i]))
            knotenliste["canvas_kor"].append(self.knoten_liste[1][i])
        
        system["elemente"] = elemente_list
        system["alr_rb"] = alr_rb
        system["knotenlasten"] = knotenlasten
        system["knotenliste"] = knotenliste
        system["theorie"] = self.theorie
        
        #Fenster was Name abfragt
        self.system_json = json.dumps(system, default=self.array_to_list)
        self.datei = tk.Toplevel()
        self.datei.geometry("200x100")
        self.datei.title("System speichern")
        self.datei_label = ttk.Label(self.datei, text="Name der Datei:")
        self.datei_label.pack()
        self.datei_entry = ttk.Entry(self.datei)
        self.datei_entry.pack()
        self.datei_button = ttk.Button(self.datei, text = "save", command=self.save_system)
        self.datei_button.pack()
        self.datei.grab_set()
       
        
    def save_system(self):
        datei_name = self.datei_entry.get() + ".json"
        ordner_pfad = os.path.join(os.path.dirname(__file__), "Systeme_json")
        datei_pfad = os.path.join(ordner_pfad, datei_name)
        
        with open(datei_pfad, "w") as file:
            file.write(self.system_json)
        
        self.datei.destroy()
        
    def load_system(self):
        self.delete()
        self.ordner_pfad = os.path.join(os.path.dirname(__file__), "Systeme_json")
        dateien = os.listdir(self.ordner_pfad)
        
        self.datei_load = tk.Toplevel()
        self.datei_load.title("Dateien")
        self.combobox_dateien = ttk.Combobox(self.datei_load)
        self.combobox_dateien["values"] = [datei for datei in dateien if datei.endswith(".json")]
        self.combobox_dateien.pack()
        self.combobox_dateien.configure(state= "readonly")
        self.datei_load_button = ttk.Button(self.datei_load, text = "load", command=self.json_to_obj)
        self.datei_load.grab_set()
        self.datei_load_button.pack()
        
    def json_to_obj(self):
        self.allow_draw = False
        #json in dict
        load_json = self.combobox_dateien.get()
        datei_pfad = os.path.join(self.ordner_pfad, load_json)
        
        with open(datei_pfad, "r") as file:
            sys_dict = json.load(file)
            
        self.datei_load.destroy()
        
        self.alr_rb = sys_dict["alr_rb"]
        self.knotenlasten = sys_dict["knotenlasten"]
        self.theorie = sys_dict["theorie"]
        
        if self.theorie == "Bernoulli":
            self.combobox_theorie.current(0)
        
        elif self.theorie == "Timoshenko mit Locking":
            self.combobox_theorie.current(1)
            
        elif self.theorie == "Timoshenko reduzierte Integration":
            self.combobox_theorie.current(2)
        
        elif self.theorie == "Timoshenko ANS/DSG":
            self.combobox_theorie.current(3)
            
        elif self.theorie == "Timoshenko exakt":
            self.combobox_theorie.current(4)
        
        
        #knotenliste erstellen: 
        knotenliste = sys_dict["knotenliste"]["knoten"]
        
        for node in knotenliste:
            self.knoten_liste[0].append(Knoten(node["id"], node["x"], node["y"], node["fg"], node["canvas_coord"], node["id_show"], node["angle"]))
        self.knoten_liste[1] = sys_dict["knotenliste"]["canvas_kor"]
       
        for element in sys_dict["elemente"]:
            
            node_list_dict = [element["knoten_1"], element["knoten_2"]]
            node_list_obj = []
            
            for node in node_list_dict:
                knoten = Knoten(node["id"], node["x"], node["y"], node["fg"], node["canvas_coord"], node["id_show"], node["angle"])
                node_list_obj.append(knoten)
                x = knoten.canvas_coord[0]
                y = knoten.canvas_coord[1]
                node_angle = math.radians(knoten.angle)
                
                #Knoten zeichnen, für doppelten Knoten id merken
                #die id die beim erstellen der knoten gespeichert wird ist nicht die mit denen die knoten im canvas erstellt werden
                id = self.canvas.create_oval(x-2, y-2, x+2,y+2, fill= "blue")
                
                #überprüfen ob doppelter Knoten
                knoten_kor = [knoten.x, knoten.y]
                j=0
                for dnode in self.knoten_liste[0]:
                    dnode_kor = [dnode.x, dnode.y]
                    if dnode_kor == knoten_kor:
                        j +=1
                    
                if j>=2: 
                    #gibt doppelten Knoten, id auf canvas id ändern und grün machen
                    knoten.id = id
                    self.canvas.itemconfig(knoten.id, outline= "green", width=2)
                    
                fg_node = knoten.fg 
                i = -1
                for fg in fg_node:
                    i +=1
                    
                    #ALR zeichnen
                    for rb in self.alr_rb:
                        if fg in rb: 
                            #gibt ein ALR
                            if i ==0:
                                x1, y1 = self.node_transformation(x, y, x, y, node_angle)
                                x2, y2 = self.node_transformation(x, y, x-6, y+6, node_angle)
                                x3, y3 = self.node_transformation(x, y, x-6, y-6, node_angle)
                                self.canvas.create_polygon(x1,y1,x2,y2, x3, y3, outline = "blue", fill = "")
                            
                            if i == 1:
                                x1, y1 = self.node_transformation(x, y, x, y, node_angle)
                                x2, y2 = self.node_transformation(x, y, x+6, y+6, node_angle)
                                x3, y3 = self.node_transformation(x, y, x-6, y+6, node_angle)
                                self.canvas.create_polygon(x1,y1,x2,y2, x3, y3, outline = "blue", fill = "")
                                
                            if i==2:
                                self.canvas.create_polygon(x+3,y-3, x+3, y+3,x-3, y+3,x-3, y-3, outline = "blue", fill = "")
                    
                    #Knotenlasten zeichnen
                    for knoten_last in self.knotenlasten:
                        
                        if knoten_last[0] == fg:
                            last = knoten_last[1]
                            
                            if last != 0:
                                
                                if i == 0:
                                    
                                    if last < 0:
                                        arrow_position = tk.LAST
                                    else:
                                        arrow_position = tk.FIRST
                                    
                                    x1, y1 = self.node_transformation(x, y, x-5, y, node_angle)
                                    x2, y2 = self.node_transformation(x, y, x-30, y, node_angle)
                                    self.canvas.create_line(x1, y1, x2, y2, arrow = arrow_position, fill= "red" )
                                    
                                if i==1:
                                    
                                    if last < 0:
                                        arrow_position = tk.LAST
                                    else:
                                        arrow_position = tk.FIRST
                                    #Last zeichnen
                                    x1, y1 = self.node_transformation(x, y, x, y-5, node_angle)
                                    x2, y2 = self.node_transformation(x, y,x, y-30, node_angle)
                                    self.canvas.create_line(x1, y1, x2, y2, arrow = arrow_position, fill= "red" )
                                    
                                if i ==2 :
                                    if last< 0:
                                        self.canvas.create_arc(x-25, y-25,x+25, y+25, outline= "red", fill="", style= tk.ARC)
                                        self.canvas.create_line(x+25, y, x+29, y-6, fill="red")
                                        self.canvas.create_line(x+25, y, x+21, y-6, fill="red")
                                        
                                    else:
                                        self.canvas.create_arc(x-25, y-25, x+25, y+25, outline= "red", fill="", style= tk.ARC)
                                        self.canvas.create_line(x, y-25, x+7, y-28, fill="red")
                                        self.canvas.create_line(x, y-25, x+7, y-20, fill="red")
                                        
            
            if self.theorie == "Timoshenko mit Locking":
                
                self.System.append(Timoshenkobalken(element["id_show"], element["id"], node_list_obj, element["EI"], element["EA"], element["GA_s"],[element["q"], element["n"]]))
                #Element zeichnen
                x1, y1 = node_list_obj[0].canvas_coord[0], node_list_obj[0].canvas_coord[1]
                x2, y2 = node_list_obj[1].canvas_coord[0], node_list_obj[1].canvas_coord[1]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
                
                #Last zeichnen
                if element["q"] != 0:
                    qz = element["q"]
                    
                    if qz < 0:
                        arrow_position = tk.LAST
                    else:
                        arrow_position = tk.FIRST
                    #Linienlast zeichnen, eventuell mit gestrichelter Faser übeprüfen
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    
                    #in Bogenmaß
                    angle = math.atan2(y2-y1, x2-x1)
                    arrow_angle = angle + math.pi / 2
                    arrow_length = 20  # Länge der Pfeile
                    arrow_dx = arrow_length * math.cos(arrow_angle)
                    arrow_dy = arrow_length * math.sin(arrow_angle)
                    self.canvas.create_line(x1, y1, x1 - arrow_dx, y1 - arrow_dy, arrow= arrow_position, fil="red")
                    self.canvas.create_line(x2, y2, x2 - arrow_dx, y2 - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x_center, y_center, x_center - arrow_dx, y_center - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x1 - arrow_dx, y1 - arrow_dy, x2 - arrow_dx, y2 - arrow_dy, fill="red")
                
            
            elif self.theorie == "Bernoulli":
                self.System.append(Balkenelement(element["id_show"], element["id"], node_list_obj, element["EI"], element["EA"], [element["q"], element["n"]]))
                #Element zeichnen
                x1, y1 = node_list_obj[0].canvas_coord[0], node_list_obj[0].canvas_coord[1]
                x2, y2 = node_list_obj[1].canvas_coord[0], node_list_obj[1].canvas_coord[1]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
                
                #Last zeichnen
                if element["q"] != 0:
                    qz = element["q"]
                    
                    if qz < 0:
                        arrow_position = tk.LAST
                    else:
                        arrow_position = tk.FIRST
                    #Linienlast zeichnen, eventuell mit gestrichelter Faser übeprüfen
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    
                    angle = math.atan2(y2-y1, x2-x1)
                    arrow_angle = angle + math.pi / 2
                    arrow_length = 20  # Länge der Pfeile
                    arrow_dx = arrow_length * math.cos(arrow_angle)
                    arrow_dy = arrow_length * math.sin(arrow_angle)
                    self.canvas.create_line(x1, y1, x1 - arrow_dx, y1 - arrow_dy, arrow= arrow_position, fil="red")
                    self.canvas.create_line(x2, y2, x2 - arrow_dx, y2 - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x_center, y_center, x_center - arrow_dx, y_center - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x1 - arrow_dx, y1 - arrow_dy, x2 - arrow_dx, y2 - arrow_dy, fill="red")
                    
            elif self.theorie == "Timoshenko reduzierte Integration":
                
                self.System.append(Timoshenkobalken_reduziert(element["id_show"], element["id"], node_list_obj, element["EI"], element["EA"], element["GA_s"],[element["q"], element["n"]]))
                #Element zeichnen
                x1, y1 = node_list_obj[0].canvas_coord[0], node_list_obj[0].canvas_coord[1]
                x2, y2 = node_list_obj[1].canvas_coord[0], node_list_obj[1].canvas_coord[1]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
                
                #Last zeichnen
                if element["q"] != 0:
                    qz = element["q"]
                    
                    if qz < 0:
                        arrow_position = tk.LAST
                    else:
                        arrow_position = tk.FIRST
                    #Linienlast zeichnen, eventuell mit gestrichelter Faser übeprüfen
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    
                    #in Bogenmaß
                    angle = math.atan2(y2-y1, x2-x1)
                    arrow_angle = angle + math.pi / 2
                    arrow_length = 20  # Länge der Pfeile
                    arrow_dx = arrow_length * math.cos(arrow_angle)
                    arrow_dy = arrow_length * math.sin(arrow_angle)
                    self.canvas.create_line(x1, y1, x1 - arrow_dx, y1 - arrow_dy, arrow= arrow_position, fil="red")
                    self.canvas.create_line(x2, y2, x2 - arrow_dx, y2 - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x_center, y_center, x_center - arrow_dx, y_center - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x1 - arrow_dx, y1 - arrow_dy, x2 - arrow_dx, y2 - arrow_dy, fill="red")
            
            elif self.theorie == "Timoshenko ANS/DSG":
                self.System.append(Timoshenkobalken_ans_dsg(element["id_show"], element["id"], node_list_obj, element["EI"], element["EA"], element["GA_s"],[element["q"], element["n"]]))
                #Element zeichnen
                x1, y1 = node_list_obj[0].canvas_coord[0], node_list_obj[0].canvas_coord[1]
                x2, y2 = node_list_obj[1].canvas_coord[0], node_list_obj[1].canvas_coord[1]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
                
                #Last zeichnen
                if element["q"] != 0:
                    qz = element["q"]
                    
                    if qz < 0:
                        arrow_position = tk.LAST
                    else:
                        arrow_position = tk.FIRST
                    #Linienlast zeichnen, eventuell mit gestrichelter Faser übeprüfen
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    
                    #in Bogenmaß
                    angle = math.atan2(y2-y1, x2-x1)
                    arrow_angle = angle + math.pi / 2
                    arrow_length = 20  # Länge der Pfeile
                    arrow_dx = arrow_length * math.cos(arrow_angle)
                    arrow_dy = arrow_length * math.sin(arrow_angle)
                    self.canvas.create_line(x1, y1, x1 - arrow_dx, y1 - arrow_dy, arrow= arrow_position, fil="red")
                    self.canvas.create_line(x2, y2, x2 - arrow_dx, y2 - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x_center, y_center, x_center - arrow_dx, y_center - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x1 - arrow_dx, y1 - arrow_dy, x2 - arrow_dx, y2 - arrow_dy, fill="red")
            
            elif self.theorie == "Timoshenko exakt":
                self.System.append(Timoshenkobalken_exakt(element["id_show"], element["id"], node_list_obj, element["EI"], element["EA"], element["GA_s"],[element["q"], element["n"]]))
                #Element zeichnen
                x1, y1 = node_list_obj[0].canvas_coord[0], node_list_obj[0].canvas_coord[1]
                x2, y2 = node_list_obj[1].canvas_coord[0], node_list_obj[1].canvas_coord[1]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
                
                #Last zeichnen
                if element["q"] != 0:
                    qz = element["q"]
                    
                    if qz < 0:
                        arrow_position = tk.LAST
                    else:
                        arrow_position = tk.FIRST
                    #Linienlast zeichnen, eventuell mit gestrichelter Faser übeprüfen
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    
                    #in Bogenmaß
                    angle = math.atan2(y2-y1, x2-x1)
                    arrow_angle = angle + math.pi / 2
                    arrow_length = 20  # Länge der Pfeile
                    arrow_dx = arrow_length * math.cos(arrow_angle)
                    arrow_dy = arrow_length * math.sin(arrow_angle)
                    self.canvas.create_line(x1, y1, x1 - arrow_dx, y1 - arrow_dy, arrow= arrow_position, fil="red")
                    self.canvas.create_line(x2, y2, x2 - arrow_dx, y2 - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x_center, y_center, x_center - arrow_dx, y_center - arrow_dy, arrow=arrow_position, fill= "red")
                    self.canvas.create_line(x1 - arrow_dx, y1 - arrow_dy, x2 - arrow_dx, y2 - arrow_dy, fill="red")
            
    
    def node_transformation(self, xx, yy, x, y, angle):
        
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        #translation zum koordinatenursprung (x-self.x, y-self.y)
        #rotation mit cos sin, rücktransformation indem self.x,y aufaddiert wird
        x_neu = xx + (x - xx) * cos_angle + (y - yy) * sin_angle
        y_neu = yy - (x - xx) * sin_angle + (y - yy) * cos_angle
        
        return x_neu, y_neu
                
        
    def array_to_list(self, arr):
        
        if isinstance(arr, np.ndarray):
            
            return arr.tolist()  # In eine Python-Liste umwandeln
        
        return arr
        
    def scale_changed(self, event): #habe es von 20 auf 10 geändert. falls fehler
        self.scale_factor_sys = round(self.scale_var_sys.get() / 10) * 10 #auf 10 runden
        if self.scale_factor_sys < 10.0:
            self.scale_factor_sys = 1
        self.scale_value.configure(text=f"Faktor {self.scale_factor_sys}")
        
    def scale_changed_sgr(self, event):
        self.scale_factor_sgr =  round(self.scale_var_sgr.get() / 5) * 5 #auf 5er runden
        if self.scale_factor_sgr < 5.0:
            self.scale_factor_sgr = 1
        self.scale_value_sgr.configure(text=f"Faktor 1/{self.scale_factor_sgr}")
        
        
    def berechnen(self):
        self.fig.clear()
        self.canvas_info.draw()
        self.theorie_calc = self.combobox_theorie.get()
        #falls die Theorie gewechselt wurde
        if self.theorie_calc != self.theorie:
            #Elemente neu erzeugen
            self.change_theory()
            
        system = Loesen(self.System, self.alr_rb, self.knotenlasten, self.knoten_liste) 
        #gibt u aus
        self.u_sys = system.loesen()
        
        #Werte für Tabelle 
        self.Ergebnisse = {}
        elemente = []
        for element in self.System:
            key = str(element.id_show)
            elemente.append(key)
            element_dict = {}
            for  x in [0.0, 0.25, 0.5, 0.75, 1.0]:
                x_el = x * element.l
                moment = round(element.Moment(x_el, self.u_sys)[0,0],2)
                querkraft = round(element.Querkraft(x_el, self.u_sys)[0,0],2)
                normalkraft = round(element.Normalkraft(x_el, self.u_sys)[0,0],2)
                biegelinie = round(element.Biegelinie(x_el, self.u_sys)[0,0], 6)
                laengsverschiebung = round(element.Längsverschiebung(x_el, self.u_sys)[0,0], 6)
                
                if "Moment" in element_dict: 
                    element_dict["Moment"].append(moment)
                else:
                    element_dict["Moment"] = [moment]
                
                if "Querkraft" in element_dict:
                    element_dict["Querkraft"].append(querkraft)
                else:
                    element_dict["Querkraft"] = [querkraft]
                    
                if "Normalkraft" in element_dict:
                    element_dict["Normalkraft"].append(normalkraft)
                else:
                    element_dict["Normalkraft"] = [normalkraft]
                
                if "Querverschiebung" in element_dict:
                    element_dict["Querverschiebung"].append(biegelinie)
                else:
                    element_dict["Querverschiebung"] = [biegelinie]
                
                if "Längsverschiebung" in element_dict:
                    element_dict["Längsverschiebung"].append(laengsverschiebung)
                else:
                    element_dict["Längsverschiebung"] = [laengsverschiebung]
            
            self.Ergebnisse[key] = element_dict
          
        self.combobox0["values"] = elemente
        self.combobox1["values"] = ["Moment", "Querkraft", "Normalkraft", "Querverschiebung", "Längsverschiebung"]
        
        self.node_results={}
        for node in self.knoten_liste[0]:
            node_id=str(node.id_show)
            knoten_results = []
            
            for fg in node.fg:
                result = round(self.u_sys[fg-1][0,0], 6)
                knoten_results.append(result)
                
            knoten_results.append(node.angle)#winkel
            
            self.node_results[node_id] = knoten_results
        
        self.combobox2["values"] = list(self.node_results.keys())
        
    def change_theory(self):

        #falls von bernoulli auf theorie mit schub gewechselt wird
        if self.theorie == "Bernoulli":
            #GAs fragen
            self.ask_GAs = tk.Toplevel()
            self.ask_GAs.title("GAs")
            self.ask_GAs_label = ttk.Label(self.ask_GAs, text="GA_s")
            self.ask_GAs_label.pack()
            self.ask_GAs_entry = ttk.Entry(self.ask_GAs)
            self.ask_GAs_entry.pack()
            self.ask_GAs_button = ttk.Button(self.ask_GAs, text = "save", command=self.get_GAs)
            self.ask_GAs_button.pack()
            self.ask_GAs.grab_set()
            self.ask_GAs.wait_window(self.ask_GAs)
            
            
        #neue Elemente erstellen
        new_system = []
        for element in self.System:
            id_show = element.id_show
            id = element.id
            knoten = [element.knoten_1, element.knoten_2]
            EI = element.EI
            EA = element.EA
            lasten = [element.q, element.n]
            
            if self.theorie_calc =="Timoshenko mit Locking":  
                
                if hasattr(element, "GA_s"):
                    GA_s = element.GA_s
                else:
                    GA_s = self.GA_s
                new_element = Timoshenkobalken(id_show, id, knoten, EI, EA, GA_s, lasten)
                new_system.append(new_element)
                    
            
            elif self.theorie_calc =="Bernoulli":
                new_element = Balkenelement(id_show, id, knoten, EI, EA, lasten)
                new_system.append(new_element)
            
            elif self.theorie_calc =="Timoshenko reduzierte Integration":  
                
                if hasattr(element, "GA_s"):
                    GA_s = element.GA_s
                else:
                    GA_s = self.GA_s
        
                new_element = Timoshenkobalken_reduziert(id_show, id, knoten, EI, EA, GA_s, lasten)
                new_system.append(new_element)
            
            elif self.theorie_calc =="Timoshenko ANS/DSG":  
                
                if hasattr(element, "GA_s"):
                    GA_s = element.GA_s
                else:
                    GA_s = self.GA_s
        
                new_element = Timoshenkobalken_ans_dsg(id_show, id, knoten, EI, EA, GA_s, lasten)
                new_system.append(new_element)
            
            elif self.theorie_calc =="Timoshenko exakt":  
                
                if hasattr(element, "GA_s"):
                    GA_s = element.GA_s
                else:
                    GA_s = self.GA_s
        
                new_element = Timoshenkobalken_exakt(id_show, id, knoten, EI, EA, GA_s, lasten)
                new_system.append(new_element)
                
            
            
            
        self.System = new_system
        self.theorie = self.theorie_calc
                
        
    def get_GAs(self):
        self.GA_s = float(self.ask_GAs_entry.get())
        self.ask_GAs.destroy()
    
    def create_element_table(self):
        
        new_window = tk.Toplevel(self.info_frame)
        new_window.title("Element")
        
        treeview = ttk.Treeview(new_window, columns=tuple(range(7)), show="headings", height=1)
        treeview.heading(0, text="Element")
        treeview.heading(1, text="Elementgröße")
        treeview.heading(2, text="0")
        treeview.heading(3, text="0.25 l")
        treeview.heading(4, text="0.5 l")
        treeview.heading(5, text="0.75 l")
        treeview.heading(6, text="l")
        
        for i in range(7):
            treeview.column(i, width=140, anchor="center")  
        
        values=[]
        selected_element = self.combobox0.get()
        values.append(selected_element)
        selected_result = self.combobox1.get()
        values.append(selected_result)
        
        results = self.Ergebnisse[selected_element][selected_result]
        for result in results:
            values.append(result)
        
        treeview.insert(parent="",index= 0, values=values)
        treeview.pack()
    
    def create_node_table(self):
        values = []
        new_window1 = tk.Toplevel(self.info_frame)
        new_window1.title("Knoten")
        
        treeview = ttk.Treeview(new_window1, columns=tuple(range(5)), show="headings", height=1)
        treeview.heading(0, text="Knoten")
        treeview.heading(1, text="u")
        treeview.heading(2, text="w")
        treeview.heading(3, text="\u03C6")
        treeview.heading(4, text="FG-Winkel[°]")
        for i in range(5):
            treeview.column(i, width=100, anchor="center")
        
        selected_node = self.combobox2.get()
        values.append(selected_node)
        for result in self.node_results[selected_node]:
            values.append(result)
        treeview.insert(parent="",index= 0, values=values)
        
        treeview.pack()
        
    
    def Moment(self):
        self.plot = "Moment"
        self.plotten()
    
    def Querkraft(self):
        self.plot = "Querkraft"
        self.plotten()
    
    def Normalkraft(self):
        self.plot = "Normalkraft"
        self.plotten()
        
    def Gesamtverformung(self):
        self.plot = "Gesamtverformung"
        self.plotten()
        
    
    def plotten(self):
        #System plotten
        self.fig.clear()
        self.toolbar.update()
        ax = self.fig.add_subplot(111)
        ax.set_xlim(0,21)
        ax.set_ylim(0,21)
        ax.set_xticks([])  # x-Achsenbeschriftungen ausschalten
        ax.set_yticks([])  # y-Achsenbeschriftungen ausschalten
        ax.invert_yaxis()
        ax.set_aspect("equal")#verhältnisse bleiben gleich, wird nicht verzerrt
        self.fig.subplots_adjust(left=0.06, right=0.94, bottom=0.06, top=0.94)
        
        n_auswertungen = 40 #Anzahl Auswertepunkte im Element, war ursprünglich 20, aber erhöht wegen besserer darstellung beim speichern
        for element in self.System:
            x_list = np.linspace(element.knoten_1.x, element.knoten_2.x, num= n_auswertungen).tolist()
            y_list = np.linspace(element.knoten_1.y, element.knoten_2.y, num= n_auswertungen).tolist()
            ax.plot(x_list, y_list, "b-", linewidth = 0.8)
            
        
        for element in self.System:
            
            #Punkte zum Plotten des Verlaufs
            el_x = np.linspace(element.knoten_1.x, element.knoten_2.x, num= n_auswertungen).tolist()
            el_y = np.linspace(element.knoten_1.y, element.knoten_2.y, num= n_auswertungen).tolist()
                
            #Auswertepunkte des Elements
            x_lokal = np.linspace(0, element.l, num= n_auswertungen)
                
            #SGR an den Auswertepunkten bestimmen
            M = []
            V = []
            N = [] 
            w = []
            u = []
            Transformationsmatrix = element.Transformationsmatrix()
            
            for x in x_lokal:
                
                m_x = element.Moment(x, self.u_sys)
                M.append(m_x[0,0]) 
                
                v_x = element.Querkraft(x, self.u_sys)
                V.append(v_x[0,0])
                
                n_x = element.Normalkraft(x, self.u_sys)
                N.append(n_x[0,0])
                
                w_x_l = element.Biegelinie(x, self.u_sys)
                u_x_l = element.Längsverschiebung(x, self.u_sys)
                
                wu_lokal = np.array([[u_x_l[0,0], w_x_l[0,0], 0, 0, 0, 0]])
                wu_global = wu_lokal @ Transformationsmatrix
                w_x_g = wu_global[0,1]
                u_x_g = wu_global[0,0]
                u.append(u_x_g)
                w.append(w_x_g) 
            
            
            W = [y + self.scale_factor_sys * w_val for y, w_val in zip(el_y, w)]
            U = [x + self.scale_factor_sys * u_val for x, u_val in zip(el_x, u)]
            
            deformed = [U, W]
            
            #Winkel berechnen, damit Verlauf senkrecht auf Element steht
            angle = np.arctan2(element.l_y, element.l_x)
            angle += np.pi/2
            
            M_x = [x + M_val * 1/self.scale_factor_sgr * np.cos(angle) for x, M_val in zip(el_x, M)]
            M_y = [y + M_val * 1/self.scale_factor_sgr * np.sin(angle) for y, M_val in zip(el_y, M)]
            M_plot = [M_x, M_y]
            
            V_x = [x + V_val * 1/self.scale_factor_sgr * np.cos(angle) for x, V_val in zip(el_x, V)]
            V_y = [y + V_val * 1/self.scale_factor_sgr * np.sin(angle) for y, V_val in zip(el_y, V)]
            V_plot = [V_x, V_y]
            
            N_x = [x + N_val * 1/self.scale_factor_sgr * np.cos(angle) for x, N_val in zip(el_x, N)]
            N_y = [y + N_val * 1/self.scale_factor_sgr * np.sin(angle) for y, N_val in zip(el_y, N)]
            N_plot = [N_x, N_y]
            
            
            
            if self.plot == "Moment":
                ax.plot(M_plot[0],M_plot[1], "r-", linewidth = 0.8)
                ax.plot([el_x[0], M_x[0]], [el_y[0], M_y[0]], "r-", linewidth = 0.8)
                ax.plot([el_x[-1], M_x[-1]], [el_y[-1], M_y[-1]], "r-", linewidth = 0.8)
                ax.set_title("Momentenverlauf", fontsize = 10)
                ax.text(M_plot[0][0], M_plot[1][0], f"{round(M[0])}", fontsize = 6)
                ax.text(M_plot[0][-1], M_plot[1][-1], f"{round(M[-1])}", fontsize = 6)
                self.canvas_info.draw()
               
            
            elif self.plot =="Querkraft":
                ax.plot(V_plot[0],V_plot[1], "r-", linewidth = 0.8)
                ax.plot([el_x[0], V_x[0]], [el_y[0], V_y[0]], "r-", linewidth = 0.8)
                ax.plot([el_x[-1], V_x[-1]], [el_y[-1], V_y[-1]], "r-", linewidth = 0.8)
                ax.set_title("Querkraftverlauf", fontsize = 10, )
                ax.text(V_plot[0][0], V_plot[1][0], f"{round(V[0])}", fontsize = 6)
                ax.text(V_plot[0][-1], V_plot[1][-1], f"{round(V[-1])}", fontsize = 6)
                self.canvas_info.draw()
                
                
            elif self.plot == "Normalkraft":
                ax.plot(N_plot[0],N_plot[1], "r-", linewidth = 0.8)
                ax.plot([el_x[0], N_x[0]], [el_y[0], N_y[0]], "r-", linewidth = 0.8)
                ax.plot([el_x[-1], N_x[-1]], [el_y[-1], N_y[-1]], "r-", linewidth = 0.8)
                ax.set_title("Normalkraftverlauf", fontsize = 10 )
                ax.text(N_plot[0][0], N_plot[1][0], f"{round(N[0])}", fontsize = 6)
                ax.text(N_plot[0][-1], N_plot[1][-1], f"{round(N[-1])}", fontsize = 6)
                self.canvas_info.draw()
                
            
            elif self.plot == "Gesamtverformung":
                ax.plot(deformed[0],deformed[1], "g-", linewidth = 0.8)
                ax.set_title("Systemverformung", fontsize = 10, )
                self.canvas_info.draw()
        
            
            
      
    def delete(self):
        
        self.canvas.delete("all")
        self.draw_grid()
        self.fig.clear()
        self.canvas_info.draw()
        self.combobox0.configure(values=())
        self.combobox1.configure(values=())
        self.combobox2.configure(values=())
        self.combobox0.set("Element wählen")
        self.combobox1.set("Elementgröße wählen")
        self.combobox2.set("Knoten wählen")
        self.combobox_theorie.set("Theorie wählen")
        self.scale_sys.set(100)
        self.scale_sgr.set(20)
        self.toolbar.update()
        
        #löschen
        self.u_sys = None
        self.Ergebnisse = None
        self.node_results = None
        self.plot = None
        self.theorie = None
        self.allow_draw = True
        
        #Knoten speichern 
        self.n_node = 0
        self.knoten_liste=[ [], [] ] #für Knoten und Canvas Koordinaten
        self.create_element_knoten = [ [], [] ]
        self.node_id_show=0
        
        self.n_el = 0 #Anzahl Elemente
        self.System = []
        self.el_id_show = 0
        self.doppelter_knoten_id = 0
        
        self.doppelter_knoten_id_show =100 #doppelter Knoten hat id 100,101,102...
        
        #Randbedingungen für Loesen
        self.alr_rb = []
        self.knotenlasten = []
    
    def update_mouse_position(self, event):
        # Mausposition Ursprung oben links
        x = event.x 
        y = event.y
        # Koordinaten umrechnen, geht bis (21,21)
        x_coord = round(x / 30)
        y_coord = round(y / 30)
        # Koordinaten im Label aktualisieren
        self.pos_label.config(text=f'Mausposition: ({x_coord}, {y_coord})')
        
    def draw_grid(self):
        
        self.canvas.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        for x in range(0, canvas_width, 30):
            for y in range(0, canvas_height, 30):
                self.canvas.create_oval(x-1, y-1, x+1, y+1, fill="black")
                
        self.canvas.create_line(30, 30, 30, 75, fill="black", arrow=tk.LAST)
        self.canvas.create_line(30, 30, 75, 30, fill="black", arrow=tk.LAST)
        self.canvas.create_arc(20,20, 75, 75, outline= "black", fill="", style= tk.ARC, start = 260, extent= 110)
        x1, y1 = 75, 35  
        x2, y2 = 70, 45  
        x3, y3 = 80, 45  
        self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, fill="black")
        
        # Beschriftungen hinzufügen
        self.canvas.create_text(18, 52, text="z,w", fill="black")
        self.canvas.create_text(52, 22, text="x,u", fill="black")
        self.canvas.create_text(75, 70, text="\u03C6", fill="black")  

    #zeichnen aktivieren bei klicken in das canvas
    def acitvate_drawing(self):
        if self.allow_draw == True:
            self.canvas.bind("<Button-1>", self.draw)
        else: 
            info = tk.Toplevel()
            info.title("Information")
            info_label = ttk.Label(info, text="Geladene Systeme können nicht bearbeitet werden. Zum Zeichnen System löschen.")
            info_label.pack(padx= 5)
            info_button = ttk.Button(info, text="OK", command=info.destroy)
            info_button.pack()
            info.grab_set()
            
        
    def draw(self, event):
        
        self.theorie = self.combobox_theorie.get()
        
        #eventuell bei activate drawing machen
        if self.theorie =="Theorie wählen":
            info = tk.Toplevel()
            info.geometry("200x50")
            info.title("Information")
            
            info_label = ttk.Label(info, text="Bitte Theorie wählen!")
            info_label.pack()
            info_button = ttk.Button(info, text="OK", command=info.destroy)
            info_button.pack()
            info.grab_set()
            self.wait_window(info)
            
        self.canvas.update()
        knoten_existiert = False
        
        #koordinaten
        x_coord = round((event.x/30)) 
        y_coord = round((event.y/30))
        x = x_coord *30 
        y = y_coord *30
        
        i = -1
        
       #wenn es noch keinen knoten gibt wird einer erstellt
        if self.knoten_liste[0] == []:
            self.create_node(x_coord, y_coord, x, y)
        
        else: 
            
            #Knotenliste durchlaufen 
            for knoten in self.knoten_liste[0]:
                
                i += 1
                
                #Schauen ob Knoten bereits existiert
                if knoten.x == x_coord and knoten.y == y_coord:
                    
                    #existiert also auswählen was man machen möchte
                    dialog = KnotenDialog() #(self, knoten)
                    result = dialog.result
                    knoten_existiert = True
                    
                    #Knoten wird Elementliste angehängt
                    
                    
                    if result == "element":
                        
                        self.create_element_knoten[0].append(knoten)
                        
                        self.create_element_knoten[1].append(self.knoten_liste[1][i])
                        
                        #falls Elementliste 2 Knoten beinhaltet, wird ein Element aus den beiden Knoten erstellt
                        
                        if len(self.create_element_knoten[0])==2:
                            self.create_element(self.create_element_knoten.copy())
                            #liste wrd wieder geleert
                            self.create_element_knoten = [[], []]
                            #funktion wird verlassen
                            return
                        
                        #sonst passiert nichts
                        else:
                            return
                        
                    #hier wird ein doppelter Knoten erstellt    
                    elif result =="knoten":
                        
                        #mit geklicktem Knoten aufrufen
                        DoppelterKnoten(self, knoten)
                        
                        
                        return
                    
            #wenn for schleife durchlaufen wurde und der Knoten noch nicht existiert wird er gezeichnet
            if knoten_existiert == False:
                self.create_node(x_coord, y_coord, x, y)    
    
        
    def create_node(self, x_coord, y_coord, x, y):
        knoten_id = self.canvas.create_oval(x-2, y-2, x+2, y+2, fill= "blue")
        last_alr = Last_ALR(self, x, y)
        last_alr.wait_window()
        #falls Fenster geschlossen ist wird funktion abgebrochen dass keine fehlermeldung entsteht
        if last_alr.lasten == []:
            self.canvas.delete(knoten_id)
            return

        self.n_node +=1
        self.node_id_show +=1
        #Knotenfreiheitsgrade
        knoten_fg = self.create_node_fg()
        #Auflager und Knotenlasten
        for i in range(3):#
            #Lasten und ALR zu zugehörigem fg
            fg = knoten_fg[i]
            last = last_alr.lasten[i]
            alr = last_alr.alr[i]
            
            if alr == 1:
                
                self.alr_rb.append([fg, 0])
                
            self.knotenlasten.append([fg, last])
        
        angle = last_alr.angle #Winkel für schräge ALR und Quer/Normalkraftgelenke
        self.knoten_liste[0].append(Knoten(knoten_id, x_coord, y_coord, knoten_fg, [x,y], self.node_id_show, angle)) #self.nnode hinzugefügt für id ab 1
        self.knoten_liste[1].append([x,y])
        
    def create_node_fg(self):
        
        node_fg = [1,2,3]
        
        if self.n_node == 1:
            return node_fg
        
        else: 
            
            for i in range(self.n_node-1):
                for j in range(3):
                    node_fg.append(node_fg[-1]+1)
                node_fg[0:3] = []
                
            return node_fg
            
        
    def create_element(self, create_element_knoten):
        
        #eventuell unnötig
        element_knoten = create_element_knoten[1]
        
        if create_element_knoten[0][0] == create_element_knoten[0][1]:
            #es wurde zweimal der gleiche Knoten angeklickt
            return
        
        x1, y1 = create_element_knoten[1][0][0], create_element_knoten[1][0][1] 
        x2, y2 = create_element_knoten[1][1][0], create_element_knoten[1][1][1]

        # Linie zwischen den Knoten zeichnen
        element_id = self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
        
        
        if self.theorie =="Theorie wählen":
            self.canvas.delete(element_id)
            return
        # Instanz der Klasse Elementeingabe erstellen
        self.elementeingabe = Elementeingabe(self, element_knoten)
        
        #wenn keine eingabe erfolgt ist, bzw das fenster einfach geschlossen wurde
        if self.elementeingabe.result == None: 
            self.canvas.delete(element_id)
            return
        
        self.el_id_show += 1
        self.n_el += 1
    
        #Eigenschaften aus Benutzereingabe
        new_element_EI = float(self.elementeingabe.result["EI"])
        new_element_EA = float(self.elementeingabe.result["EA"])
        new_element_qz = float(self.elementeingabe.result["qz"])
        new_element_qx = float(self.elementeingabe.result["qx"])
        new_element_lasten = [new_element_qz, new_element_qx]
        
        if self.theorie != "Bernoulli":
            new_element_GAs = float(self.elementeingabe.result["GAs"])
        
        
        if self.theorie=="Bernoulli":
            
            new_element = Balkenelement(self.el_id_show, element_id, create_element_knoten[0], new_element_EI, new_element_EA, new_element_lasten)
        
        elif self.theorie=="Timoshenko mit Locking":
            
            new_element = Timoshenkobalken(self.el_id_show, element_id, create_element_knoten[0], new_element_EI, new_element_EA, new_element_GAs ,new_element_lasten)
            
        elif self.theorie=="Timoshenko reduzierte Integration":
                
            new_element = Timoshenkobalken_reduziert(self.el_id_show, element_id, create_element_knoten[0], new_element_EI, new_element_EA, new_element_GAs ,new_element_lasten)
         
        elif self.theorie=="Timoshenko ANS/DSG":
                
            new_element = Timoshenkobalken_ans_dsg(self.el_id_show, element_id, create_element_knoten[0], new_element_EI, new_element_EA, new_element_GAs ,new_element_lasten)
        
        elif self.theorie=="Timoshenko exakt":
                
            new_element = Timoshenkobalken_exakt(self.el_id_show, element_id, create_element_knoten[0], new_element_EI, new_element_EA, new_element_GAs ,new_element_lasten)
             
        self.System.append(new_element)
        

class Last_ALR(tk.Toplevel):
    
    def __init__(self, parent, x, y):
        super().__init__()
        self.title("Knoten")
        self.parent = parent
        
        self.lasten = []
        self.alr = []
        self.x = x
        self.y = y
        
        self.label1 = ttk.Label(self, text = "ALR:")
        self.label1.grid(row= 0, column= 1, padx= 5, pady= 5, sticky= tk.W)
        
        self.u = tk.IntVar()
        self.u_checkbutton = ttk.Checkbutton(self, text="u", variable= self.u)
        self.u_checkbutton.grid(row= 1, column= 1, padx=5, pady= 5, sticky= tk.W)
        
        self.w = tk.IntVar()
        self.w_checkbutton = ttk.Checkbutton(self, text="w", variable= self.w)
        self.w_checkbutton.grid(row= 2, column= 1, padx=5, pady= 5, sticky= tk.W)
        
        self.phi = tk.IntVar()
        self.phi_checkbutton = ttk.Checkbutton(self, text="\u03C6", variable= self.phi)
        self.phi_checkbutton.grid(row= 3, column= 1, padx=5, pady= 5, sticky= tk.W)
        
        self.label2 = ttk.Label(self, text= "Knotenlast:")
        self.label2.grid(row= 0, column = 2, padx= 5, pady=5)
        
        self.label3 = ttk.Label(self, text= "F_x")
        self.label3.grid(row= 1, column = 2, padx= 5, pady=5)
        self.label4 = ttk.Label(self, text= "F_z")
        self.label4.grid(row= 2, column = 2, padx= 5, pady=5)
        self.label5 = ttk.Label(self, text= "M_y")
        self.label5.grid(row= 3, column = 2, padx= 5, pady=5)
        
        self.entry_fx = ttk.Entry(self, textvariable= tk.StringVar, width= 3)
        self.entry_fx.grid(row= 1, column = 3, padx=5, pady= 5, sticky= tk.W)
        
        self.entry_fz = ttk.Entry(self, textvariable= tk.StringVar, width= 3)
        self.entry_fz.grid(row= 2, column = 3, padx=5, pady= 5, sticky= tk.W)
        
        self.entry_my = ttk.Entry(self, textvariable= tk.StringVar, width= 3)
        self.entry_my.grid(row= 3, column = 3, padx=5, pady= 5, sticky= tk.W)
        
        self.label_angle = ttk.Label(self, text = "FG-Winkel in °")
        self.label_angle.grid(row= 4, column = 0, padx =5, pady= 5, sticky= tk.W, columnspan= 2)
        
        self.entry_angle = ttk.Entry(self, textvariable= tk.StringVar, width= 3)
        self.entry_angle.grid(row= 4, column=2, padx=5, pady= 5, sticky= tk.W)
        self.entry_angle.insert(0,"0")
        self.button1 = ttk.Button(self,text= "save" , command= self.save_eingabe, width= 6)
        self.button1.grid(row=5, column= 0, columnspan=4, padx=5, pady=5)
        self.grab_set()
        
        
    def save_eingabe(self):
        
        lasten = [self.entry_fx.get(), self.entry_fz.get(), self.entry_my.get()]
        self.angle = float(self.entry_angle.get()) #Winkel positiv, wenn die FG gegen den Uhrzeigersinn gedreht sind (math positiv)
        angle = math.radians(self.angle)
        
        if lasten[0] == "" or float(lasten[0]) == 0:
            self.lasten.append(0)
                
        elif float(lasten[0])!= 0:
            fx=float(lasten[0])
            
            self.lasten.append(fx)
            
            if fx < 0:
                arrow_position = tk.LAST
            else:
                arrow_position = tk.FIRST
            #Last zeichnen
            if self.angle==0:
                self.parent.canvas.create_line(self.x-5, self.y, self.x-30, self.y, arrow = arrow_position, fill= "red" )
            else: 
                x1, y1 = self.node_transformation(self.x-5, self.y, angle)
                x2, y2 = self.node_transformation(self.x-30, self.y, angle)
                self.parent.canvas.create_line(x1, y1, x2, y2, arrow = arrow_position, fill= "red" )
            
        if lasten[1] == "" or float(lasten[1]) == 0:
            self.lasten.append(0)
            
        elif float(lasten[1]) != 0:
            fz=float(lasten[1])
            self.lasten.append(fz)
            if fz < 0:
                arrow_position = tk.LAST
            else:
                arrow_position = tk.FIRST
            #Last zeichnen
            if self.angle ==0: 
                self.parent.canvas.create_line(self.x, self.y-5, self.x, self.y-30, arrow = arrow_position, fill= "red" )
            else: 
                x1, y1 = self.node_transformation(self.x, self.y-5, angle)
                x2, y2 = self.node_transformation(self.x, self.y-30, angle)
                self.parent.canvas.create_line(x1, y1, x2, y2, arrow = arrow_position, fill= "red" )
                
        if lasten[2] == "" or float(lasten[2]) == 0:
            self.lasten.append(0)
            
        elif float(lasten[2]) != 0:
            my=float(lasten[2])
            self.lasten.append(my)
            if my< 0:
                self.parent.canvas.create_arc(self.x-25, self.y-25, self.x+25, self.y+25, outline= "red", fill="", style= tk.ARC)
                self.parent.canvas.create_line(self.x+25, self.y, self.x+29, self.y-6, fill="red")
                self.parent.canvas.create_line(self.x+25, self.y, self.x+21, self.y-6, fill="red")
                
            else:
                self.parent.canvas.create_arc(self.x-25, self.y-25, self.x+25, self.y+25, outline= "red", fill="", style= tk.ARC)
                self.parent.canvas.create_line(self.x, self.y-25, self.x+7, self.y-28, fill="red")
                self.parent.canvas.create_line(self.x, self.y-25, self.x+7, self.y-20, fill="red")
       
        
        self.alr = [self.u.get(), self.w.get(), self.phi.get()]
        
        #ALR zeichnen
        if self.alr[0] ==1:
            x1, y1 = self.node_transformation(self.x, self.y, angle)
            x2, y2 = self.node_transformation(self.x-6, self.y+6, angle)
            x3, y3 = self.node_transformation(self.x-6, self.y-6, angle)
            
            self.parent.canvas.create_polygon(x1,y1,x2,y2, x3, y3, outline = "blue", fill = "")
            
            
        
        if self.alr[1]==1:
            x1, y1 = self.node_transformation(self.x, self.y, angle)
            x2, y2 = self.node_transformation(self.x+6, self.y+6, angle)
            x3, y3 = self.node_transformation(self.x-6, self.y+6, angle)
            
            self.parent.canvas.create_polygon(x1,y1,x2,y2, x3, y3, outline = "blue", fill = "")
            
        
        if self.alr[2]==1:
            self.parent.canvas.create_polygon(self.x+3, self.y-3, self.x+3, self.y+3, self.x-3, self.y+3, self.x-3, self.y-3, outline = "blue", fill = "")
            
        self.destroy()
    
    
    def node_transformation(self, x, y, angle):
        
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        #translation zum koordinatenursprung (x-self.x, y-self.y)
        #rotation mit cos sin, rücktransformation indem self.x,y aufaddiert wird
        x_neu = self.x + (x - self.x) * cos_angle + (y - self.y) * sin_angle
        y_neu = self.y - (x - self.x) * sin_angle + (y - self.y) * cos_angle

        return x_neu, y_neu
    
class KnotenDialog(tk.Toplevel):
    
    def __init__(self):# , parent, knoten):
        
        super().__init__()# (parent)
        #self.transient(parent)
        #self.knoten = knoten
        self.result = None
        self.title("Option wählen")
        
        button1 = ttk.Button(self, text="Element erstellen", command=self.element_erstellen)
        button1.pack(pady=10, padx= 10)
        button2 = ttk.Button(self, text="doppelter Knoten ", command=self.knoten_einfügen)
        button2.pack(pady=10, padx= 10)
        self.grab_set()
        self.wait_window()
        
    
    def element_erstellen(self):
        
        self.result = "element"
        self.destroy()
        
    def knoten_einfügen(self):
        
        self.result = "knoten"
        self.destroy()
        

class DoppelterKnoten(tk.Toplevel):
    
    def __init__(self, parent, knoten):
        super().__init__()
        self.title("Doppelter Knoten")
        self.parent = parent
        self.knoten = knoten
        self.node_elements = self.get_Elements(knoten)
        self.n_doppelter_knoten = 0
            
            
        self.label1 = ttk.Label(self, text = "Knoten-ID:")
        self.label1.grid(row= 0, column= 0, padx= 10, pady= 10, sticky= tk.W)
        self.label2 = ttk.Label(self, text = str(self.knoten.id_show)) #neu mit show
        self.label2.grid(row= 0, column= 1, padx= 10, pady= 10, sticky= tk.W)
        
        self.label3 = ttk.Label(self, text = "Zugehörige Elemente [ID]:")
        self.label3.grid(row= 1, column= 0, padx= 10, pady= 10, sticky= tk.W)
        
        #Dictonairy mit den Elementen und den checkboxen der Knoten, am Ende überprüfen 
        #welcher Knoten zu welchem Element gehört
        self.dict = {}
        self.doppelte_knoten_dict = {}
            
        self.current_column = 1
        self.current_row = 0
            
        self.max_fg = self.parent.knoten_liste[0][-1].fg[-1]
    
        
        for i, element in enumerate(self.node_elements): # gibt index in der Liste und wert zurück
                
                
            self.current_row = i + 2
                
            label_el = ttk.Label(self, text = f"{element.id_show}")
            label_el.grid(row= self.current_row, column= 0, padx= 10, pady= 10, sticky= tk.W)
        
            
            entry = ttk.Entry(self, textvariable= tk.StringVar(), width = 3) #1 (ja) oder 2 (nein) eingeben
            entry.grid(row= self.current_row, column = 1,padx=10, pady=5)
                
            entry_list = [entry, self.knoten.id]
                
            self.dict[element] = []
            self.dict[element].append(entry_list)  #speicher Entry des Elements und Knoten ID
                                                    #damit man später nachschauen kann ob der Knoten zu dem Element gehört
            
           
        
        self.label4 = ttk.Label(self, text = "Freiheitsgrade:")
        self.label4.grid(row= self.current_row + 1, column= 0, padx= 10, pady= 10, sticky= tk.W)
        
        self.label5 = ttk.Label(self, text = "u:")
        self.label5.grid(row= self.current_row + 2, column= 0, padx= 10, pady= 10, sticky= tk.W)
        
        
        self.label6 = ttk.Label(self, text = "w:")
        self.label6.grid(row= self.current_row + 3, column= 0, padx= 10, pady= 10, sticky= tk.W)
        
        self.label7 = ttk.Label(self, text = "\u03C6:")
        self.label7.grid(row= self.current_row + 4, column= 0, padx= 10, pady= 10, sticky= tk.W)
        
        self.label_angle = ttk.Label(self, text= "FG-Winkel:")
        self.label_angle.grid(row= self.current_row + 5, column=0, padx= 10, pady= 10, sticky= tk.W)
        
        self.label_u = ttk.Label(self, text = f"{self.knoten.fg[0]}")
        self.label_u.grid(row= self.current_row + 2, column= 1, padx= 10, pady= 10, sticky= tk.W)
        
        
        self.label_w = ttk.Label(self, text = f"{self.knoten.fg[1]}")
        self.label_w.grid(row= self.current_row + 3, column= 1, padx= 10, pady= 10, sticky= tk.W)
        
        self.label_phi = ttk.Label(self, text = f"{self.knoten.fg[2]}")
        self.label_phi.grid(row= self.current_row + 4, column= 1, padx= 10, pady= 10, sticky= tk.W)
        
        self.label_angle_show = ttk.Label(self, text= f"{self.knoten.angle}°")
        self.label_angle_show.grid(row= self.current_row + 5, column=1, padx= 10, pady= 10, sticky= tk.W)
            
        self.label8 = ttk.Label(self, text=f"Max System-FG: {self.max_fg}")
        self.label8.grid(row=self.current_row + 6, column=0, pady=10, sticky= tk.W)
                
        self.button1 = ttk.Button(self, text="Neu", command=self.new_node, width= 3)
        self.button1.grid(row=self.current_row + 7, column=0, pady=10, sticky= tk.W)
        
        self.button2 = ttk.Button(self, text="save", command=self.save)
        self.button2.grid(row=self.current_row + 7, column=1, pady=10, sticky= tk.W)
                
        self.grab_set()
        self.wait_window()
        
    
    def save(self):
       
       #Alle Knoten erstellen, mit Koordinaten des ausgewählten self.Knoten, FG und ID aus Liste
       new_nodes = []
       for knoten_id in self.doppelte_knoten_dict: #auf alle Knoten zugreifen
           knoten_fg = []    
       
           for fg in self.doppelte_knoten_dict[knoten_id][0]: # auf die fg des Knotens zugreifen
               
               knoten_fg.append(fg.get()) #Liste mit fg erstellen
               
           knoten_x = self.knoten.x
           knoten_y = self.knoten.y
           angle = self.knoten.angle
           knoten_canvas_coord = self.knoten.canvas_coord 
           id_show = self.doppelte_knoten_dict[knoten_id][1][0]
           knoten = Knoten(knoten_id, knoten_x, knoten_y, knoten_fg, knoten_canvas_coord, id_show, angle) #Knoten erstellen
           
           new_nodes.append(knoten) #Liste mit allen neuen Knoten
           #der Liste von MainWindow hinzufügen
           self.parent.knoten_liste[0].append(knoten)
           self.parent.knoten_liste[1].append(knoten_canvas_coord)
       
       #Elemente neu erstellen mit geänderten Knoten
       
       #über alle Elemente die betroffen sind iterieren 
       for element in self.dict:
           
           element_id = element.id
           
           #liste mit 1/0 und zugehörigem Knoten aufrufen, node =[1/0, id der Knoten (doppelte und der angeklickte)]
           for node in self.dict[element]:
               
               if node[0].get() == str(0):
                   
                   #nächster Schleifendurchlauf, da der Knoten nicht zum Element gehört
                   continue
               
                
               elif node[0].get() == str(1): #Knoten gehört zum Element
                   
                   new_node_id = node[1] #auf Knoten ID des Knotens der zu dem Element gehört zugreifen
                   
                   #1. der Knoten ist der angeklickte Knoten, eigentlich müsste das als Abfrage reichen,
                   #da der engeklickte Knoten der war mit dem die Elemente schon erstellt wurden. 
                   #der nächste fall ist, dass der angeklickte nicht der ist. 
                   if self.knoten.id == new_node_id: 
                       break #break da jedes Element ja nur zu einem der Knoten gehören kann, kann zum nächsten Element gegangen werden 
                       
                   else:
                       #der Knoten ist nicht der ausgwählte, d.h das Element muss mit dem doppelten Knoten
                       #neu erstellt werden
                       #neuen Knoten aus Liste holen
                       new_node = None
                       
                       for knoten in new_nodes:
                           
                           if knoten.id == new_node_id:
                               new_node = knoten
                       
                                
                       el_node_1 = element.knoten_1
                       el_node_2 = element.knoten_2
                                
                       if el_node_1 == self.knoten:
                           
                           el_node_1 = new_node
                            #der knoten 1 des Elements ist der ausgwälte Knoten, dieser ist aber nicht der neue Knoten
                            #deshalb ist Knoten2 der Knoten der erhalten bleibt und Knoten 1 wird durch new node ersetzt
                       
                       else:
                           el_node_2 = new_node
                       
                       
                       new_element_id = element_id
                       new_element_knoten = [el_node_1, el_node_2]
                       new_element_EI = element.EI
                       new_element_EA = element.EA
                       new_element_lasten = [element.q, element.n]
                        
                       id_show = element.id_show
                       
                       if self.parent.theorie != "Bernoulli":
                           new_element_GAs = element.GA_s
                       
                       if self.parent.theorie == "Bernoulli":
                           new_element = Balkenelement(id_show, new_element_id, new_element_knoten, new_element_EI, new_element_EA, new_element_lasten)
                       
                       elif self.parent.theorie == "Timoshenko mit Locking":
                           new_element = Timoshenkobalken(id_show, new_element_id, new_element_knoten, new_element_EI, new_element_EA, new_element_GAs, new_element_lasten)
                       
                       elif self.parent.theorie == "Timoshenko exakt":
                           new_element = Timoshenkobalken_exakt(id_show, new_element_id, new_element_knoten, new_element_EI, new_element_EA, new_element_GAs, new_element_lasten)
                           
                       elif self.parent.theorie == "Timoshenko reduzierte Integration":
                           new_element = Timoshenkobalken_reduziert(id_show, new_element_id, new_element_knoten, new_element_EI, new_element_EA, new_element_GAs, new_element_lasten)
                           
                       elif self.parent.theorie == "Timoshenko ANS/DSG":
                           new_element = Timoshenkobalken_ans_dsg(id_show, new_element_id, new_element_knoten, new_element_EI, new_element_EA, new_element_GAs, new_element_lasten)
                           
                    
                       #altes Element löschen
                       
                       for el in self.parent.System:
                           if el.id ==element_id:
                               old_element = el
                       
                       self.parent.System.remove(old_element)
                        
                       self.parent.System.append(new_element)
       self.destroy()                
                   
    def get_Elements(self, knoten):
        
        node_elements = []
        
        
        for element in self.parent.System:
            
            if knoten.id in [element.knoten_1.id, element.knoten_2.id]:
                node_elements.append(element)
                
        return node_elements
                
    
    def new_node(self):
        
        #verändert
        self.parent.doppelter_knoten_id_show +=1
        #verändert
        #beim Zeichnen eines doppelten Knotens wird dem Knoten ein Rand hinzugefügt
        self.parent.doppelter_knoten_id += 1
        self.parent.n_node +=1
        self.current_column += 1
        self.n_doppelter_knoten +=1
        
        
        color = "green"
        
        self.parent.canvas.itemconfig(self.knoten.id, outline= color, width=2)
        
        label_new_node = ttk.Label(self, text=f"{self.parent.doppelter_knoten_id_show}") 
        label_new_node.grid(row=0, column= self.current_column, padx=10, pady=10, sticky=tk.W)
        
        for i, element in enumerate(self.node_elements):
            
            new_entry = ttk.Entry(self, textvariable= tk.StringVar(), width = 3) #0 oder 1 eingeben
            new_entry.grid(row= i + 2, column = self.current_column,padx=10, pady=5)
            
            new_entry_list = [new_entry, self.parent.doppelter_knoten_id]
            self.dict[element].append(new_entry_list)
        
        #koordinaten übernehemen, fg verändern je nachdem welchen
        
        node_u = ttk.Entry(self, textvariable= tk.StringVar(), width = 3)
        node_u.grid(row= self.current_row + 2, column= self.current_column, padx= 10, pady= 10, sticky= tk.W)
        node_u.insert(0, str(self.knoten.fg[0]))
        
        node_w = ttk.Entry(self, textvariable= tk.StringVar(), width = 3)
        node_w.grid(row= self.current_row + 3, column= self.current_column, padx= 10, pady= 10, sticky= tk.W)
        node_w.insert(0, str(self.knoten.fg[1]))
        
        node_phi = ttk.Entry(self, textvariable= tk.StringVar(), width = 3)
        node_phi.grid(row= self.current_row + 4, column= self.current_column, padx= 10, pady= 10, sticky= tk.W)
        node_phi.insert(0, str(self.knoten.fg[2]))
        
    
        self.doppelte_knoten_dict[self.parent.doppelter_knoten_id] = []
        self.doppelte_knoten_dict[self.parent.doppelter_knoten_id].append([node_u, node_w, node_phi]) 
        self.doppelte_knoten_dict[self.parent.doppelter_knoten_id].append([self.parent.doppelter_knoten_id_show])
        
    
class Elementeingabe(tk.Toplevel):
    
    def __init__(self, parent, knoten):  
        super().__init__()
        self.title("Elementeigenschaften")
        #self.transient(parent)
        self.knoten = knoten
        self.parent= parent
        
        
        self.EI_label = ttk.Label(self, text = "EI")
        self.EI_entry = ttk.Entry(self)
        self.EI_label.grid(row= 0, column= 0, padx=10, sticky= tk.W)
        self.EI_entry.grid(row= 0, column= 1, padx=10, sticky= tk.E)
        
        self.EA_label = ttk.Label(self, text = "EA")
        self.EA_entry = ttk.Entry(self)
        self.EA_label.grid(row= 1, column= 0, padx= 10, sticky= tk.W)
        self.EA_entry.grid(row= 1, column= 1, padx=10, sticky= tk.E)
        
        self.qz_label = ttk.Label(self, text = "Linienlast q_z lokal")
        self.qz_entry = ttk.Entry(self)
        self.qz_label.grid(row= 2, column= 0, padx= 10, sticky= tk.W)
        self.qz_entry.grid(row= 2, column= 1, padx=10, sticky= tk.E)
        
        self.qx_label = ttk.Label(self, text = "Linienlast q_x lokal")
        self.qx_entry = ttk.Entry(self)
        self.qx_label.grid(row= 3, column= 0, padx= 10, sticky= tk.W)
        self.qx_entry.grid(row= 3, column= 1, padx=10, sticky= tk.E)
        
        
        #GAs falls zu Beginn Timoshenkotheorie ausgewählt wurde
        if self.parent.theorie != "Bernoulli":
            self.GAs_label = ttk.Label(self, text = "GAs")
            self.GAs_entry = ttk.Entry(self)
            self.GAs_label.grid(row= 4, column= 0, padx= 10, sticky= tk.W)
            self.GAs_entry.grid(row= 4, column= 1, padx=10, sticky= tk.E)
            
        
        
        self.create_button = ttk.Button(self, text="Erstellen", command=self.create)
        self.create_button.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        self.result = None
        self.grab_set()
        self.wait_window()
        
    
    def create(self):
        
        if self.EI_entry.get() == "":
            self.EI_entry.insert(0, 1000)
        if self.EA_entry.get() == "":
            self.EA_entry.insert(0, 1000)
        if self.qz_entry.get() == "":
            self.qz_entry.insert(0, 0)
        if self.qx_entry.get() == "":
            self.qx_entry.insert(0, 0)
            
        
        self.result = {
            "EI": self.EI_entry.get(),
            "EA": self.EA_entry.get(),
            "qz": self.qz_entry.get(),
            "qx": self.qx_entry.get()}
        
        if self.parent.theorie != "Bernoulli":
        
            if self.GAs_entry.get() == "":
                self.GAs_entry.insert(0, 0)
                
            self.result["GAs"] = self.GAs_entry.get()
        
        if self.result["qz"] != str(0):
            qz = float(self.result["qz"])
            
            if qz < 0:
                arrow_position = tk.LAST
            else:
                arrow_position = tk.FIRST
            #Linienlast zeichnen, eventuell mit gestrichelter Faser übeprüfen
            x1, y1, x2, y2 = self.knoten[0][0], self.knoten[0][1], self.knoten[1][0], self.knoten[1][1]
            
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            
            angle = math.atan2(y2-y1, x2-x1)
            arrow_angle = angle + math.pi / 2
            arrow_length = 20  # Länge der Pfeile
            arrow_dx = arrow_length * math.cos(arrow_angle)
            arrow_dy = arrow_length * math.sin(arrow_angle)
            self.parent.canvas.create_line(x1, y1, x1 - arrow_dx, y1 - arrow_dy, arrow= arrow_position, fil="red")
            self.parent.canvas.create_line(x2, y2, x2 - arrow_dx, y2 - arrow_dy, arrow=arrow_position, fill= "red")
            self.parent.canvas.create_line(x_center, y_center, x_center - arrow_dx, y_center - arrow_dy, arrow=arrow_position, fill= "red")
            self.parent.canvas.create_line(x1 - arrow_dx, y1 - arrow_dy, x2 - arrow_dx, y2 - arrow_dy, fill="red")
        
        if self.result["qx"] != str(0):
            qx = float(self.result["qx"])
            if qx < 0: 
                arrow_position = tk.FIRST
            else: 
                arrow_position = tk.LAST
            
            x1, y1, x2, y2 = self.knoten[0][0], self.knoten[0][1], self.knoten[1][0], self.knoten[1][1]
            angle = math.atan2(y2-y1, x2-x1) + math.pi/2
            arrow_length = 20
            dx = arrow_length * math.cos(angle)
            dy = arrow_length * math.sin(angle)
            
            self.parent.canvas.create_line(x1, y1, x1 - dx, y1 - dy, fil="red")
            self.parent.canvas.create_line(x2, y2, x2 - dx, y2 - dy, fill= "red")
            self.parent.canvas.create_line(x1 - dx, y1 - dy, x2 - dx, y2 - dy, fill="red")
            self.parent.canvas.create_line(x1 - dx/2, y1 - dy/2, x2 - dx/2, y2 - dy/2, arrow= arrow_position, fill="red")
                
            
        self.destroy()

GUI = MainWindow()
GUI.mainloop()




