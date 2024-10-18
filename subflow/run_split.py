import tkinter as tk
import subprocess
import threading
import os
import time
import sys

import starfile
import numpy as np
import pandas as pd
from subflow import updategui

class SplitOperation:
    
    def __init__(self):

        self.split_running = False
        self.split_thread_instance = None

    def split(self, output_text, entry_split_coordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics, notebook, jobalias):

        def split_thread():

            coordinate_dir=entry_split_coordinate_dir.get()
            splitvalue=int(entry_splitvalue.get())
            
            output_text.delete(1.0, tk.END)  # Clear previous output

            self.split_running = True
            updategui.set_update_flag(jobalias, True)
            updategui.change_tabtitle(notebook, jobalias)
            disable_ui_elements(output_text, entry_split_coordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics)

            split_final_dir = f"Split-{splitvalue}"
            if not os.path.exists(os.path.join(coordinate_dir, split_final_dir)):
                os.makedirs(os.path.join(coordinate_dir, split_final_dir))

            output_text.insert(tk.END, "Splitting...")

            while not os.path.exists(coordinate_dir):
                time.sleep(4)

            announced=False
            isempty=False
            empties = []
            while self.split_running:

                for coordinatefile in os.listdir(coordinate_dir):
                    if not self.split_running:
                        output_text.insert(tk.END, "Splitting stopped.\n")
                        output_text.see(tk.END)
                        updategui.set_update_flag(jobalias, False)
                        return

                    if coordinatefile.endswith("_resam_Zscore.star"):

                        source_file_path = os.path.join(os.getcwd(), coordinate_dir, coordinatefile)
                        destination_file_path = os.path.join(os.getcwd(), coordinate_dir, split_final_dir, coordinatefile)

                        coordinatefile_withpath = os.path.join(coordinate_dir, split_final_dir, coordinatefile)
                        outputstarsplit = coordinatefile_withpath.split("_resam_Zscore.star")[0]+"_resam_Zscore_helix_split.star"
                        outputtxtsplit = coordinatefile_withpath.split("_resam_Zscore.star")[0]+"_resam_Zscore_helix_split.txt"

                        if not os.path.exists(outputstarsplit) and coordinatefile not in empties:
                            subprocess.run(["ln", "-sf", source_file_path, destination_file_path])
                            try:
                                isempty = starsplit(coordinatefile_withpath, splitvalue, outputstarsplit, outputtxtsplit, output_text)
                                if isempty:
                                    empties.append(coordinatefile)

                            except Exception as e:
                                output_text.insert(tk.END, f"Error splitting {coordinatefile}: {str(e)}\n")

                            output_text.see(tk.END)
                            announced=False

                if not announced:
                    output_text.insert(tk.END, "\nLooking for new fit coordinate file...\n")
                    output_text.see(tk.END)
                    announced=True

                time.sleep(4)

        # Create and start the sync thread
        self.split_thread_instance = threading.Thread(target=split_thread, name=f"subflow-{jobalias}")
        self.split_thread_instance.daemon = True
        self.split_thread_instance.start()

    def stop_split(self, output_text, entry_split_coordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics, jobalias):
        self.split_running = False
        output_text.insert(tk.END, "Splitting stopping...\n")
        output_text.see(tk.END)
        enable_ui_elements(output_text, entry_split_coordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics)
        updategui.set_update_flag(jobalias, False)

def starsplit(coordinatefile, splitvalue, outputstarsplit, outputtxtsplit, output_text):
    with open(coordinatefile, 'r') as file:
        last_line = file.readlines()[-1].strip()
        if last_line.startswith('_'):
            return 1
    coord_dataframe = starfile.read(coordinatefile)
    tube_list=coord_dataframe['rlnParticleSelectZScore'].tolist()
    result = [[x] * tube_list.count(x) for x in set(tube_list)]
    list_split=[]
    z=0
    for x in result:
        lenght=(len(x))
        mult=lenght//splitvalue
        remain=lenght%splitvalue
        if mult ==0:
            list_split.append([(z)]*(remain))
            num=max(list_split)       
            z=num[0]+1
        elif remain == 0:
            for y in range(z,z+mult):
                    list_split.append([y]*splitvalue)
            num=max(list_split)
            z=num[0]+1
        elif remain >= int(0.7*splitvalue):
            for y in range(z,z+mult):
                    list_split.append([y]*splitvalue)
            list_split.append([(z+mult+1)]*(remain))
            num=max(list_split)
            z=num[0]+1
        elif remain < int(0.7*splitvalue):
            for y in range(z,z+mult):
                list_split.append([y]*splitvalue)
            list_split.append([(z+mult-1)]*(remain))
            num=max(list_split)
            z=num[0]+1
    list_split=[subitem for item in list_split for subitem in item]
    coord_dataframe['rlnParticleSelectZScore']=list_split    
    starfile.write(coord_dataframe, outputstarsplit, overwrite=True)
    np.savetxt(outputtxtsplit, coord_dataframe.values, fmt='%7.13f %7.13f %7.13f %i', delimiter=' ')
    output_text.insert(tk.END, f"Split {outputtxtsplit}\n")
    output_text.see(tk.END)

    return 0

def disable_ui_elements(output_text, entry_split_coordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics):
    entry_split_coordinate_dir.config(state='disabled')
    entry_splitvalue.config(state='disabled')
    split_button.config(state='disabled')
    browse_button_split_coordinate_dir.config(state='disabled')
    entry_tosplitmics_dir.config(state='disabled')
    browse_button_tosplitmics.config(state='disabled')
    stop_split_button.config(state='normal')
def enable_ui_elements(output_text, entry_split_coordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics):
    entry_split_coordinate_dir.config(state='normal')
    entry_splitvalue.config(state='normal')
    split_button.config(state='normal')
    browse_button_split_coordinate_dir.config(state='normal')
    entry_tosplitmics_dir.config(state='normal')
    browse_button_tosplitmics.config(state='normal')
    stop_split_button.config(state='normal')