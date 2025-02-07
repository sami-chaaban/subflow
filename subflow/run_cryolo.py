import tkinter as tk
import subprocess
import threading
import os
import time
import glob
import random
import shutil
import json
from subflow import updategui

class CryoloPickOperation:

    def __init__(self):

        self.cryolo_pick_process = None
        self.cryolo_config_process = None
        self.pick_running = False

    def pick(self, output_text, defaultbox, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset, resetpicks_button, notebook, entry_config, jobalias):

        with open(entry_config.get(), 'r') as config_file:
            self.config = json.load(config_file)

        cryolo_python = self.config.get("cryolo_python")
        cryolo_gui = self.config.get("cryolo_gui")

        if not os.path.exists(cryolo_python):
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"Error: Cryolo does not exist: {cryolo_python}\n")
            output_text.see(tk.END)
            return

        cryolo_model = entry_cryolo_model.get()
        pixel_size = entry_pixel_size.get()
        boxsize = str(int(defaultbox/float(pixel_size)))
        threshold = entry_threshold.get()
        projectname = entry_projectname.get()
        pickname = entry_pickname.get()
        gpu = entry_gpu.get()
        subset = entry_picksubset.get()
        micrographs_dir = entry_micrographs_topick.get()

        if not os.path.exists(micrographs_dir):
            output_text.insert(tk.END, f"Error: {micrographs_dir} directory does not exist.\n")
            output_text.see(tk.END)
            return

        miclist = glob.glob(os.path.join(micrographs_dir, '*.mrc'))
        if subset != "" and len(miclist) < int(subset):
            output_text.insert(tk.END, f"Error: There are only {len(miclist)} micrographs, but you asked to pick a subset of {subset}.\n")
            output_text.see(tk.END)
            return

        disable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset)
        updategui.set_update_flag(jobalias, True)
        updategui.change_tabtitle(notebook, jobalias)
        self.pick_running = True

        output_text.delete(1.0, tk.END)

        finalpickdir = os.path.join("Cryolo",projectname,pickname)
        if not os.path.isdir(finalpickdir):
            os.makedirs(finalpickdir)
            output_text.insert(tk.END, f"Created {finalpickdir}\n")
            output_text.see(tk.END)

        def run_cryolo():

            notpickedfile = os.path.join("Cryolo", projectname, pickname, "nopicklist.txt")

            try:

                if not os.path.exists(os.path.join("Cryolo", projectname, pickname, "config_cryolo.json")):

                    output_text.insert(tk.END, "Creating config file...\n")
                    output_text.see(tk.END)

                    cmd_config = [
                        cryolo_python, '-u',
                        cryolo_gui,
                        '--ignore-gooey', 'config',
                        '--saved_weights_name', 'cryolo_model.h5',
                        '-a', 'PhosaurusNet',
                        '--input_size', '1024',
                        '-nm', 'STANDARD',
                        '--num_patches', '1',
                        '--overlap_patches', '200',
                        '--filtered_output', 'Cryolo/'+projectname+'/filtered_tmp/',
                        '-f', 'LOWPASS',
                        '--low_pass_cutoff', '0.1',
                        '--janni_overlap', '24',
                        '--janni_batches', '3',
                        '--train_times', '10',
                        '--batch_size', '4',
                        '--learning_rate', '0.0001',
                        '--nb_epoch', '200',
                        '--object_scale', '5.0',
                        '--no_object_scale', '1.0',
                        '--coord_scale', '1.0',
                        '--class_scale', '1.0',
                        '--debug',
                        '--log_path', 'Cryolo/'+projectname+'/logs/',
                        '--', os.path.join("Cryolo", projectname, pickname, "config_cryolo.json"), boxsize
                    ]

                    # Run the Cryolo subprocess and capture both stdout and stderr    
                    self.cryolo_config_process = subprocess.Popen(cmd_config, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    # Read and display the output in real-time
                    for line in self.cryolo_config_process.stdout:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)

                if not self.pick_running:
                    updategui.set_update_flag(jobalias, False)
                    output_text.insert(tk.END, "Picking stopped.\n")
                    output_text.see(tk.END)
                    enable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset)

                ###############################

                micrographs_dir = entry_micrographs_topick.get()

                while self.pick_running:

                    miclist = []
                    announced = False

                    while len(miclist) == 0:

                        miclist = glob.glob(os.path.join(micrographs_dir, '*.mrc'))
                        miclist = [os.path.basename(file) for file in miclist]
                        picklist = glob.glob(os.path.join("Cryolo", projectname, pickname, "STAR", '*.star'))
                        picklist = [os.path.basename(file) for file in picklist]

                        miclist = [item for item in miclist if item.split(".mrc")[0]+".star" not in picklist]

                        if os.path.exists(notpickedfile):
                            prev_notpickedlist = []
                            with open(notpickedfile, "r") as file:
                                for line in file:
                                    prev_notpickedlist.append(line.strip())
                            miclist = [item for item in miclist if item not in prev_notpickedlist]      

                        current_time = time.time()
                        miclist = [
                            item for item in miclist
                            if (current_time - os.path.getmtime(os.path.join(micrographs_dir, item))) > 60
                        ]

                        # lockedfiles = []
                        # for filename in os.listdir('Subflow'):
                        #     if filename.startswith('lock') and filename.endswith('.txt'):
                        #         with open(os.path.join('Subflow', filename), 'r') as file:
                        #             first_line = file.readline().strip()
                        #             if first_line:
                        #                 lockedfiles.append(first_line)
                        # miclist = [item for item in miclist if item not in lockedfiles] 
              

                        if len(miclist) == 0 and not announced:
                            output_text.insert(tk.END, "\nLooking for new micrograph...\n")
                            output_text.see(tk.END)
                            announced = True

                        if not self.pick_running:
                            updategui.set_update_flag(jobalias, False)
                            output_text.insert(tk.END, "Picking stopped.\n")
                            output_text.see(tk.END)
                            enable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset)
                            return

                        time.sleep(4)


                    if subset != "":
                        random.shuffle(miclist)
                        miclist = miclist[0:int(subset)]
                    else:
                        output_text.insert(tk.END, f"\nFound {len(miclist)} new micrographs...\n")
                        output_text.see(tk.END)

                    ##########
                    if not os.path.exists("Subflow"):
                        os.makedirs("Subflow")

                    i=0
                    cryolotemp=os.path.join("Subflow",f"temp-cryolo-{jobalias}-{i}")
                    while os.path.exists(cryolotemp):
                        i+=1
                        cryolotemp=os.path.join("Subflow",f"temp-cryolo-{jobalias}-{i}")
                    os.makedirs(cryolotemp)
                    ###########

                    for moveme in miclist:

                        if not self.pick_running:
                            if os.path.exists(cryolotemp):
                                shutil.rmtree(cryolotemp)
                            updategui.set_update_flag(jobalias, False)
                            output_text.insert(tk.END, "Picking stopped.\n")
                            output_text.see(tk.END)
                            enable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset)
                            return

                        source_file_path = os.path.join(os.getcwd(), micrographs_dir, moveme)
                        destination_file_path = os.path.join(os.getcwd(), cryolotemp, moveme)
                        subprocess.run(["ln", "-sf", source_file_path, destination_file_path])

                    output_text.insert(tk.END, "\nPicking...\n")
                    output_text.see(tk.END)

                    cmd_pick = [
                        cryolo_python,
                        cryolo_gui,
                        '--ignore-gooey', 'predict',
                        '-c', os.path.join("Cryolo", projectname, pickname, "config_cryolo.json"),
                        '-w', cryolo_model,
                        '-i', cryolotemp,
                        '-o', os.path.join("Cryolo", projectname, pickname),
                        '-t', threshold,
                        '-g', gpu,
                        '-d', '0',
                        '-pbs', '3',
                        '--gpu_fraction', '1.0',
                        '-nc', '-1',
                        '--norm_margin', '0.0',
                        '--cleanup',
                        '--skip',
                        '-sm', 'LINE_STRAIGHTNESS',
                        '-st', '0.95',
                        '-sr', '1.41',
                        '-ad', '10',
                        '--directional_method', 'PREDICTED',
                        '-mw', '100',
                        '-tsr', '-1',
                        '-tmem', '0',
                        '-mn3d', '2',
                        '-tmin', '5',
                        '-twin', '-1',
                        '-tedge', '0.4',
                        '-tmerge', '0.8'
                    ]

                    # Run the Cryolo subprocess and capture both stdout and stderr
                    self.cryolo_pick_process = subprocess.Popen(cmd_pick, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    # Read and display the output in real-time
                    for line in self.cryolo_pick_process.stdout:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)

                    # Read and display the output in real-time
                    if self.cryolo_pick_process is not None:
                        for line in self.cryolo_pick_process.stderr:
                             output_text.insert(tk.END, line)
                             output_text.see(tk.END)

                    shutil.rmtree(cryolotemp)

                    ######
                    newpicklist = glob.glob(os.path.join("Cryolo", projectname, pickname, "STAR", '*.star'))
                    newpicklist = [os.path.basename(file) for file in newpicklist]
                    notpickedlist = [item for item in miclist if item.split(".mrc")[0]+".star" not in newpicklist]

                    if len(notpickedlist) > 0:

                        with open(notpickedfile, "a") as file:
                            for m in notpickedlist:
                                file.write(m+"\n")

                        if os.path.exists(notpickedfile):
                            with open(notpickedfile, 'r') as file:
                                line_count = sum(1 for line in file)

                        output_text.insert(tk.END, f"\n{len(notpickedlist)} micrographs failed to pick ({line_count} total; see {notpickedfile}).\n")
                        output_text.see(tk.END)
                        resetpicks_button.config(text=f"Reset {line_count} unpicked", state='normal')
                        resetpicks_button.grid(row=9, column=1, padx=10, pady=5, sticky="e")
                    ######

                    if not self.pick_running or subset != "":
                        updategui.set_update_flag(jobalias, False)
                        output_text.insert(tk.END, "Picking stopped.\n")
                        output_text.see(tk.END)
                        enable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset)
                        return

                    time.sleep(1)

            except subprocess.CalledProcessError as e:
                # Display an error message if the subprocess fails
                output_text.insert(tk.END, f"Error running Cryolo: {e.stderr}\n")
                updategui.set_update_flag(jobalias, False)
                output_text.see(tk.END)
                enable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset)

        # Create a thread to run the Cryolo subprocess
        cryolo_thread = threading.Thread(target=run_cryolo, name=f"subflow-{jobalias}")
        cryolo_thread.daemon = True
        cryolo_thread.start()

    def stop_pick(self, output_text):

        output_text.insert(tk.END, "Stopping...\n")
        output_text.see(tk.END)

        self.pick_running = False

        if self.cryolo_pick_process is not None:
            self.cryolo_pick_process.terminate()
        if self.cryolo_config_process is not None:
            self.cryolo_config_process.terminate()

