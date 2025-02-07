import tkinter as tk
import subprocess
import threading
import os
import time
import sys
import shutil
from starparser import fileparser
import pandas as pd
import glob


def submerge(output_text_step26, entry_firstsub, browse_button_firstsub, entry_secondsub, browse_button_secondsub, entry_outputsubmerge, submerge_button):

    def mergesubs():

        firstsubdir = entry_firstsub.get()
        secondsubdir = entry_secondsub.get()
        suboutputdir = entry_outputsubmerge.get()
        
        output_text_step26.delete(1.0, tk.END)

        if not os.path.exists(firstsubdir):
            output_text_step26.insert(tk.END, f"{firstsubdir} doesn't exist.\n")
            output_text_step26.see(tk.END)
            return
        elif not os.path.exists(secondsubdir):
            output_text_step26.insert(tk.END, f"{secondsubdir} doesn't exist.\n")
            output_text_step26.see(tk.END)
            return

        if not os.path.exists(suboutputdir):
            os.makedirs(suboutputdir)

        submerge_button.config(state='disabled')
        entry_firstsub.config(state='disabled')
        browse_button_firstsub.config(state='disabled')
        entry_secondsub.config(state='disabled')
        browse_button_secondsub.config(state='disabled')
        entry_outputsubmerge.config(state='disabled')

        output_text_step26.insert(tk.END, f"\nMerging {firstsubdir} and {secondsubdir}...\n")

        try:

            firstsubmics = [os.path.basename(name) for name in os.listdir(firstsubdir) if name.endswith("_sub.mrc")]
            secondsubmics = [os.path.basename(name) for name in os.listdir(secondsubdir) if name.endswith("_sub_sub.mrc")]

            firstsubmics = [name.split("_sub.mrc")[0] for name in firstsubmics]
            secondsubmics = [name.split("_sub_sub.mrc")[0] for name in secondsubmics]

            onlyfirstsubs = [name for name in firstsubmics if name not in secondsubmics]

            total_onlyfirstsubs = "{:,}".format(len(onlyfirstsubs))
            total_secondsubs = "{:,}".format(len(secondsubmics))
            totalsubmics = "{:,}".format(len(onlyfirstsubs)+len(secondsubmics))

            for moveme in secondsubmics:
                subprocess.run(["ln", "-sf", os.path.join(os.getcwd(), secondsubdir, moveme+"_sub_sub.mrc"), os.path.join(os.getcwd(), suboutputdir, moveme+"_sub.mrc")])

            for moveme in onlyfirstsubs:
                subprocess.run(["ln", "-sf", os.path.join(os.getcwd(), firstsubdir, moveme+"_sub.mrc"), os.path.join(os.getcwd(), suboutputdir, moveme+"_sub.mrc")])

            output_text_step26.insert(tk.END, f"\nLinked to {suboutputdir}:\n{total_secondsubs} from {secondsubdir}\n{total_onlyfirstsubs} from {firstsubdir}\n\nTotal: {totalsubmics} subtracted micrographs")
            output_text_step26.see(tk.END)

            if not os.path.exists("Subflow"):
                os.makedirs("Subflow")

            todelete = [os.path.join(firstsubdir, name+"_sub.mrc") for name in firstsubmics if name in secondsubmics]
            with open("Subflow/micrographs-to-delete.txt", "w") as f:
                for name in todelete:
                    f.write(name + "\n")

            output_text_step26.insert(tk.END, f"\n\nYou can delete singly-subtracted micrographs that have a doubly-subtracted version. See Subflow/micrographs-to-delete.txt.")
            output_text_step26.insert(tk.END, f"\n\nCheck the file before attempting to delete the paths (you can use \"xargs -a Subflow/micrographs-to-delete.txt rm -f\")")
            output_text_step26.see(tk.END)

        except Exception as e:

            output_text_step26.insert(tk.END, f"Error: {str(e)}\n")
            output_text_step26.see(tk.END)

        submerge_button.config(state='normal')
        entry_firstsub.config(state='normal')
        browse_button_firstsub.config(state='normal')
        entry_secondsub.config(state='normal')
        browse_button_secondsub.config(state='normal')
        entry_outputsubmerge.config(state='normal')

    mergesubs_instance = threading.Thread(target=mergesubs, name="subflow-mergesubs")
    mergesubs_instance.daemon = True
    mergesubs_instance.start()

