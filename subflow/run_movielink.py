import os
import subprocess
import time
import tkinter as tk
import threading
import glob
from subflow import updategui

def disable_ui_elements(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies):
    entry_sourcemovies.config(state='disabled')
    entry_syncmovies.config(state='disabled')
    # entry_suffix.config(state='disabled')
    moviesync_button.config(state='disabled')
    browse_button_sourcemovies.config(state='disabled')
    stop_moviesync_button.config(state='normal')
def enable_ui_elements(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies):
    entry_sourcemovies.config(state='normal')
    entry_syncmovies.config(state='normal')
    # entry_suffix.config(state='normal')
    moviesync_button.config(state='normal')
    browse_button_sourcemovies.config(state='normal')
    stop_moviesync_button.config(state='normal')

sync_running = False

def syncmovies(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies, notebook):
    
    global sync_running

    output_text_stepm2.delete(1.0, tk.END)  # Clear previous output

    def sync_thread():
        global sync_running
        source_dir = entry_sourcemovies.get()
        sync_dir = entry_syncmovies.get()

        source_dir = os.path.abspath(source_dir)

        # Set the flag to indicate that the sync process is running
        sync_running = True
        updategui.set_update_flag("linkmov", True)
        updategui.change_tabtitle(notebook, "linkmov")
        disable_ui_elements(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies)

        announced=False
        matching_items = glob.glob(source_dir)
        while not matching_items:
            if not announced:
                output_text_stepm2.insert(tk.END, "Looking for new movie or grid square...\n")
                output_text_stepm2.see(tk.END)
            announced=True

            if not sync_running:
                updategui.set_update_flag("linkmov", False)
                output_text_stepm2.insert(tk.END, "Link stopped.\n")
                output_text_stepm2.see(tk.END)
                enable_ui_elements(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies)
                return

            time.sleep(1)
            matching_items = glob.glob(source_dir)

        output_text_stepm2.insert(tk.END, "Linking...\n")
        output_text_stepm2.insert(tk.END, "Looking for new movie or grid square...\n")
        output_text_stepm2.see(tk.END)

        if not os.path.exists(sync_dir):
            try:
                os.mkdir(sync_dir)
                output_text_stepm2.insert(tk.END, f"Created the {sync_dir} folder.\n")
            except Exception as e:
                output_text_stepm2.insert(tk.END, f"Could not create {sync_dir} folder: {str(e)}\n")
                sync_running = False
                enable_ui_elements(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies)
                updategui.set_update_flag("linkmov", False)
                return
            output_text_stepm2.see(tk.END)

        while sync_running:

            if not os.path.exists(sync_dir):
                os.makedirs(sync_dir)

            matching_items = glob.glob(source_dir)

            for source_path in matching_items:

                if not sync_running:
                    output_text_stepm2.insert(tk.END, "Link stopped.\n")
                    output_text_stepm2.see(tk.END)
                    enable_ui_elements(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies)
                    updategui.set_update_flag("linkmov", False)
                    return

                symlink_path = os.path.join(os.getcwd(), sync_dir, os.path.basename(source_path))

                if not os.path.exists(symlink_path):
                    try:
                        subprocess.run(["ln", "-s", source_path, symlink_path])
                        output_text_stepm2.insert(tk.END, f"Linked: {source_path}\n")
                    except Exception as e:
                        output_text_stepm2.insert(tk.END, f"Error linking {source_path}: {str(e)}\n")
                    output_text_stepm2.see(tk.END)

            time.sleep(4)

    # Create and start the sync thread
    sync_thread_instance = threading.Thread(target=sync_thread, name="subflow-moviesync")
    sync_thread_instance.daemon = True
    sync_thread_instance.start()
    

def stop_syncmovies(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies):
    global sync_running
    sync_running = False
    updategui.set_update_flag("linkmov", False)
    output_text_stepm2.insert(tk.END, "Link stopping.\n")
    output_text_stepm2.see(tk.END)
    enable_ui_elements(entry_sourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_sourcemovies)
