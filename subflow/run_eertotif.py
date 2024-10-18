import tkinter as tk
import subprocess
import threading
import os
import time
import glob
from subflow import updategui

def disable_ui_elements(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button):
    entry_eer_dir.config(state='disabled')
    entry_eergroups.config(state='disabled')
    entry_tif_dir.config(state='disabled')
    browse_tif_dir.config(state='disabled')
    checkboxm1.config(state='disabled')
    entry_gainm1.config(state='disabled')
    browse_button_gainm1.config(state='disabled')
    entry_eerprocs.config(state='disabled')
    eertif_button.config(state='disabled')
    stop_eertif_button.config(state='normal')
def enable_ui_elements(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button):
    entry_eer_dir.config(state='normal')
    entry_eergroups.config(state='normal')
    entry_tif_dir.config(state='normal')
    browse_tif_dir.config(state='normal')
    checkboxm1.config(state='normal')
    entry_gainm1.config(state='normal')
    browse_button_gainm1.config(state='normal')
    entry_eerprocs.config(state='normal')
    eertif_button.config(state='normal')
    stop_eertif_button.config(state='normal')


convert_running = False
import_running = False
run_running = False

def eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button, notebook):

    global run_running
    global import_running
    global importprocess
    global convert_running
    global convertprocess

    try:
        subprocess.check_output(["which", "relion"], stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        output_text_stepm1.insert(tk.END, "Error: relion command not found. Source relion and try again.\n")
        output_text_stepm1.see(tk.END)
        convert_running=False
        import_running=False
        run_running=False
        return

    if convertgain_checkbox.get() == 1 and not os.path.exists(entry_gainm1.get()):
        output_text_stepm1.insert(tk.END, f"Error: gain file {entry_gainm1.get()} does not exist.\n")
        output_text_stepm1.see(tk.END)
        convert_running=False
        import_running=False
        run_running=False
        return

    def convert_thread():
        global run_running
        global import_running
        global importprocess
        global convert_running
        global convertprocess

        eerdir = entry_eer_dir.get()
        groups = entry_eergroups.get()
        tifdir = entry_tif_dir.get()
        convertgainflag = convertgain_checkbox.get()
        gainfile = entry_gainm1.get()
        procs = entry_eerprocs.get()
        
        output_text_stepm1.delete(1.0, tk.END)  # Clear previous output

        output_text_stepm1.insert(tk.END, "Converting EER to tif...\n")

        run_running = True
        updategui.set_update_flag("eertotif", True)
        updategui.change_tabtitle(notebook, "eertotif")
        disable_ui_elements(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button)

        if not os.path.exists("Subflow/ImportEER"):
            os.makedirs("Subflow/ImportEER")
        if not os.path.exists(eerdir):
            output_text_stepm1.insert(tk.END, "Waiting for EER file...\n")

        while run_running:
            
            output_text_stepm1.see(tk.END)

            eerlist = glob.glob(eerdir)
            eerlist = [os.path.basename(file) for file in eerlist]
            
            tiflist = []
            if os.path.exists(tifdir):
                for root_dir, _, files in os.walk(tifdir):
                    for filename in files:
                        if filename.endswith("tif"):
                            tiflist.append(os.path.basename(filename))

            leftlist = [item for item in eerlist if item.split(".eer")[0]+".tif" not in tiflist]

            if len(leftlist) > 0:

                #IMPORT

                import_running=True

                try:

                    output_text_stepm1.insert(tk.END, "Importing movies...\n")
                    output_text_stepm1.see(tk.END)

                    importprocess=subprocess.run([
                        "relion_import",
                        "--do_movies",
                        "--i", eerdir,
                        "--odir", "Subflow/ImportEER/",
                        "--ofile", "eer.star",
                        "--continue"
                        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    stdout_output = importprocess.stdout
                    stderr_output = importprocess.stderr

                    if importprocess.returncode == 0:
                        output_text_stepm1.insert(tk.END, stdout_output)
                        output_text_stepm1.insert(tk.END, stderr_output)
                    else:
                        # Insert both stdout and stderr into the widget
                        output_text_stepm1.insert(tk.END, "Error importing EER files:\n")
                        output_text_stepm1.insert(tk.END, stdout_output)
                        output_text_stepm1.insert(tk.END, stderr_output)
                        stop_eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button)

                except Exception as e:
                    output_text_stepm1.insert(tk.END, f"Error importing EER files: {str(e)}\n")
                    stop_eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button)

                import_running=False

                #CONVERT

                convert_running = True

                convertcmd = [
                            "mpirun", "-n", procs,
                            "relion_convert_to_tiff_mpi",
                            "--i", "Subflow/ImportEER/eer.star",
                            "--o", tifdir,
                            "--eer_grouping", groups,
                            "--only_do_unfinished"
                            ]
                if convertgainflag == 1:
                    convertcmd.append("--gain")
                    convertcmd.append(gainfile)

                try:
                    convertprocess=subprocess.Popen(convertcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    stdout_thread = threading.Thread(
                        target=read_stream, args=(convertprocess.stdout, output_text_stepm1)
                    )
                    stderr_thread = threading.Thread(
                        target=read_stream, args=(convertprocess.stderr, output_text_stepm1)
                    )

                    stdout_thread.start()
                    stderr_thread.start()

                    convertprocess.wait()

                except Exception as e:
                    output_text_stepm1.insert(tk.END, f"Error running relion_convert_to_tiff: {str(e)}\n")
                    stop_eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button)

                output_text_stepm1.see(tk.END)

                convert_running = False

            time.sleep(4)

    # Create and start the sync thread
    convert_thread_instance = threading.Thread(target=convert_thread, name="subflow-eertif")
    convert_thread_instance.daemon = True
    convert_thread_instance.start()

def stop_eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button):
    global run_running
    global import_running
    global importprocess
    global convert_running
    global convertprocess

    try:
        if importprocess and import_running:
            importprocess.terminate()
        elif convertprocess and convert_running:
            convertprocess.terminate()
    except:
        pass

    import_running = False
    convert_running = False
    run_running = False
    updategui.set_update_flag("eertotif", False)

    output_text_stepm1.insert(tk.END, "\nEER conversion stopped.\n")
    output_text_stepm1.see(tk.END)
    enable_ui_elements(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button)

def read_stream(stream, text_widget):
    while True:
        line = stream.readline()
        if not line:
            break
        text_widget.insert(tk.END, line)
        text_widget.see(tk.END)