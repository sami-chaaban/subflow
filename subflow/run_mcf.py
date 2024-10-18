import tkinter as tk
import subprocess
import threading
import os
import time
from subflow import updategui
import json

class MCFOperation:
    
    def __init__(self):

        self.mcf_running = False
        self.mcf_thread_instance = None

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as config_file:
            self.config = json.load(config_file)

    def mcf(self, output_text, entry_coordinate_dir, entry_suffix, entry_pixel_size, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics, notebook, jobalias):
        mcf_script = self.config.get("mcf_script")

        if not os.path.exists(mcf_script):
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, f"Error: Subtraction script does not exist: {mcf_script}\n")
            output_text.see(tk.END)
            return

        def mcf_thread():

            coordinate_dir=entry_coordinate_dir.get()
            suffix=entry_suffix.get()
            pixel_size=entry_pixel_size.get()
            samplestep=str(int(entry_samplestep.get()))
            anglechange=str(int(entry_anglechange.get()))
            minseed=str(int(entry_minseed.get()))
            polynomial=str(int(entry_polynomial.get()))
            
            output_text.delete(1.0, tk.END)

            self.mcf_running = True
            updategui.set_update_flag(jobalias, True)
            updategui.change_tabtitle(notebook, jobalias)
            disable_ui_elements(output_text, entry_coordinate_dir, entry_suffix, entry_pixel_size, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics)


            mcf_final_dir = f"MCF-{samplestep}-{anglechange}-{minseed}-{polynomial}"
            if not os.path.exists(os.path.join(coordinate_dir, mcf_final_dir)):
                os.makedirs(os.path.join(coordinate_dir, mcf_final_dir))

            output_text.insert(tk.END, "Multi curve fitting...\n")
            output_text.insert(tk.END, "\nLooking for new coordinate file...\n")

            while not os.path.exists(coordinate_dir):
                time.sleep(4)

            while self.mcf_running:
                
                output_text.see(tk.END)

                for coordinatefile in os.listdir(coordinate_dir):
                    if not self.mcf_running:
                        output_text.insert(tk.END, "Multi curve fitting stopped.\n")
                        output_text.see(tk.END)
                        updategui.set_update_flag(jobalias, False)
                        return

                    if coordinatefile.endswith(suffix + ".star"):

                        outputfilename = coordinatefile.split(".star")[0]+"_resam_Zscore.star"

                        if not os.path.isfile(os.path.join(coordinate_dir, mcf_final_dir, outputfilename)):

                            source_file_path = os.path.join(os.getcwd(), coordinate_dir, coordinatefile)
                            destination_file_path = os.path.join(os.getcwd(), coordinate_dir, mcf_final_dir, coordinatefile)
                            subprocess.run(["ln", "-sf", source_file_path, destination_file_path])

                            try:
                                result=subprocess.run([
                                    'python',
                                    mcf_script,
                                    "--pixel_size_ang", pixel_size,
                                    "--sample_step_ang", samplestep,
                                    "--max_angle_change_per_4nm", samplestep,
                                    "--min_number_seed", minseed,
                                    "--poly_expon", polynomial,
                                    destination_file_path
                                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                                stdout_output = result.stdout
                                stderr_output = result.stderr

                                if result.returncode == 0:
                                    output_text.insert(tk.END, stdout_output)
                                    output_text.insert(tk.END, stderr_output)
                                    output_text.insert(tk.END, f"Fit: {coordinatefile}\n")
                                    output_text.insert(tk.END, "\nLooking for new coordinate file...\n")
                                else:
                                    output_text.insert(tk.END, f"Error fitting {coordinatefile}:\n")
                                    output_text.insert(tk.END, stdout_output)
                                    output_text.insert(tk.END, stderr_output)

                            except Exception as e:
                                output_text.insert(tk.END, f"Error fitting {coordinatefile}: {str(e)}\n")

                            subprocess.run(["rm", "-f", destination_file_path])
                            output_text.see(tk.END)

                # Sleep for a while before checking again
                time.sleep(4)

        # Create and start the sync thread
        self.mcf_thread_instance = threading.Thread(target=mcf_thread, name="subflow-mcf")
        self.mcf_thread_instance.daemon = True
        self.mcf_thread_instance.start()

    def stop_mcf(self, output_text, entry_coordinate_dir, entry_suffix, entry_pixel_size, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics, jobalias):
        self.mcf_running = False
        output_text.insert(tk.END, "Multi curve fitting stopping...\n")
        output_text.see(tk.END)
        enable_ui_elements(output_text, entry_coordinate_dir, entry_suffix, entry_pixel_size, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics)
        updategui.set_update_flag(jobalias, False)

def disable_ui_elements(output_text, entry_coordinate_dir, entry_suffix, entry_pixel_size, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics):
    entry_coordinate_dir.config(state='disabled')
    entry_suffix.config(state='disabled')
    entry_pixel_size.config(state='disabled')
    entry_samplestep.config(state='disabled')
    entry_anglechange.config(state='disabled')
    entry_minseed.config(state='disabled')
    entry_polynomial.config(state='disabled')
    mcf_button.config(state='disabled')
    browse_coordinate_dir.config(state='disabled')
    entry_tomcfmics_dir.config(state='disabled')
    browse_button_tomcfmics.config(state='disabled')
    stop_mcf_button.config(state='normal')
def enable_ui_elements(output_text, entry_coordinate_dir, entry_suffix, entry_pixel_size, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics):
    entry_coordinate_dir.config(state='normal')
    entry_suffix.config(state='normal')
    entry_pixel_size.config(state='normal')
    entry_samplestep.config(state='normal')
    entry_anglechange.config(state='normal')
    entry_minseed.config(state='normal')
    entry_polynomial.config(state='normal')
    mcf_button.config(state='normal')
    browse_coordinate_dir.config(state='normal')
    entry_tomcfmics_dir.config(state='normal')
    browse_button_tomcfmics.config(state='normal')
    stop_mcf_button.config(state='normal')