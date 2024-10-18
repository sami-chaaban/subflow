import tkinter as tk
import subprocess
import threading
import os
import time
import sys
import shutil
from starparser import fileparser
import pandas as pd

def fixstar(output_text_step10, entry_micstar, entry_prefix, entry_submicsdir, entry_outstar, fixstar_button):

    micstar=entry_micstar.get()
    submicsdir=entry_submicsdir.get()
    outstar=entry_outstar.get()
    prefix=entry_prefix.get()
    
    output_text_step10.delete(1.0, tk.END)  # Clear previous output

    if not os.path.exists(micstar):
        output_text_step10.insert(tk.END, f"{micstar} doesn't exist\n")
        output_text_step10.see(tk.END)
        return

    fixstar_button.config(state='disabled')

    output_text_step10.insert(tk.END, f"Fixing {micstar}...\n")

    try:

        subtractedmics = [os.path.join(submicsdir,name) for name in os.listdir(submicsdir) if "_sub.mrc" in name]

        micstar_pd, metadata = fileparser.getparticles(micstar)
        originalmics = micstar_pd['_rlnMicrographName'].tolist()
        originalmics_temp = [os.path.join(submicsdir,prefix+name.split(prefix)[-1]) for name in originalmics]

        subtractedmics_intheory = [name.split(".mrc")[0]+"_sub.mrc" for name in originalmics_temp]

        micstar_pd['_rlnMicrographName'] = subtractedmics_intheory

        micstoremove = list(set(subtractedmics_intheory) - set(subtractedmics))

        m = "|".join(micstoremove)
        micstar_pd.drop(micstar_pd[micstar_pd["_rlnMicrographName"].str.contains(m)].index , axis=0, inplace=True)

        if micstar_pd.empty:
            output_text_step10.insert(tk.END, "Error: no micrographs could be matched, nothing to output.\n")
            output_text_step10.see(tk.END)

        else:
            outpath=os.path.join(os.path.dirname(micstar),outstar)
            fileparser.writestar(micstar_pd, metadata, outpath)

            output_text_step10.insert(tk.END, f"Wrote {outpath}.\n")
            output_text_step10.see(tk.END)

    except Exception as e:

        output_text_step10.insert(tk.END, f"Error: {str(e)}\n")
        output_text_step10.see(tk.END)

    fixstar_button.config(state='normal')