import os
import subprocess
import time
import tkinter as tk
import threading
import glob
from subflow import updategui

def disable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere):
    entry_sourcemics.config(state='disabled')
    entry_syncmics.config(state='disabled')
    entry_suffix.config(state='disabled')
    sync_button.config(state='disabled')
    browse_button_sourcemics.config(state='disabled')
    radio_option_linktype_corr.config(state='disabled')
    radio_option_linktype_other.config(state='disabled')
    entry_sourcemics_elsewhere.config(state='disabled')
    stop_sync_button.config(state='normal')
def enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere):
    entry_sourcemics.config(state='normal')
    entry_syncmics.config(state='normal')
    entry_suffix.config(state='normal')
    sync_button.config(state='normal')
    browse_button_sourcemics.config(state='normal')
    radio_option_linktype_corr.config(state='normal')
    radio_option_linktype_other.config(state='normal')
    entry_sourcemics_elsewhere.config(state='normal')
    stop_sync_button.config(state='normal')

sync_running = False

def sync(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere, notebook):
    
    global sync_running

    output_text_step1.delete(1.0, tk.END) 

    def sync_thread():
        global sync_running
        sync_dir = entry_syncmics.get()
        suffix = entry_suffix.get()
        linktype = selected_linktype.get()

        if linktype == "Relion":
            source_dir = entry_sourcemics.get()
        else:
            source_dir=entry_sourcemics_elsewhere.get()
            source_dir = os.path.abspath(source_dir)

        sync_running = True
        updategui.set_update_flag("linkcorr", True)
        updategui.change_tabtitle(notebook, "linkcorr")
        disable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)

        if not os.path.exists(sync_dir):
            try:
                os.mkdir(sync_dir)
                output_text_step1.insert(tk.END, f"Created the {sync_dir} folder.\n")
            except Exception as e:
                output_text_step1.insert(tk.END, f"Could not create {sync_dir} folder: {str(e)}\n")
                sync_running = False
                enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
                return
            output_text_step1.see(tk.END)

        announced=False
        if linktype == "Relion":
            while not os.path.exists(source_dir):
                if not announced:
                    output_text_step1.insert(tk.END, "Waiting for source directory...\n")
                    output_text_step1.see(tk.END)
                announced=True
            if not sync_running:
                updategui.set_update_flag("linkcorr", False)
                output_text_step1.insert(tk.END, "Link stopped.\n")
                output_text_step1.see(tk.END)
                enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
                return
            time.sleep(1)

        else:
            matching_items = glob.glob(source_dir)
            while not matching_items:
                if not announced:
                    output_text_step1.insert(tk.END, "Looking for micrographs...\n")
                    output_text_step1.see(tk.END)
                announced=True
            if not sync_running:
                updategui.set_update_flag("linkcorr", False)
                output_text_step1.insert(tk.END, "Link stopped.\n")
                output_text_step1.see(tk.END)
                enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
                return
            time.sleep(1)

        # if not os.path.exists(source_dir):
        #     output_text_step1.insert(tk.END, "Error: Input directory does not exist.\n")
        #     output_text_step1.see(tk.END)
        #     sync_running = False  # Reset the flag
        #     enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
        #     updategui.set_update_flag("linkcorr", False)
        #     return

        output_text_step1.insert(tk.END, "Linking...\n")
        output_text_step1.insert(tk.END, "Looking for new micrograph...\n")
        output_text_step1.see(tk.END)

        while sync_running:

            if linktype == "Relion":
                for root_dir, _, files in os.walk(source_dir):
                    for filename in files:
                        if not sync_running:
                            output_text_step1.insert(tk.END, "Link stopped.\n")
                            output_text_step1.see(tk.END)
                            enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
                            updategui.set_update_flag("linkcorr", False)
                            return
                        if filename.endswith(suffix + ".mrc"):
                            file_path = os.path.join(os.getcwd(), root_dir, filename)
                            symlink_path = os.path.join(os.getcwd(), sync_dir, filename)
                            if not os.path.exists(symlink_path):
                                try:
                                    subprocess.run(["ln", "-s", file_path, symlink_path])
                                    output_text_step1.insert(tk.END, f"Linked: {filename}\n")
                                except Exception as e:
                                    output_text_step1.insert(tk.END, f"Error linking {filename}: {str(e)}\n")
                                output_text_step1.see(tk.END)


            else:
                matching_items = glob.glob(source_dir)

                for source_path in matching_items:
                    if not sync_running:
                        output_text_step1.insert(tk.END, "Link stopped.\n")
                        output_text_step1.see(tk.END)
                        enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
                        updategui.set_update_flag("linkcorr", False)
                        return

                    symlink_path = os.path.join(os.getcwd(), sync_dir, os.path.basename(source_path))

                    if not os.path.exists(symlink_path):
                        try:
                            subprocess.run(["ln", "-s", source_path, symlink_path])
                            output_text_step1.insert(tk.END, f"Linked: {source_path}\n")
                        except Exception as e:
                            output_text_step1.insert(tk.END, f"Error linking {source_path}: {str(e)}\n")
                        output_text_step1.see(tk.END)


            time.sleep(4)

    # Create and start the sync thread
    sync_thread_instance = threading.Thread(target=sync_thread, name="subflow-sync")
    sync_thread_instance.daemon = True
    sync_thread_instance.start()
    

def stop_sync(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere):
    global sync_running
    sync_running = False
    updategui.set_update_flag("linkcorr", False)
    output_text_step1.insert(tk.END, "Link stopping.\n")
    output_text_step1.see(tk.END)
    enable_ui_elements(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
