import tkinter as tk
import subprocess
import threading
import os
import glob
import shutil
import json

def relionimport(output_text_step11a, entry_micstar11, entry_subcoords, entry_importjob):

    try:
        subprocess.check_output(["which", "relion"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        output_text_step11a.insert(tk.END, "Error: Relion command not found. Source relion and restart Subflow.")
        output_text_step11a.see(tk.END)
        return
    if not os.path.exists("default_pipeline.star"):
        output_text_step11a.insert(tk.END, f"Error: This doesn't seem to be a Relion directory.\n")
        output_text_step11a.see(tk.END)
        return

    def import_thread():

        importsubprocess_completed = threading.Event()

        subcoords = entry_subcoords.get()

        if not glob.glob(subcoords):
            output_text_step11a.insert(tk.END, f"Error: Could not find any coordinates.\n")
            output_text_step11a.see(tk.END)
            return

        source_job_star = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Schemes", "prep", "importcoords", "job.star")
        destination_dir = os.path.join(os.getcwd(), "Schemes", "prep", "importcoords")
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        importscheme = os.path.join(destination_dir, "job.star")
        shutil.copy(source_job_star, importscheme)

        with open(importscheme, 'r') as file:
            lines = file.readlines()

        with open(importscheme, 'w') as file:
            for line in lines:
                if "fn_in_other" in line:
                    file.write(f"fn_in_other        {subcoords}\n")
                else:
                    file.write(line)

        importjobname = getnextjob()
        if importjobname=="job000":
            output_text_step11a.insert(tk.END, f"Error: Could not figure out the next Relion job number.\n")
            output_text_step11a.see(tk.END)
            return

        importpipeliner = ["relion_pipeliner",
            "--addJobFromStar", "Schemes/prep/importcoords/job.star"]

        importcmd = ["relion_pipeliner",
            "--RunJobs", f"Import/{importjobname}/"]

        importout = f"Import/{importjobname}/run.out"
        importerr = f"Import/{importjobname}/run.err"

        output_text_step11a.insert(tk.END, f"Import {importjobname} running...\n")
        output_text_step11a.see(tk.END)

        entry_importjob.delete(0, tk.END)
        entry_importjob.insert(0, importjobname)

        try:

            subprocess.run(importpipeliner)

            import_process = subprocess.Popen(importcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        except Exception as e:
            output_text_step11a.insert(tk.END, f"Error running Import: {str(e)}\n")
            output_text_step11a.see(tk.END)

        import_stdout_thread = threading.Thread(
            target=read_stream, args=(import_process.stdout, output_text_step11a, importsubprocess_completed, importout)
        )
        import_stderr_thread = threading.Thread(
            target=read_stream, args=(import_process.stderr, output_text_step11a, importsubprocess_completed, importerr)
        )

        import_stdout_thread.start()
        import_stderr_thread.start()

        import_process.wait()

        importsubprocess_completed.set()

        import_stdout_thread.join()
        import_stderr_thread.join()

    import_thread_instance = threading.Thread(target=import_thread, name="subflow-coordimport")
    import_thread_instance.daemon = True
    import_thread_instance.start()

def relionextract(output_text_step11b, entry_micstar11, entry_importjob, entry_boxsize, entry_rescaledbox, entry_config):

    try:
        subprocess.check_output(["which", "relion"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        output_text_step11b.insert(tk.END, "Error: Relion command not found. Source Relion and restart SUbflow.")
        output_text_step11b.see(tk.END)
        return
    if not os.path.exists("default_pipeline.star"):
        output_text_step11b.insert(tk.END, f"Error: This doesn't seem to be a Relion directory.\n")
        output_text_step11b.see(tk.END)
        return

    def extract_thread():

        extractsubprocess_completed = threading.Event()

        importjob = entry_importjob.get()
        micstar = entry_micstar11.get()
        boxsize = entry_boxsize.get()
        rescaledbox = entry_rescaledbox.get()

        if not os.path.exists(micstar):
            output_text_step11b.insert(tk.END, f"Error: {micstar} doesn't exist.\n")
            output_text_step11b.see(tk.END)
            return
        elif not os.path.exists(f"Import/{importjob}/coords_suffix.star"):
            output_text_step11b.insert(tk.END, f"Error: Import/{importjob}/coords_suffix.star doesn't exist.\n")
            output_text_step11b.see(tk.END)
            return

        source_job_star = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Schemes", "proc", "extract", "job.star")
        destination_dir = os.path.join(os.getcwd(), "Schemes", "proc", "extract")
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        extractscheme = os.path.join(destination_dir, "job.star")
        shutil.copy(source_job_star, extractscheme)

        with open(entry_config.get(), 'r') as config_file:
            config = json.load(config_file)
        customjobstar = config.get("relion_extract_job")
        
        if customjobstar != "" and not os.path.exists(customjobstar):
            output_text_step0.insert(tk.END, f"The job.star file does not exist: {customjobstar}\n")
            output_text_step0.see(tk.END)
            corr_running=False
            stop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
            updategui.set_update_flag("preprocess", False)
            return
        elif customjobstar != "":
            shutil.copy(customjobstar, extractscheme)

        with open(extractscheme, 'r') as file:
            lines = file.readlines()

        with open(extractscheme, 'w') as file:
            for line in lines:
                if "coords_suffix" in line:
                    file.write(f"coords_suffix  Import/{importjob}/coords_suffix.star\n")
                elif "extract_size" in line:
                    file.write(f"extract_size  {boxsize}\n")
                elif "rescale" in line and "do_rescale" not in line:
                    file.write(f"rescale  {rescaledbox}\n")
                elif "do_rescale" in line and int(rescaledbox) != int(boxsize):
                    file.write(f"do_rescale    Yes\n")
                elif "star_mics" in line:
                    file.write(f"star_mics  {micstar}\n")
                else:
                    file.write(line)

        extractjobname = getnextjob()
        if extractjobname=="job000":
            output_text_step11b.insert(tk.END, f"Could not figure out the next Relion job number.\n")
            output_text_step11b.see(tk.END)
            return

        extractpipeliner = ["relion_pipeliner", 
            "--addJobFromStar", "Schemes/proc/extract/job.star"]

        extractcmd = ["relion_pipeliner",
            "--RunJobs", f"Extract/{extractjobname}/"]

        extractout = f"Extract/{extractjobname}/run.out"
        extracterr = f"Extract/{extractjobname}/run.err"

        output_text_step11b.insert(tk.END, f"Extract {extractjobname} running...\n")
        output_text_step11b.see(tk.END)

        try:

            subprocess.run(extractpipeliner)

            extract_process = subprocess.Popen(extractcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        except Exception as e:
            output_text_step11b.insert(tk.END, f"Error running Extract: {str(e)}\n")
            output_text_step11b.see(tk.END)

        extract_stdout_thread = threading.Thread(
            target=read_stream, args=(extract_process.stdout, output_text_step11b, extractsubprocess_completed, extractout)
        )
        extract_stderr_thread = threading.Thread(
            target=read_stream, args=(extract_process.stderr, output_text_step11b, extractsubprocess_completed, extracterr)
        )

        extract_stdout_thread.start()
        extract_stderr_thread.start()

        extract_process.wait()

        extractsubprocess_completed.set()

        extract_stdout_thread.join()
        extract_stderr_thread.join()

    extract_thread_instance = threading.Thread(target=extract_thread, name="subflow-coordextract")
    extract_thread_instance.daemon = True
    extract_thread_instance.start()

def getnextjob():

    nextrelionjob="job000"
    with open("default_pipeline.star", 'r') as file:
        for line in file:
            if '_rlnPipeLineJobCounter' in line:
                nextrelionjobnum = int(line.split()[-1])
                nextrelionjob = f"job{nextrelionjobnum:03d}"
                break
    return nextrelionjob

def read_stream(stream, text_widget, subprocess_completed, outfile):
    while not subprocess_completed.is_set():
        line = stream.readline()
        if not line:
            break
        text_widget.insert(tk.END, line)
        text_widget.see(tk.END)
        with open(outfile, 'a') as file:
            file.write(line)
