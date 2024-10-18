import tkinter as tk
import subprocess
import threading
import os
import time
import glob
import sys
import shutil
from subflow import updategui

def disable_ui_elements(entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain):
    entry_sourcemovies.config(state='disabled')
    entry_gain.config(state='disabled')
    entry_optics.config(state='disabled')
    entry_pixelsize_corr.config(state='disabled')
    entry_voltage.config(state='disabled')
    entry_dose.config(state='disabled')
    entry_eergroups_corr.config(state='disabled')
    entry_gainrot.config(state='disabled')
    entry_gainflip.config(state='disabled')
    entry_mtf.config(state='disabled')
    corr_button.config(state='disabled')
    stop_corr_button.config(state='disabled')
    browse_button_gain.config(state='disabled')
    stop_corr_button.config(state='normal')
def enable_ui_elements(entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain):
    entry_sourcemovies.config(state='normal')
    entry_gain.config(state='normal')
    entry_optics.config(state='normal')
    entry_pixelsize_corr.config(state='normal')
    entry_voltage.config(state='normal')
    entry_dose.config(state='normal')
    entry_eergroups_corr.config(state='normal')
    entry_gainrot.config(state='normal')
    entry_gainflip.config(state='normal')
    entry_mtf.config(state='normal')
    corr_button.config(state='normal')
    stop_corr_button.config(state='normal')
    browse_button_gain.config(state='normal')
    stop_corr_button.config(state='normal')

global corr_running
corr_running = False

def corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain, notebook):

    output_text_step0.delete(1.0, tk.END)  # Clear previous output

    try:
        subprocess.check_output(["which", "relion"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        output_text_step0.insert(tk.END, "Error: relion command not found. Source relion and try again.")
        output_text_step0.see(tk.END)
        corr_running=False
        return

    if os.path.exists(".relion_lock_scheme_prep"):
        output_text_step0.insert(tk.END, "Error: the .relion_lock_scheme_prep directory is blocking the run. Make sure the schemer is not running and then manually remove it")
        output_text_step0.see(tk.END)
        corr_running=False
        return

    disable_ui_elements(entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)

    def corr_thread():
        global corr_running
        global schemer_process

        subprocess_completed = threading.Event()

        corr_running=True
        updategui.set_update_flag("preprocess", True)
        updategui.change_tabtitle(notebook, "preprocess")

        sourcemovies = entry_sourcemovies.get()
        gain = entry_gain.get()
        optics = entry_optics.get()
        pixelsize_corr = entry_pixelsize_corr.get()
        voltage = entry_voltage.get()
        dose = entry_dose.get()
        eergroups_corr = entry_eergroups_corr.get()
        gainrot = entry_gainrot.get()
        gainflip = entry_gainflip.get()
        mtf = entry_mtf.get()

        importjob = "Import/job001/"
        corrjob = "MotionCorr/job002/"
        ctfjob = "CtfFind/job003/"
        importout = f"{importjob}run.out"
        importerr = f"{importjob}run.err"
        corrout = f"{corrjob}run.out"
        correrr = f"{corrjob}run.err"
        ctfout = f"{ctfjob}run.out"
        ctferr = f"{ctfjob}run.err"

        if os.path.exists(importout):
            importoutsize = os.path.getsize(importout)
        else:
            importoutsize = 0
        if os.path.exists(importerr):
            importerrsize = os.path.getsize(importerr)
        else:
            importerrsize = 0
        if os.path.exists(corrout):
            corroutsize = os.path.getsize(corrout)
        else:
            corroutsize = 0
        if os.path.exists(correrr):
            correrrsize = os.path.getsize(correrr)
        else:
            correrrsize = 0
        if os.path.exists(ctfout):
            ctfoutsize = os.path.getsize(ctfout)
        else:
            ctfoutsize = 0
        if os.path.exists(ctferr):
            ctferrsize = os.path.getsize(ctferr)
        else:
            ctferrsize = 0

        if gainrot == "":
            gainrot = "\"No rotation (0)\""
        elif gainrot == "90":
            gainrot = "\"90 degrees (1)\""
        elif gainrot == "180":
            gainrot = "\"180 degrees (2)\""
        elif gainrot == "270":
            gainrot = "\"270 degrees (3)\""
        else:
            output_text_step0.insert(tk.END, "Error: The gain rotation needs to be 90, 180, or 270 (or none).\n")
            output_text_step0.see(tk.END)
            corr_running=False
            stop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
            updategui.set_update_flag("preprocess", False)
            return

        if gainflip == "":
            gainflip = "\"No flipping (0)\""
        elif gainflip == "up-down":
            gainflip = "\"Flip upside down (1)\""
        elif gainflip == "left-right":
            gainflip = "\"Flip left to right (2)\""
        else:
            output_text_step0.insert(tk.END, "Error: The gain flip needs to be up-down, or left-right (or none).\n")
            output_text_step0.see(tk.END)
            corr_running=False
            stop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
            updategui.set_update_flag("preprocess", False)
            return

        if not os.path.exists(gain) and gain != "":
            output_text_step0.insert(tk.END, f"The gain reference {gain} does not exist.\n")
            output_text_step0.see(tk.END)
            corr_running=False
            stop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
            updategui.set_update_flag("preprocess", False)
            return

        if eergroups_corr == "":
            eergroups_corr = "32"

        schemesdir = os.path.join(os.getcwd(), "Schemes")

        output_text_step0.insert(tk.END, "\nPreprocessing running...\n\n")
        output_text_step0.see(tk.END)
            
        try:

            if not os.path.exists(schemesdir):
                shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Schemes"), schemesdir)
            else:
                subprocess.run(["rm", "-f", os.path.join(schemesdir, "RELION_JOB_ABORT_NOW")])
                subprocess.run(["rm", "-f", os.path.join(importjob, "RELION_JOB_ABORT_NOW")])
                subprocess.run(["rm", "-f", os.path.join(corrjob, "RELION_JOB_ABORT_NOW")])
                subprocess.run(["rm", "-f", os.path.join(ctfjob, "RELION_JOB_ABORT_NOW")])

            #Edit import values

            importscheme = os.path.join(schemesdir, "prep", "importmovies", "job.star")
            with open(importscheme, 'r') as file:
                lines = file.readlines()

            with open(importscheme, 'w') as file:
                for line in lines:
                    if "angpix" in line:
                        file.write(f"  angpix        {pixelsize_corr}\n")
                    elif "fn_in_raw" in line:
                        file.write(f"  fn_in_raw        {sourcemovies}\n")
                    elif "kV" in line:
                        file.write(f"  kV        {voltage}\n")
                    elif "optics_group_name" in line:
                        file.write(f"  optics_group_name        {optics}\n")
                    elif "fn_in_raw" in line:
                        file.write(f"  fn_in_raw        {sourcemovies}\n")
                    elif "fn_mtf" in line:
                        file.write(f"  fn_mtf        {mtf}\n")
                    else:
                        file.write(line)

            #Edit motioncorr values

            corrscheme = os.path.join(schemesdir, "prep", "motioncorr", "job.star")
            with open(corrscheme, 'r') as file:
                lines = file.readlines()

            with open(corrscheme, 'w') as file:
                for line in lines:
                    if "dose_per_frame" in line:
                        file.write(f"  dose_per_frame        {dose}\n")
                    elif "eer_grouping" in line:
                        file.write(f"  eer_grouping        {eergroups_corr}\n")
                    elif "fn_gain_ref" in line:
                        file.write(f"  fn_gain_ref        {gain}\n")
                    elif "gain_flip" in line:
                        file.write(f"  gain_flip        {gainflip}\n")
                    elif "gain_rot" in line:
                        file.write(f"  gain_rot        {gainrot}\n")
                    else:
                        file.write(line)

            ####

            cmd = ["relion_schemer",
                "--scheme", "prep",
                "--run",
                "--pipeline_control", "Schemes/"
                ]

            subprocess.run(["touch", ".gui_projectdir"])

            # slurmid = None

            schemer_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        except Exception as e:
            output_text_step0.insert(tk.END, f"Error running Relion scheme: {str(e)}\n")
            output_text_step0.see(tk.END)
            corr_running=False
            enable_ui_elements(entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
            updategui.set_update_flag("preprocess", False)
            return

        stdout_thread = threading.Thread(
            target=read_stream, args=(schemer_process.stdout, output_text_step0, subprocess_completed)
        )
        stderr_thread = threading.Thread(
            target=read_stream, args=(schemer_process.stderr, output_text_step0, subprocess_completed)
        )

        stdout_thread.start()
        stderr_thread.start()

        import_monitor_thread = threading.Thread(
            target=monitor_files, args=(importout, output_text_step0b, importoutsize, subprocess_completed)
        )
        import_monitor_thread.start()

        importerr_monitor_thread = threading.Thread(
            target=monitor_files, args=(importerr, output_text_step0c, importerrsize, subprocess_completed)
        )
        importerr_monitor_thread.start()

        corr_monitor_thread = threading.Thread(
            target=monitor_files, args=(corrout, output_text_step0b, corroutsize, subprocess_completed)
        )
        corr_monitor_thread.start()

        correrr_monitor_thread = threading.Thread(
            target=monitor_files, args=(correrr, output_text_step0c, correrrsize, subprocess_completed)
        )
        correrr_monitor_thread.start()

        ctf_monitor_thread = threading.Thread(
            target=monitor_files, args=(ctfout, output_text_step0b, ctfoutsize, subprocess_completed)
        )
        ctf_monitor_thread.start()

        ctferr_monitor_thread = threading.Thread(
            target=monitor_files, args=(ctferr, output_text_step0c, ctferrsize, subprocess_completed)
        )
        ctferr_monitor_thread.start()

        schemer_process.wait()

        subprocess_completed.set()

        stdout_thread.join()
        stderr_thread.join()
        # import_monitor_thread.join()
        # importerr_monitor_thread.join()
        # corr_monitor_thread.join()
        # correrr_monitor_thread.join()
        # ctf_monitor_thread.join()
        # ctferr_monitor_thread.join()

        corr_running=False
        enable_ui_elements(entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
        updategui.set_update_flag("preprocess", False)

        output_text_step0.insert(tk.END, "\nPreprocessing stopped.\n")
        output_text_step0.see(tk.END)

    corr_thread_instance = threading.Thread(target=corr_thread, name="subflow-corr")
    corr_thread_instance.daemon = True
    corr_thread_instance.start()

def read_stream(stream, text_widget, subprocess_completed):
    while not subprocess_completed.is_set():
        line = stream.readline()
        if not line:
            break
        text_widget.insert(tk.END, line)
        text_widget.see(tk.END)

def monitor_files(file_path, text_widget, starting_point, subprocess_completed):

    while not subprocess_completed.is_set():

        while not os.path.exists(file_path):
            time.sleep(1)

        file_size = os.path.getsize(file_path)
        if starting_point > file_size:
            starting_point = file_size

        with open(file_path, 'r') as file_pointer:
            file_pointer.seek(starting_point)
            lines = file_pointer.readlines()

        for line in lines:
            text_widget.insert(tk.END, line)
            text_widget.see(tk.END)

        starting_point = file_size

        time.sleep(1)

def stop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain):
    global corr_running

    importjob = "Import/job001/"
    corrjob = "MotionCorr/job002/"
    ctfjob = "CtfFind/job003/"

    if corr_running:

        stop_corr_button.config(state='disabled')
        subprocess.run(["touch", os.path.join("Schemes", "RELION_JOB_ABORT_NOW")])
        if not os.path.exists(importjob):
            os.makedirs(importjob)
        if not os.path.exists(corrjob):
            os.makedirs(corrjob)
        if not os.path.exists(ctfjob):
            os.makedirs(ctfjob)
        subprocess.run(["touch", os.path.join(importjob, "RELION_JOB_ABORT_NOW")])
        subprocess.run(["touch", os.path.join(corrjob, "RELION_JOB_ABORT_NOW")])
        subprocess.run(["touch", os.path.join(ctfjob, "RELION_JOB_ABORT_NOW")])

        output_text_step0.insert(tk.END, "\n\nPreprocessing stopping. It may take a minute...\n\n")
        output_text_step0.see(tk.END)

    else:
        enable_ui_elements(entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
        updategui.set_update_flag("preprocess", False)
        output_text_step0.see(tk.END)


def forcestop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain):
    output_text_step0.insert(tk.END, "\n\nEnabled UI.\nMake sure preprocessing is actually stopped before proceeding.\nIf you forced it because it crashed, make sure you fix the issue before rerunning.\n\n")
    output_text_step0.see(tk.END)
    enable_ui_elements(entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
    updategui.set_update_flag("preprocess", False)