def pickmerge(output_text_step26_2, entry_firstpicks, browse_button_firstpicks, entry_secondpicks, browse_button_secondpicks, entry_outputpickmerge, pickmerge_button):

    def mergepicks():

        firstpicksdir = entry_firstpicks.get()
        secondpicksdir = entry_secondpicks.get()
        pickoutputdir = entry_outputpickmerge.get()
        
        output_text_step26_2.delete(1.0, tk.END)

        if not os.path.exists(firstpicksdir):
            output_text_step26_2.insert(tk.END, f"{firstpicksdir} doesn't exist.\n")
            output_text_step26_2.see(tk.END)
            return
        elif not os.path.exists(secondpicksdir):
            output_text_step26_2.insert(tk.END, f"{secondpicksdir} doesn't exist.\n")
            output_text_step26_2.see(tk.END)
            return

        if not os.path.exists(pickoutputdir):
            os.makedirs(pickoutputdir)

        pickmerge_button.config(state='disabled')
        entry_firstpicks.config(state='disabled')
        browse_button_firstpicks.config(state='disabled')
        entry_secondpicks.config(state='disabled')
        browse_button_secondpicks.config(state='disabled')
        entry_outputpickmerge.config(state='disabled')

        output_text_step26_2.insert(tk.END, f"\nMerging {firstpicksdir} and {secondpicksdir}...\n")

        try:

            firstpicks = [os.path.basename(name) for name in os.listdir(firstpicksdir)]
            secondpicks = [os.path.basename(name) for name in os.listdir(secondpicksdir)]

            firstpicks = [name.split("_sub.star")[0] for name in firstpicks]
            secondpicks = [name.split("_sub_sub.star")[0] for name in secondpicks]

            onlyfirstpicks = [name for name in firstpicks if name not in secondpicks]

            for moveme in secondpicks:
                subprocess.run(["ln", "-sf", os.path.join(os.getcwd(), secondpicksdir, moveme+"_sub_sub.star"), os.path.join(os.getcwd(), pickoutputdir, moveme+"_sub.star")])

            for moveme in onlyfirstpicks:
                subprocess.run(["ln", "-sf", os.path.join(os.getcwd(), firstpicksdir, moveme+"_sub.star"), os.path.join(os.getcwd(), pickoutputdir, moveme+"_sub.star")])

            total_onlyfirstpicks = "{:,}".format(len(onlyfirstpicks))
            total_secondpicks = "{:,}".format(len(secondpicks))
            totalpickmics = "{:,}".format(len(onlyfirstpicks)+len(secondpicks))

            output_text_step26_2.insert(tk.END, f"\nLinked to {pickoutputdir}\n{total_secondpicks} from {secondpicksdir}\n{total_onlyfirstpicks} from {firstpicksdir}\n\nTotal: {totalpickmics} micrographs with picks\n")
            output_text_step26_2.see(tk.END)

        except Exception as e:

            output_text_step26_2.insert(tk.END, f"Error: {str(e)}\n")
            output_text_step26_2.see(tk.END)

        pickmerge_button.config(state='normal')
        entry_firstpicks.config(state='normal')
        browse_button_firstpicks.config(state='normal')
        entry_secondpicks.config(state='normal')
        browse_button_secondpicks.config(state='normal')
        entry_outputpickmerge.config(state='normal')

        output_text_step26_2.insert(tk.END, f"\nCounting total picks...\n")
        output_text_step26_2.see(tk.END)

        ###

        totalpickedparts = 0

        picklist = glob.glob(os.path.join(pickoutputdir, f'*_sub.star'))

        for picked in picklist:

            with open(picked, 'r') as file:
                lines = file.readlines()

            last_underscore_index = -1
            for i, line in enumerate(lines):
                if line.startswith("_"):
                    last_underscore_index = i

            if last_underscore_index == -1:
                non_empty_lines_after_last_underscore=0
            
            non_empty_lines_after_last_underscore = 0
            for line in lines[last_underscore_index + 1:]:
                if line.strip():
                    non_empty_lines_after_last_underscore += 1

            totalpickedparts+=non_empty_lines_after_last_underscore

        totalpickedparts="{:,}".format(totalpickedparts)

        ###

        output_text_step26_2.insert(tk.END, f"\n{totalpickedparts} coordinates\n")
        output_text_step26_2.see(tk.END)
    

    mergepicks_instance = threading.Thread(target=mergepicks, name="subflow-mergepicks")
    mergepicks_instance.daemon = True
    mergepicks_instance.start()

def picklink(output_text_step10b, entry_firstpicks_single, entry_outputpickmerge_single,browse_button_firstpickssingle, browse_button_outputpickmergesingle, linksingle_button):

    def linkpicks():

        firstpicksdir = entry_firstpicks_single.get()
        pickoutputdir = entry_outputpickmerge_single.get()
        
        output_text_step10b.delete(1.0, tk.END)

        if not os.path.exists(firstpicksdir):
            output_text_step10b.insert(tk.END, f"{firstpicksdir} doesn't exist.\n")
            output_text_step10b.see(tk.END)
            return

        if not os.path.exists(pickoutputdir):
            output_text_step10b.insert(tk.END, f"{pickoutputdir} doesn't exist.\n")
            output_text_step10b.see(tk.END)
            return

        entry_firstpicks_single.config(state='disabled')
        entry_outputpickmerge_single.config(state='disabled')
        browse_button_firstpickssingle.config(state='disabled')
        browse_button_outputpickmergesingle.config(state='disabled')
        linksingle_button.config(state='disabled')

        output_text_step10b.insert(tk.END, f"\nLinking star files in {firstpicksdir} to {pickoutputdir}...\n")

        try:

            firstpicks = [os.path.basename(name) for name in os.listdir(firstpicksdir)]

            for moveme in firstpicks:
                subprocess.run(["ln", "-sf", os.path.join(os.getcwd(), firstpicksdir, moveme), os.path.join(os.getcwd(), pickoutputdir, moveme)])

            total_firstpicks = "{:,}".format(len(firstpicks))

            output_text_step10b.insert(tk.END, f"\nLinked {total_firstpicks} picks.\n")
            output_text_step10b.see(tk.END)

        except Exception as e:

            output_text_step10b.insert(tk.END, f"Error: {str(e)}\n")
            output_text_step10b.see(tk.END)

        entry_firstpicks_single.config(state='normal')
        entry_outputpickmerge_single.config(state='normal')
        browse_button_firstpickssingle.config(state='normal')
        browse_button_outputpickmergesingle.config(state='normal')
        linksingle_button.config(state='normal')
    

    linkpicks_instance = threading.Thread(target=linkpicks, name="subflow-linkpicks")
    linkpicks_instance.daemon = True
    linkpicks_instance.start()
