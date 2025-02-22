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

def displaysplit(output_text_step7, entry_splitedmics_dir, entry_splitcoordinate_dir, entry_todisplay_step7, selected_order_step7, filter_forsplit_checkbox, entry_config):
    global splitedmics_dir
    splitedmics_dir = entry_splitedmics_dir.get()
    splitcoordinate_dir = entry_splitcoordinate_dir.get()
    order = selected_order_step7.get()
    filterflag = filter_forsplit_checkbox.get()

    with open(entry_config.get(), 'r') as config_file:
        config = json.load(config_file)

    cryolo_python = config.get("cryolo_python")
    cryolo_gui = config.get("cryolo_gui")
    cryolo_boxmanager = config.get("cryolo_boxmanager")

    output_text_step7.delete(1.0, tk.END)  # Clear previous output
    output_text_step7.insert(tk.END, "BoxManager started...\n")
    output_text_step7.see(tk.END)

    def run_boxmanager():

        miclist = glob.glob(os.path.join(splitedmics_dir, '*.mrc'))
        miclist = [os.path.basename(file) for file in miclist]

        picklist = glob.glob(os.path.join(splitcoordinate_dir, '*_resam_Zscore_helix_split.star'))
        picklist = sorted(picklist, key=lambda x: os.path.getmtime(x))
        picklist = [os.path.basename(file) for file in picklist]

        miclist = [item.split("_resam_Zscore_helix_split.star")[0]+".mrc" for item in picklist if item.split("_resam_Zscore_helix_split.star")[0]+".mrc" in miclist]

        #####################

        if order == "Last":
            miclist.reverse()
        elif order == "Random":
            random.shuffle(miclist)

        if len(miclist) == 0:
            output_text_step7.insert(tk.END, f"Error: There are no micrographs with split coordinates.\n")
            output_text_step7.see(tk.END)
            return

        todisplay = entry_todisplay_step7.get()

        if todisplay in ["all", "All", "ALL"]:
            todisplay = len(miclist)
        else:
            todisplay=int(todisplay)
            if todisplay > len(miclist):
                output_text_step7.insert(tk.END, f"Warning: There are only {len(miclist)} micrographs with split coordinates.\n")
                output_text_step7.see(tk.END)
                todisplay=len(miclist)

        miclist = miclist[:todisplay]

        #################

        if not os.path.exists("Subflow"):
            os.makedirs("Subflow")

        global mictemp
        i=0
        mictemp=os.path.join("Subflow","temp-mics"+str(i))
        while os.path.exists(mictemp):
            mictemp=os.path.join("Subflow","temp-mics"+str(i))
            i+=1
        os.makedirs(mictemp)

        if filterflag:

            # Use ProcessPoolExecutor to process files in parallel
            with ProcessPoolExecutor(max_workers=12) as executor:
                list(executor.map(process_file, miclist))

        else:

            for moveme in miclist:
                source_file_path = os.path.join(os.getcwd(), splitedmics_dir, moveme)
                destination_file_path = os.path.join(os.getcwd(), mictemp, moveme)
                subprocess.run(["ln", "-sf", source_file_path, destination_file_path])

        #################

        i=0
        splittemp=os.path.join(splitcoordinate_dir,"temp-split"+str(i))
        while os.path.exists(splittemp):
            splittemp=os.path.join(splitcoordinate_dir,"temp-split"+str(i))
            i+=1
        os.makedirs(splittemp)

        for filename in picklist:
            if filename.split("_resam_Zscore_helix_split.star")[0]+".mrc" in miclist:
                source_file_path = os.path.join(os.getcwd(), splitcoordinate_dir, filename)
                filename_nosuffix = filename.split("_resam_Zscore_helix_split.star")[0]+".star"
                destination_file_path = os.path.join(os.getcwd(), splittemp, filename_nosuffix)
                subprocess.run(["ln", "-sf", source_file_path, destination_file_path])

        try:
            cmd = [
                cryolo_python,
                cryolo_boxmanager,
                '-i', mictemp,
                '-b', splittemp
            ]

            # Run the BoxManager subprocess and capture both stdout and stderr
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read and display the output in real-time
            for line in process.stdout:
                output_text_step7.insert(tk.END, line)
                output_text_step7.see(tk.END)

            # Wait for the subprocess to complete
            process.wait()

            ##########
            shutil.rmtree(mictemp)
            shutil.rmtree(splittemp)
            ###########

            # Display a completion message
            output_text_step7.insert(tk.END, "BoxManager completed.\n")

            output_text_step7.see(tk.END)

        except subprocess.CalledProcessError as e:
            # Display an error message if the subprocess fails
            output_text_step7.insert(tk.END, f"Error running BoxManager: {e.stderr}\n")
            output_text_step7.see(tk.END)

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
    global splitedmics_dir
    global mictemp
    source_file_path = os.path.join(os.getcwd(), splitedmics_dir, processme)
    destination_file_path = os.path.join(os.getcwd(), mictemp, processme)
    low_pass_filter_mrc(source_file_path, destination_file_path)