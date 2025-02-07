import tkinter as tk
import subprocess
import threading
import os
import shutil
import glob
import random
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import mrcfile
from scipy.fft import rfftn, irfftn
from scipy.ndimage import fourier_gaussian
import json

def display(output_text_step3, entry_pickedmics_dir, entry_picks_dir, entry_todisplay_step3, selected_order_step3, selected_picktype, filter_forpicks_checkbox, entry_config):
    global pickedmics
    picktype = selected_picktype.get()
    picks_dir = entry_picks_dir.get()
    pickedmics = entry_pickedmics_dir.get()
    order = selected_order_step3.get()
    filterflag = filter_forpicks_checkbox.get()

    with open(entry_config.get(), 'r') as config_file:
        config = json.load(config_file)

    cryolo_python = config.get("cryolo_python")
    cryolo_gui = config.get("cryolo_gui")
    cryolo_boxmanager = config.get("cryolo_boxmanager")

    # Add your BoxManager logic here
    output_text_step3.delete(1.0, tk.END)  # Clear previous output
    output_text_step3.insert(tk.END, "BoxManager started...\n")
    output_text_step3.see(tk.END)

    if not os.path.exists(pickedmics):
        output_text_step3.insert(tk.END, f"Cannot find the directory {pickedmics}.\n")
        output_text_step3.see(tk.END)

    # Create a function to run the BoxManager subprocess
    def run_boxmanager():

        miclist = glob.glob(os.path.join(pickedmics, '*.mrc'))
        miclist = [os.path.basename(file) for file in miclist]

        picklist = glob.glob(os.path.join(picks_dir,"STAR", '*.star'))
        picklist = sorted(picklist, key=lambda x: os.path.getmtime(x))
        picklist = [os.path.basename(file) for file in picklist]

        miclist = [item.split(".star")[0]+".mrc" for item in picklist if item.split(".star")[0]+".mrc" in miclist]

        ##########
        if not os.path.exists("Subflow"):
            os.makedirs("Subflow")

        global mictemp
        i=0
        mictemp=os.path.join("Subflow","temp-mics"+str(i))
        while os.path.exists(mictemp):
            mictemp=os.path.join("Subflow","temp-mics"+str(i))
            i+=1
        os.makedirs(mictemp)
        ###########

        if order == "Last":
            miclist = miclist.reverse()
        elif order == "Random":
            random.shuffle(miclist)

        if len(miclist) == 0:
            output_text_step3.insert(tk.END, f"Error: There are no picked micrographs.\n")
            output_text_step3.see(tk.END)
            return

        todisplay = entry_todisplay_step3.get()

        if todisplay not in ["all", "All", "ALL"]:
            if int(todisplay) > len(miclist):
                output_text_step3.insert(tk.END, f"Warning: There are only {len(miclist)} picked micrographs.\n")
                output_text_step3.see(tk.END)
                todisplay=len(miclist)
            miclist = miclist[0:int(todisplay)]

        if filterflag:

            # Use ProcessPoolExecutor to process files in parallel
            with ProcessPoolExecutor(max_workers=12) as executor:
                list(executor.map(process_file, miclist))

        else:

            for moveme in miclist:

                source_file_path = os.path.join(os.getcwd(), pickedmics, moveme)
                destination_file_path = os.path.join(os.getcwd(), mictemp, moveme)
                subprocess.run(["ln", "-sf", source_file_path, destination_file_path])

        try:
            cmd = [
                cryolo_python,
                cryolo_boxmanager,
                '-i', mictemp,
                '-b', os.path.join(picks_dir,picktype)
            ]

            # Run the BoxManager subprocess and capture both stdout and stderr
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read and display the output in real-time
            for line in process.stdout:
                output_text_step3.insert(tk.END, line)
                output_text_step3.see(tk.END)

            # Wait for the subprocess to complete
            process.wait()

            ##########
            shutil.rmtree(mictemp)
            ###########

            # Display a completion message
            output_text_step3.insert(tk.END, "BoxManager completed.\n")
            output_text_step3.see(tk.END)

        except subprocess.CalledProcessError as e:
            # Display an error message if the subprocess fails
            output_text_step3.insert(tk.END, f"Error running BoxManager: {e.stderr}\n")
            output_text_step3.see(tk.END)

    # Create a thread to run the BoxManager subprocess
    boxmanager_thread = threading.Thread(target=run_boxmanager, name="subflow-boxmanager")
    boxmanager_thread.daemon = True
    boxmanager_thread.start()


def low_pass_filter_mrc(input_path, output_path, cutoff=2.5):
    with mrcfile.open(input_path, mode='r') as mrc:
        data = mrc.data
    fft_data = rfftn(data)
    filtered_fft_data = fourier_gaussian(fft_data, sigma=cutoff)
    filtered_data = irfftn(filtered_fft_data, s=data.shape)
    with mrcfile.new(output_path, overwrite=True) as mrc:
        mrc.set_data(np.float32(filtered_data))

def process_file(processme):
    global pickedmics
    global mictemp
    source_file_path = os.path.join(os.getcwd(), pickedmics, processme)
    destination_file_path = os.path.join(os.getcwd(), mictemp, processme)
    low_pass_filter_mrc(source_file_path, destination_file_path)