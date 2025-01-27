import tkinter as tk
import subprocess
import threading
import os
import time
import sys
import shutil
import mrcfile
import numpy as np
from subflow import updategui
import concurrent.futures
import json

def scalemask(ogmaskpath, scale_factor):
    header_dtype = np.dtype(
        [('head1', '10int32'), ('head2', '6float32'), ('axisOrientations', '3int32'), ('minMaxMean', '3int32'),
         ('extra', '32int32')])
    header = np.fromfile(ogmaskpath, dtype=header_dtype, count=1)
    head1 = header['head1'][0]
    extra = header['extra'][0][1]
    dataSize = head1[0:3]
    dataSize = dataSize[::-1]
    mrcType = head1[3]
    if mrcType == 0:
        dataType = np.int8
    elif mrcType == 1:
        dataType = np.int16
    elif mrcType == 2:
        dataType = np.float32
    elif mrcType == 6:
        dataType = np.uint16
    num0 = int(np.prod(dataSize, dtype=np.uint64))
    with open(ogmaskpath) as f:
        ogmask = np.fromfile(f, dtype=dataType, count=num0, offset=1024 + extra)
    ogmask = ogmask.reshape(dataSize)
    ogmask = ogmask[0, :, :]

    new_shape = tuple(int(dim * scale_factor) for dim in ogmask.shape)
    scaledmask = np.zeros(new_shape, dtype=ogmask.dtype)
    for y in range(new_shape[0]):
        for x in range(new_shape[1]):
            scaledmask[y, x] = ogmask[
                int(y / scale_factor),
                int(x / scale_factor)
            ]

    new_width = str(int(364 * scale_factor))
    new_height = str(int(36 * scale_factor))

    return (scaledmask, new_width, new_height)