def disable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset):
    entry_micrographs_topick.config(state='disabled')
    entry_cryolo_model.config(state='disabled')
    entry_pixel_size.config(state='disabled')
    entry_threshold.config(state='disabled')
    entry_projectname.config(state='disabled')
    entry_pickname.config(state='disabled')
    entry_gpu.config(state='disabled')
    pick_button.config(state='disabled')
    browse_button_micrographs_topick.config(state='disabled')
    browse_button_cryolo_model.config(state='disabled')
    entry_picksubset.config(state='disabled')
    stop_pick_button.config(state='normal')
def enable_ui_elements(output_text, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset):
    entry_micrographs_topick.config(state='normal')
    entry_cryolo_model.config(state='normal')
    entry_pixel_size.config(state='normal')
    entry_threshold.config(state='normal')
    entry_projectname.config(state='normal')
    entry_pickname.config(state='normal')
    entry_gpu.config(state='normal')
    browse_button_micrographs_topick.config(state='normal')
    browse_button_cryolo_model.config(state='normal')
    entry_picksubset.config(state='normal')
    pick_button.config(state='normal')
    stop_pick_button.config(state='normal')

def reset_picks(resetpicks_button, pickpath):

    notpickedfile = os.path.join(pickpath, "nopicklist.txt")
    if os.path.exists(notpickedfile):
        os.remove(notpickedfile)
    resetpicks_button.config(text="Reset", state='disabled')
    resetpicks_button.grid_remove()

