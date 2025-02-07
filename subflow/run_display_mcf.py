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

def displaymcf(output_text_step5, entry_mcfedmics_dir, entry_mcfcoordinate_dir, entry_todisplay_step5, selected_order_step5, filter_formcf_checkbox, entry_config):
    global mcfedmics_dir
    mcfedmics_dir = entry_mcfedmics_dir.get()
    mcfcoordinate_dir = entry_mcfcoordinate_dir.get()
    order = selected_order_step5.get()
    filterflag = filter_formcf_checkbox.get()

    with open(entry_config.get(), 'r') as config_file:
        config = json.load(config_file)

    cryolo_python = config.get("cryolo_python")
    cryolo_gui = config.get("cryolo_gui")
    cryolo_boxmanager = config.get("cryolo_boxmanager")

    output_text_step5.delete(1.0, tk.END)  # Clear previous output
    output_text_step5.insert(tk.END, "BoxManager started...\n")
    output_text_step5.see(tk.END)

    def run_boxmanager():

        miclist = glob.glob(os.path.join(mcfedmics_dir, '*.mrc'))
        miclist = [os.path.basename(file) for file in miclist]

        picklist = glob.glob(os.path.join(mcfcoordinate_dir, '*_resam_Zscore.star'))
        picklist = sorted(picklist, key=lambda x: os.path.getmtime(x))
        picklist = [os.path.basename(file) for file in picklist]

        miclist = [item.split("_resam_Zscore.star")[0]+".mrc" for item in picklist if item.split("_resam_Zscore.star")[0]+".mrc" in miclist]

        #####################

        if order == "Last":
            miclist.reverse()
        elif order == "Random":
            random.shuffle(miclist)

        if len(miclist) == 0:
            output_text_step5.insert(tk.END, f"Error: There are no micrographs with multi-curve-fit coordinates.\n")
            output_text_step5.see(tk.END)
            return

        todisplay = entry_todisplay_step5.get()

        if todisplay in ["all", "All", "ALL"]:
            todisplay = len(miclist)
        else:
            todisplay=int(todisplay)
            if todisplay > len(miclist):
                output_text_step5.insert(tk.END, f"Warning: There are only {len(miclist)} micrographs with multi-curve-fit coordinates.\n")
                output_text_step5.see(tk.END)
                todisplay=len(miclist)

        miclist = miclist[0:todisplay]

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
                source_file_path = os.path.join(os.getcwd(), mcfedmics_dir, moveme)
                destination_file_path = os.path.join(os.getcwd(), mictemp, moveme)
                subprocess.run(["ln", "-sf", source_file_path, destination_file_path])

        #################

        i=0
        mcftemp=os.path.join(mcfcoordinate_dir,"temp-mcf"+str(i))
        while os.path.exists(mcftemp):
            mcftemp=os.path.join(mcfcoordinate_dir,"temp-mcf"+str(i))
            i+=1
        os.makedirs(mcftemp)

        for filename in picklist:
            if filename.split("_resam_Zscore.star")[0]+".mrc" in miclist:
                source_file_path = os.path.join(os.getcwd(), mcfcoordinate_dir, filename)
                filename_nosuffix = filename.split("_resam_Zscore.star")[0]+".star"
                destination_file_path = os.path.join(os.getcwd(), mcftemp, filename_nosuffix)
                subprocess.run(["ln", "-sf", source_file_path, destination_file_path])

        try:
            cmd = [
                cryolo_python,
                cryolo_boxmanager,
                '-i', mictemp,
                '-b', mcftemp
            ]

            # Run the BoxManager subprocess and capture both stdout and stderr
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read and display the output in real-time
            for line in process.stdout:
                output_text_step5.insert(tk.END, line)
                output_text_step5.see(tk.END)

            # Wait for the subprocess to complete
            process.wait()

            ##########
            shutil.rmtree(mictemp)
            shutil.rmtree(mcftemp)
            ###########

            # Display a completion message
            output_text_step5.insert(tk.END, "BoxManager completed.\n")

            output_text_step5.see(tk.END)

        except subprocess.CalledProcessError as e:
            # Display an error message if the subprocess fails
            output_text_step5.insert(tk.END, f"Error running BoxManager: {e.stderr}\n")
            output_text_step5.see(tk.END)

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
    global mcfedmics_dir
    global mictemp
    source_file_path = os.path.join(os.getcwd(), mcfedmics_dir, processme)
    destination_file_path = os.path.join(os.getcwd(), mictemp, processme)
    low_pass_filter_mrc(source_file_path, destination_file_path)