class SubtractOperation:

    def __init__(self):
        self.subtract_running = False
        self.subtract_thread_instance = None
        self.output_text = None

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as config_file:
            self.config = json.load(config_file)

    def safe_output_insert(self, text):
        if self.output_text:
            self.output_text.after(0, lambda: self.output_text.insert(tk.END, text))
            self.output_text.after(0, lambda: self.output_text.see(tk.END))

    def subtract(self, output_text, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask,
                 radio_option_manual, radio_option_auto, entry_pixel_size, entry_mask, entry_searchstart,
                 entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub,
                 browse_button_coordstosub, browse_button_mask, notebook, jobalias):

        self.output_text = output_text

        self.subtract_script = self.config.get("subtract_script")

        if not os.path.exists(self.subtract_script):
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END,f"Error: Subtraction script does not exist: {self.subtract_script}\n")
            output_text.see(tk.END)
            return

        def subtract_thread():
            mictosub_dir = entry_mictosub_dir.get()
            coordstosub_dir = entry_coordstosub.get()
            suboutput_dir = entry_suboutput.get()
            pixelsize = entry_pixel_size.get()
            mask = entry_mask.get()
            searchstart = entry_searchstart.get()
            searchend = entry_searchend.get()
            automask = selected_automask.get()

            output_text.delete(1.0, tk.END)

            # The sync process is running
            self.subtract_running = True
            updategui.set_update_flag(jobalias, True)
            updategui.change_tabtitle(notebook, jobalias)
            disable_ui_elements(output_text, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask,
                                radio_option_manual, radio_option_auto, entry_pixel_size, entry_mask, entry_searchstart,
                                entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub,
                                browse_button_coordstosub, browse_button_mask)

            if not os.path.exists("Subflow"):
                os.makedirs("Subflow")

            i = 0
            subtemp = os.path.join("Subflow", f"temp-{jobalias}{i}")
            while os.path.exists(subtemp):
                i += 1
                subtemp = os.path.join("Subflow", f"temp-{jobalias}{i}")
            os.makedirs(subtemp)

            self.safe_output_insert(f"Created temporary directory for subtraction files {subtemp}.\n")

            if not os.path.exists(suboutput_dir):
                try:
                    os.mkdir(suboutput_dir)
                    self.safe_output_insert(f"Created the {suboutput_dir} folder.\n")
                except Exception as e:
                    self.safe_output_insert(f"Could not create the {suboutput_dir} folder: {str(e)}\n")
                    self.subtract_running = False
                    updategui.set_update_flag(jobalias, False)
                    return

            if automask == "Auto":
                self.safe_output_insert("Creating scaled mask in SubtractionFiles...\n")

                ogmaskpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "MT-290A_mask_angpix1p1A_box364X36.mrc")

                scale_factor = 1.1 / float(pixelsize)

                scaledmask, new_width, new_height = scalemask(ogmaskpath, scale_factor)

                newmaskname = "MT-290A_mask_angpix" + pixelsize.replace(".", "p") + "A_box" + str(new_width) + "X" + str(
                    new_height) + ".mrc"

                if not os.path.exists("SubtractionFiles"):
                    os.makedirs("SubtractionFiles")

                newmaskpath = os.path.join("SubtractionFiles", newmaskname)

                with mrcfile.new(newmaskpath, overwrite=True) as output_mrc:
                    output_mrc.set_data(scaledmask)

                self.safe_output_insert(f"Wrote {newmaskpath}.\n")

                mask = newmaskpath  # overwrite

            else:
                if not os.path.exists(mask):
                    self.safe_output_insert(f"Could not find {mask}.\n")

            self.safe_output_insert("Subtracting...\n")
            self.safe_output_insert("\nLooking for new split coordinate file...\n")
            announced = True

            while not os.path.exists(coordstosub_dir):
                time.sleep(4)

            # Use ThreadPoolExecutor to process multiple images simultaneously
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_to_coordinate = {}
                processed_files = set()

                while self.subtract_running:
                    # List of coordinate files to process
                    coordinate_files = [f for f in os.listdir(coordstosub_dir)
                                        if f.endswith("_resam_Zscore_helix_split.txt") and f not in processed_files]

                    for coordinatefile in coordinate_files:
                        if not self.subtract_running:
                            shutil.rmtree(subtemp)
                            self.safe_output_insert("\nSubtraction stopped.\n")
                            updategui.set_update_flag(jobalias, False)
                            return

                        coordstosub = os.path.join(coordstosub_dir, coordinatefile)

                        originname = coordinatefile.split("_resam_Zscore_helix_split.txt")[0] + ".mrc"
                        originpath = os.path.join(mictosub_dir, originname)
                        origintemp = os.path.join(subtemp, originname)

                        subname = coordinatefile.split("_resam_Zscore_helix_split.txt")[0] + "_sub.mrc"
                        subpath = os.path.join(suboutput_dir, subname)
                        micsubtemp = os.path.join(subtemp, subname)  # before moving it's here

                        if not os.path.exists(originpath):
                            self.safe_output_insert(f"Could not find {originpath}\n")
                            continue

                        if not os.path.exists(subpath):
                            # Submit the subtraction task to the executor
                            future = executor.submit(self.process_subtraction, origintemp, originpath, micsubtemp,
                                                     subpath, coordstosub, mask, searchstart, searchend, subtemp)
                            future_to_coordinate[future] = coordinatefile
                            processed_files.add(coordinatefile)

                    # Check for completed futures
                    done_futures = []
                    for future in future_to_coordinate:
                        if future.done():
                            coordinatefile = future_to_coordinate[future]
                            try:
                                future.result()
                            except Exception as e:
                                self.safe_output_insert(f"Error processing {coordinatefile}: {str(e)}\n")
                            else:
                                self.safe_output_insert(f"Completed processing {coordinatefile}\n")
                            done_futures.append(future)

                    # Remove completed futures from the tracking dictionary
                    for future in done_futures:
                        del future_to_coordinate[future]

                    if not announced and self.subtract_running:
                        self.safe_output_insert("\nLooking for next split coordinate file...\n")
                        announced = True

                    if self.subtract_running:
                        time.sleep(4)

            # Clean up temporary directory after processing
            shutil.rmtree(subtemp)
            self.safe_output_insert("\nSubtraction completed.\n")
            updategui.set_update_flag(jobalias, False)
            enable_ui_elements(output_text, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask,
                               radio_option_manual, radio_option_auto, entry_pixel_size, entry_mask, entry_searchstart,
                               entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub,
                               browse_button_coordstosub, browse_button_mask)

        self.subtract_thread_instance = threading.Thread(target=subtract_thread, name="subflow-subtract")
        self.subtract_thread_instance.daemon = True
        self.subtract_thread_instance.start()

    def process_subtraction(self, origintemp, originpath, micsubtemp, subpath, coordstosub, mask, searchstart,
                            searchend, subtemp):
        # Link the original image to a temporary location
        subprocess.run(["ln", "-sf", os.path.join(os.getcwd(), originpath), os.path.join(os.getcwd(), origintemp)])

        try:
            result = subprocess.run([
                self.subtract_script,
                origintemp,
                mask,
                coordstosub,
                "0",
                searchstart,
                searchend
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            stdout_output = result.stdout
            stderr_output = result.stderr

            if result.returncode == 0:
                self.safe_output_insert(stdout_output)
                self.safe_output_insert(stderr_output)

                mvcommand = f'mv {micsubtemp} {subpath}'
                subprocess.run(mvcommand, shell=True)

                self.safe_output_insert(f"Moved to {subpath}.\n")

                rmcommand = f'rm -f {subtemp}/*ave*'
                subprocess.run(rmcommand, shell=True)

                self.safe_output_insert(f"Subtracted: {os.path.basename(originpath)}\n")

            else:
                self.safe_output_insert(f"Error subtracting {os.path.basename(originpath)}.\n")
                self.safe_output_insert(stdout_output)
                self.safe_output_insert(stderr_output)
                self.safe_output_insert("(one possibility is that your micrographs are float16 when they shouldn't be)\n")
        except Exception as e:
            self.safe_output_insert(f"Error subtracting {os.path.basename(originpath)}: {str(e)}\n")

    def stop_subtract(self, output_text, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask,
                      radio_option_manual, radio_option_auto, entry_pixel_size, entry_mask, entry_searchstart,
                      entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub,
                      browse_button_coordstosub, browse_button_mask, jobalias):
        self.subtract_running = False
        self.safe_output_insert("Subtraction stopping...\n")
        enable_ui_elements(output_text, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask,
                           radio_option_manual, radio_option_auto, entry_pixel_size, entry_mask, entry_searchstart,
                           entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub,
                           browse_button_coordstosub, browse_button_mask)
        updategui.set_update_flag(jobalias, False)


def disable_ui_elements(output_text, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask,
                        radio_option_manual, radio_option_auto, entry_pixel_size, entry_mask, entry_searchstart,
                        entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub,
                        browse_button_coordstosub, browse_button_mask):
    entry_mictosub_dir.config(state='disabled')
    entry_coordstosub.config(state='disabled')
    entry_suboutput.config(state='disabled')
    radio_option_manual.config(state='disabled')
    radio_option_auto.config(state='disabled')
    entry_pixel_size.config(state='disabled')
    entry_mask.config(state='disabled')
    entry_searchstart.config(state='disabled')
    entry_searchend.config(state='disabled')
    browse_button_mictosub.config(state='disabled')
    browse_button_coordstosub.config(state='disabled')
    browse_button_mask.config(state='disabled')
    subtract_button.config(state='disabled')
    stop_subtract_button.config(state='normal')


def enable_ui_elements(output_text, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask,
                       radio_option_manual, radio_option_auto, entry_pixel_size, entry_mask, entry_searchstart,
                       entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub,
                       browse_button_coordstosub, browse_button_mask):
    entry_mictosub_dir.config(state='normal')
    entry_coordstosub.config(state='normal')
    entry_suboutput.config(state='normal')
    radio_option_manual.config(state='normal')
    radio_option_auto.config(state='normal')
    if selected_automask.get() == "Auto":
        entry_pixel_size.config(state='normal')
        entry_mask.config(state='disabled')
        browse_button_mask.config(state='disabled')
    else:
        entry_pixel_size.config(state='disabled')
        entry_mask.config(state='normal')
        browse_button_mask.config(state='normal')
    browse_button_mictosub.config(state='normal')
    browse_button_coordstosub.config(state='normal')
    entry_searchstart.config(state='normal')
    entry_searchend.config(state='normal')
    subtract_button.config(state='normal')
    stop_subtract_button.config(state='disabled')