import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sv_ttk

import subflow
from subflow.run_movielink import syncmovies, stop_syncmovies
from subflow.run_eertotif import eertif, stop_eertif
from subflow.run_preprocess import corr, stop_corr, forcestop_corr
from subflow.run_miclink import sync, stop_sync
from subflow.run_display_mics import displaycorr
from subflow.run_cryolo import CryoloPickOperation, reset_picks
from subflow.run_display_mtpicks import display
from subflow.run_mcf import MCFOperation
from subflow.run_display_mcf import displaymcf
from subflow.run_split import SplitOperation
from subflow.run_display_split import displaysplit
from subflow.run_subtract import SubtractOperation
from subflow.run_display_subtract import displaysub
from subflow.run_fixstar import fixstar
from subflow.run_display_complexpicks import displaycomplex
from subflow.run_merge import submerge, pickmerge
from subflow.run_extract import relionimport, relionextract
from subflow.run_csparc import cscreateworkspace, csimportparts, csimportvols, cshetero, csnonunif, cs2star

import os, sys
import socket
import glob
import threading
import time
from datetime import datetime
import pandas as pd
from starparser import fileparser
from subflow import updategui
from subflow.updategui import flagmap

def gui():

    ##############
    #MAIN WINDOW
    root = tk.Tk()

    notebook = ttk.Notebook(root)
    notebook.grid(row=1, column=0, columnspan=2, sticky="nsew")
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    sv_ttk.set_theme("light")

    fontname = "helvetica"
    header_font = (fontname, 16)
    common_font = (fontname, 13)
    common_font_bold = (fontname, 13, "bold")
    output_font = (fontname, 11)

    directory_parts = os.getcwd().split(os.path.sep)
    last_three_layers = directory_parts[-3:]
    last_three_layers = os.path.sep.join(last_three_layers)
    hostname=socket.gethostname().split(".")[0]
    # top_label = tk.Label(root, text=f"{hostname} : {last_three_layers}", bg="#f0f0f0", font=common_font)
    # top_label.grid(row=0, column=0, columnspan=2, sticky="ew")

    root.title(f"{hostname} : {last_three_layers}")

    tabs = []
    for step in range(1, 31):
        tab = ttk.Frame(notebook)
        tabs.append(tab)
        notebook.add(tab, text=f"{step}")

    # Customize the style of notebook tabs
    style = ttk.Style()
    style.configure("lefttab.TNotebook", tabposition="wn")
    notebook.configure(style="lefttab.TNotebook")

    style.configure("TNotebook.Tab", font=common_font_bold) 
    style.configure("TLabel", font=common_font)
    style.configure("TEntry", font=common_font)
    style.configure("TButton", font=common_font)

    bigtitle = ttk.Style()
    bigtitle.configure("title.TLabel", font=header_font)

    checkbuttonstyle = ttk.Style()
    checkbuttonstyle.configure("Switch.TCheckbutton", indicatoron=False)

    # Allow the notebook to expand when resizing
    notebook.grid_rowconfigure(0, weight=1)
    notebook.grid_columnconfigure(0, weight=1)

    ##############
    #AUTO-PROPAGATE VARIABLES

    def set_pixelsize(*args):
        global globalpixelsize
        globalpixelsize = typedpixelsize.get()
        pixelsizesearch_focusout(*args)
    typedpixelsize = tk.StringVar()
    globalpixelsize = "1.1"

    def set_pickdir(*args):
        global globalpickdir
        globalpickdir = typedpickdir.get()
    typedpickdir = tk.StringVar()
    globalpickdir = "Cryolo/MTs/allpicks_0p2/STAR"

    def set_pickdir2(*args):
        global globalpickdir2
        globalpickdir2 = typedpickdir2.get()
    typedpickdir2 = tk.StringVar()
    globalpickdir2 = "Cryolo/MTs-round2/allpicks_0p2/STAR"

    def set_suffix(*args):
        global globalsuffix
        globalsuffix = typedsuffix.get()
    typedsuffix = tk.StringVar()
    globalsuffix = "fractions"

    def set_suffix2(*args):
        global globalsuffix2
        globalsuffix2 = typedsuffix2.get()
    typedsuffix2 = tk.StringVar()
    globalsuffix2 = "fractions_sub"

    def set_numdisplay(*args):
        global globalnumdisplay
        globalnumdisplay = typednumdisplay.get()
    typednumdisplay = tk.StringVar()
    globalnumdisplay = "25"

    def set_micrographs(*args):
        global globalmicrographs
        globalmicrographs = typedmicrographs.get()
    typedmicrographs = tk.StringVar()
    globalmicrographs = "Micrographs"

    def set_submicrographs(*args):
        global globalsubmicrographs
        globalsubmicrographs = typedsubmicrographs.get()
    typedsubmicrographs = tk.StringVar()
    globalsubmicrographs = "SubtractedMicrographs"

    def set_submicrographs2(*args):
        global globalsubmicrographs2
        globalsubmicrographs2 = typedsubmicrographs2.get()
    typedsubmicrographs2 = tk.StringVar()
    globalsubmicrographs2 = "SubtractedMicrographs2"

    def set_mcfdir(*args):
        global globalmcfdir
        globalmcfdir = typedmcfdir.get()
    typedmcfdir = tk.StringVar()
    globalmcfdir = "Cryolo/MTs/allpicks_0p2/STAR/MCF-41-20-3-2"

    def set_mcfdir2(*args):
        global globalmcfdir2
        globalmcfdir2 = typedmcfdir2.get()
    typedmcfdir2 = tk.StringVar()
    globalmcfdir2 = "Cryolo/MTs-round2/allpicks_0p2/STAR/MCF-41-20-3-2"

    def set_splitdir(*args):
        global globalsplitdir
        globalsplitdir = typedsplitdir.get()
    typedsplitdir = tk.StringVar()
    globalsplitdir = "Cryolo/MTs/allpicks_0p2/STAR/MCF-41-20-3-2/Split-10"

    def set_splitdir2(*args):
        global globalsplitdir
        globalsplitdir2 = typedsplitdir2.get()
    typedsplitdir2 = tk.StringVar()
    globalsplitdir2 = "Cryolo/MTs-round2/allpicks_0p2/STAR/MCF-41-20-3-2/Split-10"

    def set_corrmics(*args):
        global globalcorrmics
        globalcorrmics = typedcorrmics.get()
    typedcorrmics = tk.StringVar()
    globalcorrmics = "MotionCorr/job002"

    def set_movies(*args):
        global globalmovies
        globalmovies = typedmovies.get()
    typedmovies = tk.StringVar()
    globalmovies = "Movies"


    ##############
    #Stop/start All

    def startall():
        if not updategui.get_update_flag("linkmov"):
            syncmovies(entry_scopesourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_scopesourcemovies, notebook)
        if eer_var.get()==1:
            if not updategui.get_update_flag("eertotif"): 
                eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button, notebook)
        if not updategui.get_update_flag("preprocess"):
            corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain, notebook)
        if not updategui.get_update_flag("linkcorr"):
            sync(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere, notebook)
        if not updategui.get_update_flag("pickfil"):
            pick_operation_fil.pick(output_text_step2, 253, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset,resetpicks_button, notebook, "pickfil")
        if not updategui.get_update_flag("mcf"):
            mcf_operation.mcf(output_text_step4, entry_coordinate_dir, entry_suffix_step4, entry_pixel_size_step4, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics, notebook, "mcf")
        if not updategui.get_update_flag("split"):
            split_operation.split(output_text_step6, entry_splitcoordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics, notebook, "split")
        if not updategui.get_update_flag("sub"):
            subtract_operation.subtract(output_text_step8, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask, radio_option_manual, radio_option_auto, entry_pixel_size_step8, entry_mask, entry_searchstart, entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub, browse_button_coordstosub, browse_button_mask, notebook, "sub")
        if not updategui.get_update_flag("pickcomp"):
            pick_operation_complex.pick(output_text_step11, 638, entry_submicrographs_topick, entry_pixel_size_subpick, entry_cryolo_model_complex, entry_threshold_complex, entry_projectname_complex, entry_pickname_complex, entry_gpu_complex, pickcomplex_button, stop_pickcomplex_button, browse_button_submicrographs_topick, browse_button_cryolo_model_complex, entry_picksubset_complex, resetcomplexpicks_button, notebook, "pickcomp")
        if doublesub_var.get() == 1:
            if not updategui.get_update_flag("pickfil2"):
                pick_operation_fil2.pick(output_text_step16, 253, entry_micrographs_topick16, entry_pixel_size16, entry_cryolo_model16, entry_threshold16, entry_projectname16, entry_pickname16, entry_gpu16, pick_button16, stop_pick_button16, browse_button_micrographs_topick16, browse_button_cryolo_model16, entry_picksubset16, resetpicks16_button, notebook, "pickfil2")
            if not updategui.get_update_flag("mcf2"):
                mcf_operation18.mcf(output_text_step18, entry_coordinate_dir18, entry_suffix_step18, entry_pixel_size_step18, entry_samplestep18, entry_anglechange18, entry_minseed18, entry_polynomial18, mcf_button18, stop_mcf_button18, browse_coordinate_dir18, entry_tomcfmics_dir18, browse_button_tomcfmics18, notebook, "mcf2")
            if not updategui.get_update_flag("split2"):
                split_operation20.split(output_text_step20, entry_splitcoordinate_dir20, entry_splitvalue20, split_button20, stop_split_button20, browse_button_split_coordinate_dir20, entry_tosplitmics_dir20, browse_button_tosplitmics20, notebook, "split2")
            if not updategui.get_update_flag("sub2"):
                subtract_operation22.subtract(output_text_step22, entry_mictosub_dir22, entry_coordstosub22, entry_suboutput22, selected_automask22, radio_option_manual22, radio_option_auto22, entry_pixel_size_step22, entry_mask22, entry_searchstart22, entry_searchend22, subtract_button22, stop_subtract_button22, browse_button_mictosub22, browse_button_coordstosub22, browse_button_mask22, notebook, "sub2")
            if not updategui.get_update_flag("pickcomp2"):
                pick_operation_complex24.pick(output_text_step24, 638, entry_submicrographs_topick24, entry_pixel_size_subpick24, entry_cryolo_model_complex24, entry_threshold_complex24, entry_projectname_complex24, entry_pickname_complex24, entry_gpu_complex24, pickcomplex_button24, stop_pickcomplex_button24, browse_button_submicrographs_topick24, browse_button_cryolo_model_complex24, entry_picksubset_complex24, resetcomplexpicks24_button, notebook, "pickcomp2")

    def stopall():
        if updategui.get_update_flag("linkmov"):
            stop_syncmovies(entry_scopesourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_scopesourcemovies)
        if updategui.get_update_flag("eertotif"): 
            stop_eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button)
        if updategui.get_update_flag("preprocess"):
            stop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain)
        if updategui.get_update_flag("linkcorr"):
            stop_sync(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere)
        if updategui.get_update_flag("pickfil"):
            pick_operation_fil.stop_pick(output_text_step2)
        if updategui.get_update_flag("mcf"):
            mcf_operation.stop_mcf(output_text_step4, entry_coordinate_dir, entry_suffix_step4, entry_pixel_size_step4, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics, "mcf")
        if updategui.get_update_flag("split"):
            split_operation.stop_split(output_text_step6, entry_splitcoordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics, "split")
        if updategui.get_update_flag("sub"):
            subtract_operation.stop_subtract(output_text_step8, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask, radio_option_manual, radio_option_auto, entry_pixel_size_step8, entry_mask, entry_searchstart, entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub, browse_button_coordstosub, browse_button_mask, "sub")
        if updategui.get_update_flag("pickcomp"):
            pick_operation_complex.stop_pick(output_text_step11)
        if updategui.get_update_flag("pickfil2"):
            pick_operation_fil2.stop_pick(output_text_step16)
        if updategui.get_update_flag("mcf2"):
            mcf_operation18.stop_mcf(output_text_step18, entry_coordinate_dir18, entry_suffix_step18, entry_pixel_size_step18, entry_samplestep18, entry_anglechange18, entry_minseed18, entry_polynomial18, mcf_button18, stop_mcf_button18, browse_coordinate_dir18, entry_tomcfmics_dir18, browse_button_tomcfmics18, "mcf2")
        if updategui.get_update_flag("split2"):
            split_operation20.stop_split(output_text_step20, entry_splitcoordinate_dir20, entry_splitvalue20, split_button20, stop_split_button20, browse_button_split_coordinate_dir20, entry_tosplitmics_dir20, browse_button_tosplitmics20, "split2")
        if updategui.get_update_flag("sub2"):
            subtract_operation22.stop_subtract(output_text_step22, entry_mictosub_dir22, entry_coordstosub22, entry_suboutput22, selected_automask22, radio_option_manual22, radio_option_auto22, entry_pixel_size_step22, entry_mask22, entry_searchstart22, entry_searchend22, subtract_button22, stop_subtract_button22, browse_button_mictosub22, browse_button_coordstosub22, browse_button_mask22, "sub2")
        if updategui.get_update_flag("pickcomp2"):
            pick_operation_complex24.stop_pick(output_text_step24)

    ##############
    #UI

    global show_adv
    show_adv = False

    def toggle_ui():
        if showcoords_checkbox.get() == 1:
            label_splitcoordinate_step9.grid(row=3, column=0, padx=10, pady=2, sticky="e")
            entry_splitcoordinate_step9.grid(row=3, column=1, padx=10, pady=2, sticky="ew")  
            browse_button_splitcoordinate_step9.grid(row=3, column=2, padx=10, pady=2)
        else:
            label_splitcoordinate_step9.grid_remove()
            entry_splitcoordinate_step9.grid_remove()
            browse_button_splitcoordinate_step9.grid_remove()

        if not updategui.get_update_flag("sub"):
            if selected_automask.get() == "Auto":
                entry_mask.config(state='disabled')
                browse_button_mask.config(state='disabled')
                entry_pixel_size_step8.config(state='normal')
            else:
                entry_mask.config(state='normal')
                browse_button_mask.config(state='normal')
                entry_pixel_size_step8.config(state='disabled')

        if not updategui.get_update_flag("sub2"):
            if selected_automask22.get() == "Auto":
                entry_mask22.config(state='disabled')
                browse_button_mask22.config(state='disabled')
                entry_pixel_size_step22.config(state='normal')
            else:
                entry_mask22.config(state='normal')
                browse_button_mask22.config(state='normal')
                entry_pixel_size_step22.config(state='disabled')

        if convertgain_checkbox.get() == 1:
            entry_gainm1.grid(row=6, column=1, padx=10, pady=2, sticky="ew")  
            browse_button_gainm1.grid(row=6, column=2, padx=10, pady=2)
            label_gainm1.grid(row=6, column=0, padx=10, pady=2, sticky="e")
        else:
            entry_gainm1.grid_remove()
            browse_button_gainm1.grid_remove()
            label_gainm1.grid_remove()

        if selected_linktype.get() == "Elsewhere":
            label_sourcemics.grid_remove()
            entry_sourcemics.grid_remove()
            browse_button_sourcemics.grid_remove()
            label_suffix.grid_remove()
            entry_suffix.grid_remove()
            label_sourcemics_elsewhere.grid(row=2, column=0, padx=10, pady=2, sticky="e")
            entry_sourcemics_elsewhere.grid(row=2, column=1, padx=10, pady=2, sticky="ew")
        else:
            label_sourcemics.grid(row=2, column=0, padx=10, pady=2, sticky="e")
            entry_sourcemics.grid(row=2, column=1, padx=10, pady=2, sticky="ew")
            browse_button_sourcemics.grid(row=2, column=2, padx=10, pady=2)
            label_suffix.grid(row=3, column=0, padx=10, pady=2, sticky="e")
            entry_suffix.grid(row=3, column=1, padx=10, pady=2, sticky="ew")
            label_sourcemics_elsewhere.grid_remove()
            entry_sourcemics_elsewhere.grid_remove()

        if doublesub_var.get()==1:
            notebook.tab(16, state="normal")
            notebook.tab(17, state="hidden")
            notebook.tab(18, state="normal")
            notebook.tab(19, state="hidden")
            notebook.tab(20, state="normal")
            notebook.tab(21, state="hidden")
            notebook.tab(22, state="normal")
            notebook.tab(23, state="hidden")
            notebook.tab(24, state="normal")
            notebook.tab(25, state="hidden")
            notebook.tab(26, state="normal")
        else:
            notebook.tab(16, state="hidden")
            notebook.tab(17, state="hidden")
            notebook.tab(18, state="hidden")
            notebook.tab(19, state="hidden")
            notebook.tab(20, state="hidden")
            notebook.tab(21, state="hidden")
            notebook.tab(22, state="hidden")
            notebook.tab(23, state="hidden")
            notebook.tab(24, state="hidden")
            notebook.tab(25, state="hidden")
            notebook.tab(26, state="hidden")

        global show_adv
        if not show_adv:
            label_eergroups_corr.grid_remove()
            entry_eergroups_corr.grid_remove()
            label_gainrot.grid_remove()
            entry_gainrot.grid_remove()
            label_gainflip.grid_remove()
            entry_gainflip.grid_remove()
            label_mtf.grid_remove()
            entry_mtf.grid_remove()
            browse_button_mtf.grid_remove()
            forcestop_corr_button.grid_remove()
            adv_button.config(text="↓")
            show_adv = False
        else:
            label_eergroups_corr.grid(row=7, column=0, padx=10, pady=2, sticky="e")
            entry_eergroups_corr.grid(row=7, column=1, padx=10, pady=2, sticky="ew")
            label_gainrot.grid(row=8, column=0, padx=10, pady=2, sticky="e")
            entry_gainrot.grid(row=8, column=1, padx=10, pady=2, sticky="ew")
            label_gainflip.grid(row=9, column=0, padx=10, pady=2, sticky="e")
            entry_gainflip.grid(row=9, column=1, padx=10, pady=2, sticky="ew")
            label_mtf.grid(row=10, column=0, padx=10, pady=2, sticky="e")
            entry_mtf.grid(row=10, column=1, padx=10, pady=2, sticky="ew")
            browse_button_mtf.grid(row=10, column=2, padx=10, pady=2, sticky="ew")
            forcestop_corr_button.grid(row=11, column=1, padx=10, pady=5, sticky="e")
            adv_button.config(text="↑")
            show_adv = True

        if eer_var.get()==1:
            notebook.tab(2, state="normal")
        else:
            notebook.tab(2, state="hidden")

        check_reset(resetpicks_button, os.path.join("Cryolo", entry_projectname.get(), entry_pickname.get(), "nopicklist.txt"))
        check_reset(resetcomplexpicks_button, os.path.join("Cryolo", entry_projectname_complex.get(), entry_pickname_complex.get(), "nopicklist.txt"))
        check_reset(resetpicks16_button, os.path.join("Cryolo", entry_projectname16.get(), entry_pickname16.get(), "nopicklist.txt"))
        check_reset(resetcomplexpicks24_button, os.path.join("Cryolo", entry_projectname_complex24.get(), entry_pickname_complex24.get(), "nopicklist.txt"))

    def check_reset(button, nopicklist):

        if os.path.exists(nopicklist):
            with open(nopicklist,'r') as file:
                line_count = sum(1 for line in file)
            button.config(text=f"Reset {line_count} unpicked", state='normal')
            button.grid(row=9, column=1, padx=10, pady=5, sticky="e")
        else:
            button.config(text="Reset", state='disabled')
            button.grid_remove()

    def toggle_adv():
        global show_adv
        show_adv = not show_adv
        toggle_ui()

    def toggle_eer_propagate():

        if eer_var.get()==1:
            entry_sourcemovies.delete(0, tk.END)
            entry_sourcemovies.insert(0, "Movies/EER/GridSquare*/Data/*_EER.tif")
            entry_syncmovies.delete(0, tk.END)
            entry_syncmovies.insert(0, "EER")
            entry_suffix.delete(0, tk.END)
            entry_suffix.insert(0, "EER")
            entry_suffix_step18.delete(0, tk.END)
            entry_suffix_step18.insert(0, "EER_sub")
            entry_gainm1.delete(0, tk.END)
            entry_gainm1.insert(0, "GainReference/gain-reference.gain")
            entry_gain.delete(0, tk.END)
            entry_gain.insert(0, "Movies/gain-reference.mrc")
        else:
            entry_sourcemovies.delete(0, tk.END)
            entry_sourcemovies.insert(0, "Movies/GridSquare*/Data/*_fractions.tif")
            entry_syncmovies.delete(0, tk.END)
            entry_syncmovies.insert(0, "Movies")
            entry_suffix.delete(0, tk.END)
            entry_suffix.insert(0, "fractions")
            entry_suffix_step18.delete(0, tk.END)
            entry_suffix_step18.insert(0, "fractions_sub")
            entry_gainm1.delete(0, tk.END)
            entry_gainm1.insert(0, "GainReference/gain-reference.tiff")

        toggle_ui()

    def toggle_doublesub_propagate():

        if doublesub_var.get()==1:
            entry_submicsdir.delete(0, tk.END)
            entry_submicsdir.insert(0, "SubtractedMicrographs-merged")
            entry_subcoords.delete(0, tk.END)
            entry_subcoords.insert(0, "SubtractedMicrographs-merged/*.star")
        else:
            entry_submicsdir.delete(0, tk.END)
            entry_submicsdir.insert(0, "SubtractedMicrographs")
            entry_subcoords.delete(0, tk.END)
            entry_subcoords.insert(0, "SubtractedMicrographs/*.star")

        toggle_ui()

    ##############
    #BROWSE

    def browse_directory(entry_widget):
        current_directory = os.getcwd() 
        directory_path = filedialog.askdirectory(initialdir=current_directory)
        if directory_path:
            relative_path = os.path.relpath(directory_path, current_directory)
            entry_widget.delete(0, tk.END) 
            entry_widget.insert(0, relative_path) 

    def browse_file(entry_widget):
        current_directory = os.getcwd() 
        file_path = filedialog.askopenfilename(initialdir=current_directory)
        if file_path:
            relative_path = os.path.relpath(file_path, current_directory)
            entry_widget.delete(0, tk.END) 
            entry_widget.insert(0, relative_path)

    ##############
    #FOCUS-OUT

    def pickdir_focusout(eventpick, project, pick, step, angle, seed, poly, split, entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9):
        if eventpick.widget not in [entry_splitvalue, entry_splitvalue20]:
            if entry_picks_dir['state']!='disabled':
                entry_picks_dir.delete(0, tk.END)
                entry_picks_dir.insert(0, os.path.join("Cryolo", project, pick))
            if entry_coordinate_dir['state']!='disabled':
                entry_coordinate_dir.delete(0, tk.END)
                entry_coordinate_dir.insert(0, os.path.join("Cryolo", project, pick, "STAR"))
            if entry_mcfcoordinate_dir['state']!='disabled':
                entry_mcfcoordinate_dir.delete(0, tk.END)
                entry_mcfcoordinate_dir.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}"))
            if entry_splitcoordinate_dir['state']!='disabled':
                entry_splitcoordinate_dir.delete(0, tk.END)
                entry_splitcoordinate_dir.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}"))
        if entry_splitcoordinate_dir_step7['state']!='disabled':
            entry_splitcoordinate_dir_step7.delete(0, tk.END)
            entry_splitcoordinate_dir_step7.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}",f"Split-{split}"))
        if entry_coordstosub['state']!='disabled':
            entry_coordstosub.delete(0, tk.END)
            entry_coordstosub.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}",f"Split-{split}"))
        if entry_splitcoordinate_step9['state']!='disabled':
            entry_splitcoordinate_step9.delete(0, tk.END)
            entry_splitcoordinate_step9.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}",f"Split-{split}"))

    def pickdir_focusout_forthreshchange(project, pick, step, angle, seed, poly, split, entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9):
        if entry_picks_dir['state']!='disabled':
            entry_picks_dir.delete(0, tk.END)
            entry_picks_dir.insert(0, os.path.join("Cryolo", project, pick))
        if entry_coordinate_dir['state']!='disabled':
            entry_coordinate_dir.delete(0, tk.END)
            entry_coordinate_dir.insert(0, os.path.join("Cryolo", project, pick, "STAR"))
        if entry_mcfcoordinate_dir['state']!='disabled':
            entry_mcfcoordinate_dir.delete(0, tk.END)
            entry_mcfcoordinate_dir.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}"))
        if entry_splitcoordinate_dir['state']!='disabled':
            entry_splitcoordinate_dir.delete(0, tk.END)
            entry_splitcoordinate_dir.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}"))
        if entry_splitcoordinate_dir_step7['state']!='disabled':
            entry_splitcoordinate_dir_step7.delete(0, tk.END)
            entry_splitcoordinate_dir_step7.insert(0, os.path.join("Cryolo", project, "STAR", pick, f"MCF-{step}-{angle}-{seed}-{poly}",f"Split-{split}"))
        if entry_coordstosub['state']!='disabled':
            entry_coordstosub.delete(0, tk.END)
            entry_coordstosub.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}",f"Split-{split}"))
        if entry_splitcoordinate_step9['state']!='disabled':
            entry_splitcoordinate_step9.delete(0, tk.END)
            entry_splitcoordinate_step9.insert(0, os.path.join("Cryolo", project, pick, "STAR", f"MCF-{step}-{angle}-{seed}-{poly}",f"Split-{split}"))

    def thresh_focusout(eventthresh, num, threshold, project, pick, step, angle, seed, poly, split, entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9):
        if num == 1:
            entry_pickname.delete(0, tk.END)
            entry_pickname.insert(0, "allpicks_"+threshold.replace(".", "p"))
        elif num == 2:
            entry_pickname16.delete(0, tk.END)
            entry_pickname16.insert(0, "allpicks_"+threshold.replace(".", "p"))
        pickdir_focusout_forthreshchange(project, pick, step, angle, seed, poly, split, entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9)

    def pickdir_focusout_forthreshchange_complex(project, threshold, displayentry, mergeentry):
        displayentry.delete(0, tk.END)
        displayentry.insert(0, os.path.join("Cryolo", project, "allpicks_"+threshold.replace(".", "p")))
        if mergeentry['state']!='disabled':
            mergeentry.delete(0, tk.END)
            mergeentry.insert(0, os.path.join("Cryolo", project, "allpicks_"+threshold.replace(".", "p"), "STAR"))

    def thresh_focusout_complex(eventthresh, num, project, threshold, displayentry, mergeentry):
        if num == 1:
            entry_pickname_complex.delete(0, tk.END)
            entry_pickname_complex.insert(0, "allpicks_"+threshold.replace(".", "p"))
        elif num == 2:
            entry_pickname_complex24.delete(0, tk.END)
            entry_pickname_complex24.insert(0, "allpicks_"+threshold.replace(".", "p"))
        pickdir_focusout_forthreshchange_complex(project, threshold, displayentry, mergeentry)


    def pixelsizesearch_focusout(*args):

        try:

            pixelsize = float(entry_pixel_size_step8.get())

            new_start_value = str(int(57 * 1.1 / pixelsize))
            new_end_value = str(int(172 * 1.1 / pixelsize))

            if not updategui.get_update_flag("sub"):

                # Update the entry widgets with the new values
                entry_searchstart.delete(0, tk.END)
                entry_searchstart.insert(0, str(new_start_value))
                
                entry_searchend.delete(0, tk.END)
                entry_searchend.insert(0, str(new_end_value))

            if not updategui.get_update_flag("sub2"):

                entry_searchstart22.delete(0, tk.END)
                entry_searchstart22.insert(0, str(new_start_value))
                
                entry_searchend22.delete(0, tk.END)
                entry_searchend22.insert(0, str(new_end_value))

        except:

            return

    def pickdir_complex_focusout(eventpick, project, pick, fordisplay, formerge):

        fordisplay.delete(0, tk.END)
        fordisplay.insert(0, os.path.join("Cryolo", project, pick))
        formerge.delete(0, tk.END)
        formerge.insert(0, os.path.join("Cryolo", project, pick, "STAR"))

    ##############
    #Utils

    def count_mics(button, micdir):

        def counting_task():

            current = button.cget("text")

            button.config(text=f"{current} counting...", state="disabled")

            file_count = 0

            for root, dirs, files in os.walk(micdir):
                for file in files:
                    if file.endswith(".mrc") and not file.endswith("_PS.mrc"):
                        file_count += 1

            file_count = "{:,}".format(file_count)

            button.config(text=f"{file_count} micrographs", state="normal")

        # Create a new thread to run the counting task
        counting_thread = threading.Thread(target=counting_task)
        counting_thread.start()

    def count_movies(button, moviedir):

        def counting_task():

            current = button.cget("text")

            button.config(text=f"{current} counting...", state="disabled")

            mrc_count = 0
            eer_count = 0
            tif_count = 0
            tiff_count = 0

            mrc_count = len(glob.glob(os.path.join(moviedir, "**/*.mrc"), recursive=True))
            eer_count = len(glob.glob(os.path.join(moviedir, "**/*.eer"), recursive=True))
            tif_count = len(glob.glob(os.path.join(moviedir, "**/*.tif"), recursive=True))
            tiff_count = len(glob.glob(os.path.join(moviedir, "**/*.tiff"), recursive=True))

            if mrc_count+eer_count+tif_count+tiff_count == 0:
                button.config(text="#", state="normal")
                return

            if mrc_count != 0:
                mrc_text = "{:,}".format(mrc_count) + " mrc"
            if eer_count != 0:
                eer_text = "{:,}".format(eer_count) + " eer"
            if tif_count != 0:
                tif_text = "{:,}".format(tif_count) + " tif"
            if tiff_count != 0:
                tiff_text = "{:,}".format(tiff_count) + " tiff"

            final_text = ""

            if mrc_count != 0:
                final_text = mrc_text
            if eer_count != 0:
                if final_text:
                    final_text += ", " + eer_text
                else:
                    final_text = eer_text
            if tif_count != 0:
                if final_text:
                    final_text += ", " + tif_text
                else:
                    final_text = tif_text
            if tiff_count != 0:
                if final_text:
                    final_text += ", " + tiff_text
                else:
                    final_text = tiff_text


            button.config(text=f"{final_text} files", state="normal")

        # Create a new thread to run the counting task
        counting_thread = threading.Thread(target=counting_task)
        counting_thread.start()

    def count_corresponding_mics(button, micdir, pickdir, suffix):

        def counting_task():

            current = button.cget("text")

            button.config(text=f"{current} counting...", state="disabled")

            miclist = glob.glob(os.path.join(micdir, '*.mrc'))
            miclist = [os.path.basename(file) for file in miclist]

            picklist = glob.glob(os.path.join(pickdir, f'*{suffix}'))
            picklist = [os.path.basename(file) for file in picklist]

            miclist = [item for item in miclist if item.split(".mrc")[0] + suffix in picklist]

            totalpickedmics = len(miclist)

            totalpickedmics = "{:,}".format(totalpickedmics)

            button.config(text=f"{totalpickedmics} micrographs", state="normal")

        counting_thread = threading.Thread(target=counting_task)
        counting_thread.start()

    def count_picks(button, pickdir, suffix):

        def counting_task():

            current = button.cget("text")

            button.config(text=f"{current} counting...", state="disabled")

            totalpickedparts = 0

            picklist = glob.glob(os.path.join(pickdir, f'*{suffix}'))

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

            button.config(text=f"{totalpickedparts} picks", state="normal")

        counting_thread = threading.Thread(target=counting_task)
        counting_thread.start()


    # def count_corr(button):
    #     def counting_task():
    #         current = button.cget("text")
    #         button.config(text=f"{current} counting...", state="disabled")
    #         if not os.path.exists("MotionCorr/job002/corrected_micrographs.star"):
    #             button.config(text="#", state="normal")
    #         else:
    #             micstar_pd, metadata = fileparser.getparticles("MotionCorr/job002/corrected_micrographs.star")
    #             totalmics = len(micstar_pd.index)
    #             totalmics = "{:,}".format(totalmics)
    #             button.config(text=f"{totalmics} micrographs", state="normal")
    #     counting_thread = threading.Thread(target=counting_task)
    #     counting_thread.start()

    ##############
    #SAVE/LOAD

    def saveparams(paramsdict):

        current_directory = os.getcwd() 
        file_path = filedialog.asksaveasfilename(initialdir=current_directory)


        if file_path:

            def writeandshow(field, text):
                file.write(text)
                field.insert(tk.END, text)

            try:

                paramsdict["output_text_hq"].delete(1.0, tk.END)
                paramsdict["output_text_hq"].insert(tk.END, f"Saved {os.path.basename(file_path)}:\n")
                paramsdict["output_text_hq"].insert(tk.END, "--------------------------------------------------\n")

                with open(file_path, 'w') as file:
                    if paramsdict["doublesub_var"].get() == 1:
                        writeandshow(paramsdict["output_text_hq"], f"Double subtraction : yes\n")
                    else:
                        writeandshow(paramsdict["output_text_hq"], f"Double subtraction : no\n")
                    
                    if paramsdict["eer_var"].get() == 1:
                        writeandshow(paramsdict["output_text_hq"], f"EER : yes\n")
                    else:
                        writeandshow(paramsdict["output_text_hq"], f"EER : no\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Movies (before linking) : {paramsdict['entry_scopesourcemovies'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Movies (linked directory) : {paramsdict['entry_syncmovies'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Movies (EER) : {paramsdict['entry_eer_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"EER grouping (for conversion) : {paramsdict['entry_eergroups'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Movies (after EER conversion) : {paramsdict['entry_tif_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"EER-tif procs : {paramsdict['entry_eerprocs'].get()}\n")
                    
                    if paramsdict["convertgain_checkbox"].get() == 1:
                        writeandshow(paramsdict["output_text_hq"], f"Convert gain : yes\n")
                    else:
                        writeandshow(paramsdict["output_text_hq"], f"Convert gain : no\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Gain reference (to convert) : {paramsdict['entry_gainm1'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Movies : {paramsdict['entry_sourcemovies'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Gain reference : {paramsdict['entry_gain'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Optics group : {paramsdict['entry_optics'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (motioncorr) : {paramsdict['entry_pixelsize_corr'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Voltage : {paramsdict['entry_voltage'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Dose : {paramsdict['entry_dose'].get()}\n")
                    
                    if paramsdict["show_adv"]:
                        writeandshow(paramsdict["output_text_hq"], f"Show advanced : yes\n")
                    else:
                        writeandshow(paramsdict["output_text_hq"], f"Show advanced : no\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"EER grouping (for motion corr) : {paramsdict['entry_eergroups_corr'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Gain rotation : {paramsdict['entry_gainrot'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Gain flipping : {paramsdict['entry_gainflip'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"MTF : {paramsdict['entry_mtf'].get()}\n")
                    
                    if paramsdict["selected_linktype"].get() == "Relion":
                        writeandshow(paramsdict["output_text_hq"], f"Micrograph path type : Relion\n")
                    elif paramsdict["selected_linktype"].get() == "Elsewhere":
                        writeandshow(paramsdict["output_text_hq"], f"Micrograph path type : Elsewhere\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs to link : {paramsdict['entry_sourcemics'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs to link (elsewhere) : {paramsdict['entry_sourcemics_elsewhere'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Directory to link to : {paramsdict['entry_syncmics'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph suffix : {paramsdict['entry_suffix'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs (motion corrected) : {paramsdict['entry_corrmics'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs directory to pick : {paramsdict['entry_micrographs_topick'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (picking) : {paramsdict['entry_pixel_size'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo model : {paramsdict['entry_cryolo_model'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Threshold : {paramsdict['entry_threshold'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo subdirectory name : {paramsdict['entry_projectname'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo picking job name : {paramsdict['entry_pickname'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"GPU : {paramsdict['entry_gpu'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Subset : {paramsdict['entry_picksubset'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (picked) : {paramsdict['entry_pickedmics_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo picking directory : {paramsdict['entry_picks_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Display : {paramsdict['entry_todisplay_step3'].get()}\n")
                    
                    if paramsdict["selected_picktype"].get() == "STAR":
                        writeandshow(paramsdict["output_text_hq"], f"Filetype : STAR\n")
                    elif paramsdict["selected_picktype"].get() == "CBOX":
                        writeandshow(paramsdict["output_text_hq"], f"Filetype : CBOX\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo STAR output : {paramsdict['entry_coordinate_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph suffix (for MCF) : {paramsdict['entry_suffix_step4'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (MCF) : {paramsdict['entry_pixel_size_step4'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Step size (Å) : {paramsdict['entry_samplestep'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Max angle change per 4nm : {paramsdict['entry_anglechange'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Minimum to seed filament : {paramsdict['entry_minseed'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Polynomial : {paramsdict['entry_polynomial'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after MCF) : {paramsdict['entry_mcfedmics_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Fit directory : {paramsdict['entry_mcfcoordinate_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Fit STAR files : {paramsdict['entry_splitcoordinate_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Split value : {paramsdict['entry_splitvalue'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after split) : {paramsdict['entry_splitedmics_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Split directory : {paramsdict['entry_splitcoordinate_dir_step7'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs to subtract : {paramsdict['entry_mictosub_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Directory with split filaments : {paramsdict['entry_coordstosub'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Output directory : {paramsdict['entry_suboutput'].get()}\n")
                    
                    if paramsdict["selected_automask"].get() == "Auto":
                        writeandshow(paramsdict["output_text_hq"], f"Masking : Auto\n")
                    elif paramsdict["selected_automask"].get() == "Manual":
                        writeandshow(paramsdict["output_text_hq"], f"Masking : Manual\n")
                        writeandshow(paramsdict["output_text_hq"], f"Mask file : {paramsdict['entry_mask'].get()}\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (subtraction) : {paramsdict['entry_pixel_size_step8'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Search start : {paramsdict['entry_searchstart'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Search end : {paramsdict['entry_searchend'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after subtraction) : {paramsdict['entry_subtractedmics'].get()}\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after subtraction, to pick) : {paramsdict['entry_submicrographs_topick'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (complex picking) : {paramsdict['entry_pixel_size_subpick'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo model (complex picking) : {paramsdict['entry_cryolo_model_complex'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Threshold (complex picking) : {paramsdict['entry_threshold_complex'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo subdirectory name (complex picking) : {paramsdict['entry_projectname_complex'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo picking job name (complex picking) : {paramsdict['entry_pickname_complex'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"GPU (complex picking) : {paramsdict['entry_gpu_complex'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Subset (complex picking) : {paramsdict['entry_picksubset_complex'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs (complex picking) : {paramsdict['entry_complex_pickedmics_dir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Picked complexes : {paramsdict['entry_complex_picks_dir'].get()}\n")

                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory to pick #2 : {paramsdict['entry_micrographs_topick16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (picking) #2 : {paramsdict['entry_pixel_size16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo model #2 : {paramsdict['entry_cryolo_model16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Threshold #2 : {paramsdict['entry_threshold16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo subdirectory name #2 : {paramsdict['entry_projectname16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo picking job name #2 : {paramsdict['entry_pickname16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"GPU #2 : {paramsdict['entry_gpu16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Subset #2 : {paramsdict['entry_picksubset16'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (picked) #2 : {paramsdict['entry_pickedmics_dir17'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo picking directory #2 : {paramsdict['entry_picks_dir17'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo STAR output #2 : {paramsdict['entry_coordinate_dir18'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph suffix (for MCF) #2 : {paramsdict['entry_suffix_step18'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (MCF) #2 : {paramsdict['entry_pixel_size_step18'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Step size (Å) #2 : {paramsdict['entry_samplestep18'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Max angle change per 4nm #2 : {paramsdict['entry_anglechange18'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Minimum to seed filament #2 : {paramsdict['entry_minseed18'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Polynomial #2 : {paramsdict['entry_polynomial18'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after MCF) #2 : {paramsdict['entry_mcfedmics_dir19'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Fit directory #2 : {paramsdict['entry_mcfcoordinate_dir19'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Fit STAR files #2 : {paramsdict['entry_splitcoordinate_dir20'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Split value #2 : {paramsdict['entry_splitvalue20'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after split) #2 : {paramsdict['entry_splitedmics_dir21'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Split directory #2 : {paramsdict['entry_splitcoordinate_dir_step21'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs to subtract #2 : {paramsdict['entry_mictosub_dir22'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Directory with split filaments #2 : {paramsdict['entry_coordstosub22'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Output directory #2 : {paramsdict['entry_suboutput22'].get()}\n")
                    
                    if paramsdict["selected_automask22"].get() == "Auto":
                        writeandshow(paramsdict["output_text_hq"], f"Masking #2 : Auto\n")
                    elif paramsdict["selected_automask22"].get() == "Manual":
                        writeandshow(paramsdict["output_text_hq"], f"Masking #2 : Manual\n")
                        writeandshow(paramsdict["output_text_hq"], f"Mask file #2 : {paramsdict['entry_mask22'].get()}\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (subtraction) #2 : {paramsdict['entry_pixel_size_step22'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Search start #2 : {paramsdict['entry_searchstart22'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Search end #2 : {paramsdict['entry_searchend22'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after subtraction) #2 : {paramsdict['entry_subtractedmics23'].get()}\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph directory (after subtraction, to pick) #2 : {paramsdict['entry_submicrographs_topick24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Pixel size (complex picking) #2 : {paramsdict['entry_pixel_size_subpick24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo model (complex picking) #2 : {paramsdict['entry_cryolo_model_complex24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Threshold (complex picking) #2 : {paramsdict['entry_threshold_complex24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo subdirectory name (complex picking) #2 : {paramsdict['entry_projectname_complex24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryolo picking job name (complex picking) #2 : {paramsdict['entry_pickname_complex24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"GPU (complex picking) #2 : {paramsdict['entry_gpu_complex24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Subset (complex picking) #2 : {paramsdict['entry_picksubset_complex24'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrographs (complex picking) #2 : {paramsdict['entry_complex_pickedmics_dir25'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Picked complexes #2 : {paramsdict['entry_complex_picks_dir25'].get()}\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"First subtraction : {paramsdict['entry_firstsub'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Second subtraction : {paramsdict['entry_secondsub'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Merged output : {paramsdict['entry_outputsubmerge'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"First picks : {paramsdict['entry_firstpicks'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Second picks : {paramsdict['entry_secondpicks'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Merged picks : {paramsdict['entry_outputpickmerge'].get()}\n")
                    
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph star file : {paramsdict['entry_micstar'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Micrograph prefix : {paramsdict['entry_prefix'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Subtracted micrographs : {paramsdict['entry_submicsdir'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Output name : {paramsdict['entry_outstar'].get()}\n")

                    writeandshow(paramsdict["output_text_hq"], f"Particle coordinates : {paramsdict['entry_subcoords'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Subtracted micrograph star file : {paramsdict['entry_micstar11'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Extract box size : {paramsdict['entry_boxsize'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Extract rescaling : {paramsdict['entry_rescaledbox'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Import job : {paramsdict['entry_importjob'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc license : {paramsdict['entry_license'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc host : {paramsdict['entry_host'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc port : {paramsdict['entry_port'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc email : {paramsdict['entry_email'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc project : {paramsdict['entry_project'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc workspace name : {paramsdict['entry_workspacename'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc workspace UID : {paramsdict['entry_workspacenum'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Extracted particles : {paramsdict['entry_particles'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc volumes : {paramsdict['entry_importvols'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc heterogeneous : {paramsdict['entry_hetero'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc good class : {paramsdict['entry_goodclass'].get()}\n")
                    writeandshow(paramsdict["output_text_hq"], f"Cryosparc nonuniform job : {paramsdict['entry_convertjob'].get()}\n")

            except Exception as e:

                paramsdict["output_text_hq"].insert(tk.END, f"Could not save {file_path}: {str(e)}\n")

        if not os.path.exists("Subflow"):
            os.makedirs("Subflow")
        with open("Subflow/subflow-last.txt", 'w') as file:
            file.write(file_path)

    def browseload_params(paramsdict):

        try:

            current_directory = os.getcwd() 
            file_path = filedialog.askopenfilename(initialdir=current_directory)

            if not os.path.exists(file_path):
                return

            loadparams(paramsdict, file_path)

        except Exception as e:

            paramsdict["output_text_hq"].insert(tk.END, f"Could not load {file_path}: {str(e)}\n")

    def loadparams(paramsdict, file_path):

        global show_adv

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            pipeline_param, pipeline_value = line.split(" : ")
            pipeline_value = pipeline_value.strip("\n")

            if pipeline_param == "Double subtraction":
                if pipeline_value == "yes":
                    paramsdict["doublesub_var"].set(1)
                else:
                    paramsdict["doublesub_var"].set(0)
            elif pipeline_param == "EER":
                if pipeline_value == "yes":
                    paramsdict["eer_var"].set(1)
                else:
                    paramsdict["eer_var"].set(0)

            elif pipeline_param == "Movies (before linking)":
                paramsdict["entry_scopesourcemovies"].delete(0, tk.END)
                paramsdict["entry_scopesourcemovies"].insert(0, pipeline_value)
            elif pipeline_param == "Movies (linked directory)":
                paramsdict["entry_syncmovies"].delete(0, tk.END)
                paramsdict["entry_syncmovies"].insert(0, pipeline_value)
            elif pipeline_param == "Movies (EER)":
                paramsdict["entry_eer_dir"].delete(0, tk.END)
                paramsdict["entry_eer_dir"].insert(0, pipeline_value)
            elif pipeline_param == "EER grouping (for conversion)":
                paramsdict["entry_eergroups"].delete(0, tk.END)
                paramsdict["entry_eergroups"].insert(0, pipeline_value)
            elif pipeline_param == "Movies (after EER conversion)":
                paramsdict["entry_tif_dir"].delete(0, tk.END)
                paramsdict["entry_tif_dir"].insert(0, pipeline_value)
            elif pipeline_param == "EER-tif procs":
                paramsdict["entry_eerprocs"].delete(0, tk.END)
                paramsdict["entry_eerprocs"].insert(0, pipeline_value)
            elif pipeline_param == "Convert gain":
                if pipeline_value == "yes":
                    paramsdict["convertgain_checkbox"].set(1)
                else:
                    paramsdict["convertgain_checkbox"].set(0)
            elif pipeline_param == "Gain reference (to convert)":
                paramsdict["entry_gainm1"].delete(0, tk.END)
                paramsdict["entry_gainm1"].insert(0, pipeline_value)

            elif pipeline_param == "Movies":
                paramsdict["entry_sourcemovies"].delete(0, tk.END)
                paramsdict["entry_sourcemovies"].insert(0, pipeline_value)
            elif pipeline_param == "Gain reference":
                paramsdict["entry_gain"].delete(0, tk.END)
                paramsdict["entry_gain"].insert(0, pipeline_value)
            elif pipeline_param == "Optics group":
                paramsdict["entry_optics"].delete(0, tk.END)
                paramsdict["entry_optics"].insert(0, pipeline_value)
            elif pipeline_param == "Pixel size (motioncorr)":
                paramsdict["entry_pixelsize_corr"].delete(0, tk.END)
                paramsdict["entry_pixelsize_corr"].insert(0, pipeline_value)
            elif pipeline_param == "Voltage":
                paramsdict["entry_voltage"].delete(0, tk.END)
                paramsdict["entry_voltage"].insert(0, pipeline_value)
            elif pipeline_param == "Dose":
                paramsdict["entry_dose"].delete(0, tk.END)
                paramsdict["entry_dose"].insert(0, pipeline_value)
            elif pipeline_param == "Show advanced":
                if pipeline_value == "yes":
                    paramsdict["show_adv"] = True
                else:
                    paramsdict["show_adv"] = False
            elif pipeline_param == "EER grouping (for motion corr)":
                paramsdict["entry_eergroups_corr"].delete(0, tk.END)
                paramsdict["entry_eergroups_corr"].insert(0, pipeline_value)
            elif pipeline_param == "Gain rotation":
                paramsdict["entry_gainrot"].delete(0, tk.END)
                paramsdict["entry_gainrot"].insert(0, pipeline_value)
            elif pipeline_param == "Gain flipping":
                paramsdict["entry_gainflip"].delete(0, tk.END)
                paramsdict["entry_gainflip"].insert(0, pipeline_value)
            elif pipeline_param == "MTF":
                paramsdict["entry_mtf"].delete(0, tk.END)
                paramsdict["entry_mtf"].insert(0, pipeline_value)

            elif pipeline_param == "Micrograph path type":
                paramsdict["selected_linktype"].set(pipeline_value)
            elif pipeline_param == "Micrographs to link":
                paramsdict["entry_sourcemics"].delete(0, tk.END)
                paramsdict["entry_sourcemics"].insert(0, pipeline_value)           
            elif pipeline_param == "Micrographs to link (elsewhere)":
                paramsdict["entry_sourcemics_elsewhere"].delete(0, tk.END)
                paramsdict["entry_sourcemics_elsewhere"].insert(0, pipeline_value)
            elif pipeline_param ==  "Directory to link to":
                paramsdict["entry_syncmics"].delete(0, tk.END)
                paramsdict["entry_syncmics"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Micrograph suffix":
                paramsdict["entry_suffix"].delete(0, tk.END)
                paramsdict["entry_suffix"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Micrographs (motion corrected)":
                paramsdict["entry_corrmics"].delete(0, tk.END)
                paramsdict["entry_corrmics"].insert(0, pipeline_value) 

            elif pipeline_param ==  "Micrographs directory to pick":
                paramsdict["entry_micrographs_topick"].delete(0, tk.END)
                paramsdict["entry_micrographs_topick"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Pixel size (picking)":
                paramsdict["entry_pixel_size"].delete(0, tk.END)
                paramsdict["entry_pixel_size"].insert(0, pipeline_value)   
            elif pipeline_param ==  "Cryolo model":
                paramsdict["entry_cryolo_model"].delete(0, tk.END)
                paramsdict["entry_cryolo_model"].insert(0, pipeline_value)
            elif pipeline_param ==  "Threshold":
                paramsdict["entry_threshold"].delete(0, tk.END)
                paramsdict["entry_threshold"].insert(0, pipeline_value)   
            elif pipeline_param ==  "Cryolo subdirectory name":
                paramsdict["entry_projectname"].delete(0, tk.END)
                paramsdict["entry_projectname"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Cryolo picking job name":
                paramsdict["entry_pickname"].delete(0, tk.END)
                paramsdict["entry_pickname"].insert(0, pipeline_value)  
            elif pipeline_param ==  "GPU":
                paramsdict["entry_gpu"].delete(0, tk.END)
                paramsdict["entry_gpu"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Subset":
                paramsdict["entry_picksubset"].delete(0, tk.END)
                paramsdict["entry_picksubset"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Micrograph directory (picked)":
                paramsdict["entry_pickedmics_dir"].delete(0, tk.END)
                paramsdict["entry_pickedmics_dir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo picking directory":
                paramsdict["entry_picks_dir"].delete(0, tk.END)
                paramsdict["entry_picks_dir"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Display":
                paramsdict["entry_todisplay_step3"].delete(0, tk.END)
                paramsdict["entry_todisplay_step3"].insert(0, pipeline_value)
            elif pipeline_param ==  "Filetype":
                paramsdict["selected_picktype"].set(pipeline_value)
            elif pipeline_param ==  "Cryolo STAR output":
                paramsdict["entry_coordinate_dir"].delete(0, tk.END)
                paramsdict["entry_coordinate_dir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph suffix (for MCF)":
                paramsdict["entry_suffix_step4"].delete(0, tk.END)
                paramsdict["entry_suffix_step4"].insert(0, pipeline_value)
            elif pipeline_param ==  "Pixel size (MCF)":
                paramsdict["entry_pixel_size_step4"].delete(0, tk.END)
                paramsdict["entry_pixel_size_step4"].insert(0, pipeline_value)
            elif pipeline_param ==  "Step size (Å)":
                paramsdict["entry_samplestep"].delete(0, tk.END)
                paramsdict["entry_samplestep"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Max angle change per 4nm":
                paramsdict["entry_anglechange"].delete(0, tk.END)
                paramsdict["entry_anglechange"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Minimum to seed filament":
                paramsdict["entry_minseed"].delete(0, tk.END)
                paramsdict["entry_minseed"].insert(0, pipeline_value)
            elif pipeline_param ==  "Polynomial":
                paramsdict["entry_polynomial"].delete(0, tk.END)
                paramsdict["entry_polynomial"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph directory (after MCF)":
                paramsdict["entry_mcfedmics_dir"].delete(0, tk.END)
                paramsdict["entry_mcfedmics_dir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Fit directory":
                paramsdict["entry_mcfcoordinate_dir"].delete(0, tk.END)
                paramsdict["entry_mcfcoordinate_dir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Fit STAR files":
                paramsdict["entry_splitcoordinate_dir"].delete(0, tk.END)
                paramsdict["entry_splitcoordinate_dir"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Split value":
                paramsdict["entry_splitvalue"].delete(0, tk.END)
                paramsdict["entry_splitvalue"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph directory (after split)":
                paramsdict["entry_splitedmics_dir"].delete(0, tk.END)
                paramsdict["entry_splitedmics_dir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Split directory":
                paramsdict["entry_splitcoordinate_dir_step7"].delete(0, tk.END)
                paramsdict["entry_splitcoordinate_dir_step7"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrographs to subtract":
                paramsdict["entry_mictosub_dir"].delete(0, tk.END)
                paramsdict["entry_mictosub_dir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Directory with split filaments":
                paramsdict["entry_coordstosub"].delete(0, tk.END)
                paramsdict["entry_coordstosub"].insert(0, pipeline_value)
            elif pipeline_param ==  "Output directory":
                paramsdict["entry_suboutput"].delete(0, tk.END)
                paramsdict["entry_suboutput"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Masking":
                if pipeline_value == "Auto":
                    paramsdict["selected_automask"].set("Auto")
                    paramsdict["entry_mask"].config(state='disabled')
                    paramsdict["entry_pixel_size_step8"].config(state='normal')
                elif pipeline_value == "Manual":
                    paramsdict["selected_automask"].set("Manual")
                    paramsdict["entry_mask"].config(state='normal')
                    paramsdict["entry_pixel_size_step8"].config(state='disabled')
            elif pipeline_param ==  "Mask file":
                paramsdict["entry_mask"].delete(0, tk.END)
                paramsdict["entry_mask"].insert(0, pipeline_value) 
            elif pipeline_param == "Pixel size (subtraction)":
                paramsdict["entry_pixel_size_step8"].delete(0, tk.END)
                paramsdict["entry_pixel_size_step8"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Search start":
                paramsdict["entry_searchstart"].delete(0, tk.END)
                paramsdict["entry_searchstart"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Search end":
                paramsdict["entry_searchend"].delete(0, tk.END)
                paramsdict["entry_searchend"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph directory (after subtraction)":
                paramsdict["entry_subtractedmics"].delete(0, tk.END)
                paramsdict["entry_subtractedmics"].insert(0, pipeline_value)

            elif pipeline_param ==  "Micrograph directory (after subtraction, to pick)":
                paramsdict["entry_submicrographs_topick"].delete(0, tk.END)
                paramsdict["entry_submicrographs_topick"].insert(0, pipeline_value)
            elif pipeline_param ==  "Pixel size (complex picking)":
                paramsdict["entry_pixel_size_subpick"].delete(0, tk.END)
                paramsdict["entry_pixel_size_subpick"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo model (complex picking)":
                paramsdict["entry_cryolo_model_complex"].delete(0, tk.END)
                paramsdict["entry_cryolo_model_complex"].insert(0, pipeline_value)
            elif pipeline_param ==  "Threshold (complex picking)":
                paramsdict["entry_threshold_complex"].delete(0, tk.END)
                paramsdict["entry_threshold_complex"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo subdirectory name (complex picking)":
                paramsdict["entry_projectname_complex"].delete(0, tk.END)
                paramsdict["entry_projectname_complex"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo picking job name (complex picking)":
                paramsdict["entry_pickname_complex"].delete(0, tk.END)
                paramsdict["entry_pickname_complex"].insert(0, pipeline_value)
            elif pipeline_param ==  "GPU (complex picking)":
                paramsdict["entry_gpu_complex"].delete(0, tk.END)
                paramsdict["entry_gpu_complex"].insert(0, pipeline_value)
            elif pipeline_param ==  "Subset (complex picking)":
                paramsdict["entry_picksubset_complex"].delete(0, tk.END)
                paramsdict["entry_picksubset_complex"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrographs (complex picking)":
                paramsdict["entry_complex_pickedmics_dir"].delete(0, tk.END)
                paramsdict["entry_complex_pickedmics_dir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Picked complexes":
                paramsdict["entry_complex_picks_dir"].delete(0, tk.END)
                paramsdict["entry_complex_picks_dir"].insert(0, pipeline_value)

            #####

            elif pipeline_param ==  "Micrographs directory to pick #2":
                paramsdict["entry_micrographs_topick16"].delete(0, tk.END)
                paramsdict["entry_micrographs_topick16"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Pixel size (picking) #2":
                paramsdict["entry_pixel_size16"].delete(0, tk.END)
                paramsdict["entry_pixel_size16"].insert(0, pipeline_value)   
            elif pipeline_param ==  "Cryolo model #2":
                paramsdict["entry_cryolo_model16"].delete(0, tk.END)
                paramsdict["entry_cryolo_model16"].insert(0, pipeline_value)
            elif pipeline_param ==  "Threshold #2":
                paramsdict["entry_threshold16"].delete(0, tk.END)
                paramsdict["entry_threshold16"].insert(0, pipeline_value)   
            elif pipeline_param ==  "Cryolo subdirectory name #2":
                paramsdict["entry_projectname16"].delete(0, tk.END)
                paramsdict["entry_projectname16"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Cryolo picking job name #2":
                paramsdict["entry_pickname16"].delete(0, tk.END)
                paramsdict["entry_pickname16"].insert(0, pipeline_value)  
            elif pipeline_param ==  "GPU #2":
                paramsdict["entry_gpu16"].delete(0, tk.END)
                paramsdict["entry_gpu16"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Subset #2":
                paramsdict["entry_picksubset16"].delete(0, tk.END)
                paramsdict["entry_picksubset16"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Micrograph directory (picked) #2":
                paramsdict["entry_pickedmics_dir17"].delete(0, tk.END)
                paramsdict["entry_pickedmics_dir17"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo picking directory #2":
                paramsdict["entry_picks_dir17"].delete(0, tk.END)
                paramsdict["entry_picks_dir17"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Cryolo STAR output #2":
                paramsdict["entry_coordinate_dir18"].delete(0, tk.END)
                paramsdict["entry_coordinate_dir18"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph suffix (for MCF) #2":
                paramsdict["entry_suffix_step18"].delete(0, tk.END)
                paramsdict["entry_suffix_step18"].insert(0, pipeline_value)
            elif pipeline_param ==  "Pixel size (MCF) #2":
                paramsdict["entry_pixel_size_step18"].delete(0, tk.END)
                paramsdict["entry_pixel_size_step18"].insert(0, pipeline_value)
            elif pipeline_param ==  "Step size (Å) #2":
                paramsdict["entry_samplestep18"].delete(0, tk.END)
                paramsdict["entry_samplestep18"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Max angle change per 4nm #2":
                paramsdict["entry_anglechange18"].delete(0, tk.END)
                paramsdict["entry_anglechange18"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Minimum to seed filament #2":
                paramsdict["entry_minseed18"].delete(0, tk.END)
                paramsdict["entry_minseed18"].insert(0, pipeline_value)
            elif pipeline_param ==  "Polynomial #2":
                paramsdict["entry_polynomial18"].delete(0, tk.END)
                paramsdict["entry_polynomial18"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph directory (after MCF) #2":
                paramsdict["entry_mcfedmics_dir19"].delete(0, tk.END)
                paramsdict["entry_mcfedmics_dir19"].insert(0, pipeline_value)
            elif pipeline_param ==  "Fit directory #2":
                paramsdict["entry_mcfcoordinate_dir19"].delete(0, tk.END)
                paramsdict["entry_mcfcoordinate_dir19"].insert(0, pipeline_value)
            elif pipeline_param ==  "Fit STAR files #2":
                paramsdict["entry_splitcoordinate_dir20"].delete(0, tk.END)
                paramsdict["entry_splitcoordinate_dir20"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Split value #2":
                paramsdict["entry_splitvalue20"].delete(0, tk.END)
                paramsdict["entry_splitvalue20"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph directory (after split) #2":
                paramsdict["entry_splitedmics_dir21"].delete(0, tk.END)
                paramsdict["entry_splitedmics_dir21"].insert(0, pipeline_value)
            elif pipeline_param ==  "Split directory #2":
                paramsdict["entry_splitcoordinate_dir_step21"].delete(0, tk.END)
                paramsdict["entry_splitcoordinate_dir_step21"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrographs to subtract #2":
                paramsdict["entry_mictosub_dir22"].delete(0, tk.END)
                paramsdict["entry_mictosub_dir22"].insert(0, pipeline_value)
            elif pipeline_param ==  "Directory with split filaments #2":
                paramsdict["entry_coordstosub22"].delete(0, tk.END)
                paramsdict["entry_coordstosub22"].insert(0, pipeline_value)
            elif pipeline_param ==  "Output directory #2":
                paramsdict["entry_suboutput22"].delete(0, tk.END)
                paramsdict["entry_suboutput22"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Masking #2":
                if pipeline_value == "Auto":
                    paramsdict["selected_automask22"].set("Auto")
                    paramsdict["entry_mask22"].config(state='disabled')
                    paramsdict["entry_pixel_size_step22"].config(state='normal')
                elif pipeline_value == "Manual":
                    paramsdict["selected_automask22"].set("Manual")
                    paramsdict["entry_mask22"].config(state='normal')
                    paramsdict["entry_pixel_size_step22"].config(state='disabled')
            elif pipeline_param ==  "Mask file #2":
                paramsdict["entry_mask22"].delete(0, tk.END)
                paramsdict["entry_mask22"].insert(0, pipeline_value) 
            elif pipeline_param == "Pixel size (subtraction) #2":
                paramsdict["entry_pixel_size_step22"].delete(0, tk.END)
                paramsdict["entry_pixel_size_step22"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Search start #2":
                paramsdict["entry_searchstart22"].delete(0, tk.END)
                paramsdict["entry_searchstart22"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Search end #2":
                paramsdict["entry_searchend22"].delete(0, tk.END)
                paramsdict["entry_searchend22"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrograph directory (after subtraction) #2":
                paramsdict["entry_subtractedmics23"].delete(0, tk.END)
                paramsdict["entry_subtractedmics23"].insert(0, pipeline_value)

            elif pipeline_param ==  "Micrograph directory (after subtraction, to pick) #2":
                paramsdict["entry_submicrographs_topick24"].delete(0, tk.END)
                paramsdict["entry_submicrographs_topick24"].insert(0, pipeline_value)
            elif pipeline_param ==  "Pixel size (complex picking) #2":
                paramsdict["entry_pixel_size_subpick24"].delete(0, tk.END)
                paramsdict["entry_pixel_size_subpick24"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo model (complex picking) #2":
                paramsdict["entry_cryolo_model_complex24"].delete(0, tk.END)
                paramsdict["entry_cryolo_model_complex24"].insert(0, pipeline_value)
            elif pipeline_param ==  "Threshold (complex picking) #2":
                paramsdict["entry_threshold_complex24"].delete(0, tk.END)
                paramsdict["entry_threshold_complex24"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo subdirectory name (complex picking) #2":
                paramsdict["entry_projectname_complex24"].delete(0, tk.END)
                paramsdict["entry_projectname_complex24"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryolo picking job name (complex picking) #2":
                paramsdict["entry_pickname_complex24"].delete(0, tk.END)
                paramsdict["entry_pickname_complex24"].insert(0, pipeline_value)
            elif pipeline_param ==  "GPU (complex picking) #2":
                paramsdict["entry_gpu_complex24"].delete(0, tk.END)
                paramsdict["entry_gpu_complex24"].insert(0, pipeline_value)
            elif pipeline_param ==  "Subset (complex picking) #2":
                paramsdict["entry_picksubset_complex24"].delete(0, tk.END)
                paramsdict["entry_picksubset_complex24"].insert(0, pipeline_value)
            elif pipeline_param ==  "Micrographs (complex picking) #2":
                paramsdict["entry_complex_pickedmics_dir25"].delete(0, tk.END)
                paramsdict["entry_complex_pickedmics_dir25"].insert(0, pipeline_value)
            elif pipeline_param ==  "Picked complexes #2":
                paramsdict["entry_complex_picks_dir25"].delete(0, tk.END)
                paramsdict["entry_complex_picks_dir25"].insert(0, pipeline_value)

            elif pipeline_param ==  "First subtraction":
                paramsdict["entry_firstsub"].delete(0, tk.END)
                paramsdict["entry_firstsub"].insert(0, pipeline_value)
            elif pipeline_param ==  "Second subtraction":
                paramsdict["entry_secondsub"].delete(0, tk.END)
                paramsdict["entry_secondsub"].insert(0, pipeline_value)
            elif pipeline_param ==  "Merged output":
                paramsdict["entry_outputsubmerge"].delete(0, tk.END)
                paramsdict["entry_outputsubmerge"].insert(0, pipeline_value)
            elif pipeline_param ==  "First picks":
                paramsdict["entry_firstpicks"].delete(0, tk.END)
                paramsdict["entry_firstpicks"].insert(0, pipeline_value)
            elif pipeline_param ==  "Second picks":
                paramsdict["entry_secondpicks"].delete(0, tk.END)
                paramsdict["entry_secondpicks"].insert(0, pipeline_value)
            elif pipeline_param ==  "Merged picks":
                paramsdict["entry_outputpickmerge"].delete(0, tk.END)
                paramsdict["entry_outputpickmerge"].insert(0, pipeline_value)

            #####


            elif pipeline_param ==  "Micrograph star file":
                paramsdict["entry_micstar"].delete(0, tk.END)
                paramsdict["entry_micstar"].insert(0, pipeline_value) 
            elif pipeline_param ==  "Micrograph prefix":
                paramsdict["entry_prefix"].delete(0, tk.END)
                paramsdict["entry_prefix"].insert(0, pipeline_value)
            elif pipeline_param ==  "Subtracted micrographs":
                paramsdict["entry_submicsdir"].delete(0, tk.END)
                paramsdict["entry_submicsdir"].insert(0, pipeline_value)
            elif pipeline_param ==  "Output name":
                paramsdict["entry_outstar"].delete(0, tk.END)
                paramsdict["entry_outstar"].insert(0, pipeline_value)

            ####

            elif pipeline_param ==  "Particle coordinates":
                paramsdict["entry_subcoords"].delete(0, tk.END)
                paramsdict["entry_subcoords"].insert(0, pipeline_value)
            elif pipeline_param ==  "Subtracted micrograph star file":
                paramsdict["entry_micstar11"].delete(0, tk.END)
                paramsdict["entry_micstar11"].insert(0, pipeline_value)
            elif pipeline_param ==  "Extract box size":
                paramsdict["entry_boxsize"].delete(0, tk.END)
                paramsdict["entry_boxsize"].insert(0, pipeline_value)
            elif pipeline_param ==  "Extract rescaling":
                paramsdict["entry_rescaledbox"].delete(0, tk.END)
                paramsdict["entry_rescaledbox"].insert(0, pipeline_value)
            elif pipeline_param ==  "Import job":
                paramsdict["entry_importjob"].delete(0, tk.END)
                paramsdict["entry_importjob"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc license":
                paramsdict["entry_license"].delete(0, tk.END)
                paramsdict["entry_license"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc host":
                paramsdict["entry_host"].delete(0, tk.END)
                paramsdict["entry_host"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc port":
                paramsdict["entry_port"].delete(0, tk.END)
                paramsdict["entry_port"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc email":
                paramsdict["entry_email"].delete(0, tk.END)
                paramsdict["entry_email"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc project":
                paramsdict["entry_project"].delete(0, tk.END)
                paramsdict["entry_project"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc workspace name":
                paramsdict["entry_workspacename"].delete(0, tk.END)
                paramsdict["entry_workspacename"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc workspace UID":
                paramsdict["entry_workspacenum"].delete(0, tk.END)
                paramsdict["entry_workspacenum"].insert(0, pipeline_value)
            elif pipeline_param ==  "Extracted particles":
                paramsdict["entry_particles"].delete(0, tk.END)
                paramsdict["entry_particles"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc volumes":
                paramsdict["entry_importvols"].delete(0, tk.END)
                paramsdict["entry_importvols"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc heterogeneous":
                paramsdict["entry_hetero"].delete(0, tk.END)
                paramsdict["entry_hetero"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc good class":
                paramsdict["entry_goodclass"].delete(0, tk.END)
                paramsdict["entry_goodclass"].insert(0, pipeline_value)
            elif pipeline_param ==  "Cryosparc nonuniform job":
                paramsdict["entry_convertjob"].delete(0, tk.END)
                paramsdict["entry_convertjob"].insert(0, pipeline_value)


        toggle_ui()

        paramsdict["output_text_hq"].delete(1.0, tk.END)
        paramsdict["output_text_hq"].insert(tk.END, f"Loaded {os.path.basename(file_path)}:\n")
        paramsdict["output_text_hq"].insert(tk.END, "--------------------------------------------------\n")
        for line in lines:
            paramsdict["output_text_hq"].insert(tk.END, line)

        if not os.path.exists("Subflow"):
            os.makedirs("Subflow")
        with open("Subflow/subflow-last.txt", 'w') as file:
            file.write(file_path)

    ##############
    #TABS

    t = 1
    notebook.tab(t, text=flagmap["linkmov"]["titles"][0])

    if len(tabs) > t:

        label_stepm2 = ttk.Label(tabs[t], text="Link movies", style="title.TLabel")
        label_stepm2.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_scopesourcemovies = ttk.Label(tabs[t], text="GridSquares or movies (wildcard)")
        label_scopesourcemovies.grid(row=1, column=0, padx=10, pady=3, sticky="e")

        entry_scopesourcemovies = ttk.Entry(tabs[t], font=common_font)
        entry_scopesourcemovies.insert(0, "/path/to/Images-Disc1/Grid*")
        entry_scopesourcemovies.grid(row=1, column=1, padx=10, pady=3, sticky="ew")

        browse_button_scopesourcemovies = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_scopesourcemovies))
        browse_button_scopesourcemovies.grid(row=1, column=2, padx=10, pady=3)

        label_syncmovies = ttk.Label(tabs[t], text="Directory to link to")
        label_syncmovies.grid(row=2, column=0, padx=10, pady=3, sticky="e")

        entry_syncmovies = ttk.Entry(tabs[t], textvariable=typedmovies, font=common_font)
        entry_syncmovies.insert(0, globalmovies)
        entry_syncmovies.grid(row=2, column=1, padx=10, pady=3, sticky="ew")

        # label_suffix = ttk.Label(tabs[t], text="Micrograph suffix")
        # label_suffix.grid(row=3, column=0, padx=10, pady=3, sticky="e")

        # entry_suffix = ttk.Entry(tabs[t], textvariable=typedsuffix, font=common_font)
        # entry_suffix.insert(0, globalsuffix)
        # entry_suffix.grid(row=3, column=1, padx=10, pady=3, sticky="ew")

        moviesync_button = ttk.Button(tabs[t], text="Link", command=lambda: syncmovies(entry_scopesourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_scopesourcemovies, notebook))
        moviesync_button.grid(row=3, column=0, padx=10, pady=3, sticky="e")

        stop_moviesync_button = ttk.Button(tabs[t], text="Stop", command=lambda: stop_syncmovies(entry_scopesourcemovies, entry_syncmovies, output_text_stepm2, moviesync_button, stop_moviesync_button, browse_button_scopesourcemovies))
        stop_moviesync_button.grid(row=3, column=1, padx=10, pady=3, sticky="w")

        output_text_stepm2 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_stepm2.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_stepm2.config(highlightthickness=1, highlightbackground="grey")

        scrollbarm2 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_stepm2.config(yscrollcommand=scrollbarm2.set)
        scrollbarm2.config(command=output_text_stepm2.yview)
        scrollbarm2.grid(row=4, column=2, rowspan=1, sticky="ns")

        count_movielinks_button = ttk.Button(tabs[t], text="#", command=lambda: count_movies(count_movielinks_button, entry_syncmovies.get()))
        count_movielinks_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        # Allow the last row (output_text) to expand when resizing
        tabs[t].grid_rowconfigure(4, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["eertotif"]["titles"][0])

    if len(tabs) > t:

        label_stepm1 = ttk.Label(tabs[t], text="Convert EER to tif", style="title.TLabel")
        label_stepm1.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_eer_dir = ttk.Label(tabs[t], text="EER files (wildcard)")
        label_eer_dir.grid(row=1, column=0, padx=10, pady=3, sticky="e")

        entry_eer_dir = ttk.Entry(tabs[t], font=common_font)
        entry_eer_dir.insert(0, "EER/GridSquare*/Data/*EER.eer")
        entry_eer_dir.grid(row=1, column=1, padx=10, pady=3, sticky="ew")

        # browse_eer_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_eer_dir))
        # browse_eer_dir.grid(row=1, column=2, padx=10, pady=3)

        label_eergroups = ttk.Label(tabs[t], text="EER grouping")
        label_eergroups.grid(row=2, column=0, padx=10, pady=3, sticky="e")

        entry_eergroups = ttk.Entry(tabs[t], font=common_font)
        entry_eergroups.insert(0, "34")
        entry_eergroups.grid(row=2, column=1, padx=10, pady=3, sticky="ew")

        label_tif_dir = ttk.Label(tabs[t], text="Output directory")
        label_tif_dir.grid(row=3, column=0, padx=10, pady=3, sticky="e")

        entry_tif_dir = ttk.Entry(tabs[t], font=common_font)
        entry_tif_dir.insert(0, "Movies")
        entry_tif_dir.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        browse_tif_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_tif_dir))
        browse_tif_dir.grid(row=3, column=2, padx=10, pady=3)

        label_eerprocs = ttk.Label(tabs[t], text="MPI processes")
        label_eerprocs.grid(row=4, column=0, padx=10, pady=3, sticky="e")

        entry_eerprocs = ttk.Entry(tabs[t], font=common_font)
        entry_eerprocs.insert(0, "4")
        entry_eerprocs.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        convertgain_checkbox = tk.IntVar()

        label_checkboxm1 = ttk.Label(tabs[t], text="Convert gain reference?")
        label_checkboxm1.grid(row=5, column=0, padx=10, pady=3, sticky="e")

        checkboxm1 = tk.Checkbutton(tabs[t], variable=convertgain_checkbox,command=toggle_ui)
        checkboxm1.grid(row=5, column=1, padx=10, pady=3, sticky="w")

        label_gainm1 = ttk.Label(tabs[t], text="Gain reference")
        label_gainm1.grid(row=6, column=0, padx=10, pady=3, sticky="e")

        entry_gainm1 = ttk.Entry(tabs[t], font=common_font)
        #entry_gainm1.insert(0, "")
        entry_gainm1.grid(row=6, column=1, padx=10, pady=3, sticky="ew")  

        browse_button_gainm1 = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_gainm1))
        browse_button_gainm1.grid(row=6, column=2, padx=10, pady=3)

        eertif_button = ttk.Button(tabs[t], text="Convert", command=lambda: eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button, notebook))
        eertif_button.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        stop_eertif_button = ttk.Button(tabs[t], text="Stop", command=lambda: stop_eertif(output_text_stepm1, entry_eer_dir, entry_eergroups, entry_tif_dir, browse_tif_dir, entry_eerprocs, convertgain_checkbox, checkboxm1, entry_gainm1, eertif_button, browse_button_gainm1, stop_eertif_button))
        stop_eertif_button.grid(row=7, column=1, padx=10, pady=3, sticky="w")

        output_text_stepm1 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_stepm1.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_stepm1.config(highlightthickness=1, highlightbackground="grey")

        scrollbarm1 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_stepm1.config(yscrollcommand=scrollbarm1.set)
        scrollbarm1.config(command=output_text_stepm1.yview)
        scrollbarm1.grid(row=8, column=2, rowspan=1, sticky="ns")

        count_tifs_button = ttk.Button(tabs[t], text="#", command=lambda: count_movies(count_tifs_button, entry_tif_dir.get()))
        count_tifs_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(8, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["preprocess"]["titles"][0])

    if len(tabs) > t:

        label_step0 = ttk.Label(tabs[t], text="Import, Motion correct, CTF estimate", style="title.TLabel")
        label_step0.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        # label2_step0 = ttk.Label(tabs[t], text="Make sure no Relion pipeline exists already")
        # label2_step0.grid(row=1, column=0, columnspan=2, padx=10, pady=3)

        label_sourcemovies = ttk.Label(tabs[t], text="Movies (wildcard)")
        label_sourcemovies.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_sourcemovies = ttk.Entry(tabs[t], font=common_font)
        entry_sourcemovies.insert(0, "Movies/GridSquare*/Data/*_fractions.tiff") 
        entry_sourcemovies.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        # browse_button_sourcemovies = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_sourcemovies))
        # browse_button_sourcemovies.grid(row=2, column=2, padx=10, pady=2)

        label_sourcemics = ttk.Label(tabs[t], text="Gain reference")
        label_sourcemics.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_gain = ttk.Entry(tabs[t], font=common_font)
        entry_gain.insert(0, "GainReference/gain-reference.tiff")
        entry_gain.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_gain = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_gain))
        browse_button_gain.grid(row=2, column=2, padx=10, pady=2)

        label_optics = ttk.Label(tabs[t], text="Optics group name")
        label_optics.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_optics = ttk.Entry(tabs[t], font=common_font)
        try:
            entry_optics.insert(0, datetime.now().strftime("%y%m%d"))
        except:
            entry_optics.insert(0, "OpticsGroup1")
        entry_optics.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_pixelsize_corr = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixelsize_corr.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_pixelsize_corr = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        entry_pixelsize_corr.insert(0, globalpixelsize)
        entry_pixelsize_corr.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_voltage = ttk.Label(tabs[t], text="Voltage (kV)")
        label_voltage.grid(row=5, column=0, padx=10, pady=2, sticky="e")

        entry_voltage = ttk.Entry(tabs[t], font=common_font)
        entry_voltage.insert(0, "300")
        entry_voltage.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        label_dose = ttk.Label(tabs[t], text="Dose per frame (e⁻/Å²)")
        label_dose.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_dose = ttk.Entry(tabs[t], font=common_font)
        entry_dose.insert(0, "1")
        entry_dose.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        adv_button = ttk.Button(tabs[t], text="↓", command=toggle_adv)
        adv_button.grid(row=11, column=2, padx=10, pady=2, sticky="e")

        label_eergroups_corr = ttk.Label(tabs[t], text="EER grouping (if applicable)")
        label_eergroups_corr.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_eergroups_corr = ttk.Entry(tabs[t], font=common_font)
        entry_eergroups_corr.insert(0, "")
        entry_eergroups_corr.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_gainrot = ttk.Label(tabs[t], text="Gain rotation (90, 180, 270)")
        label_gainrot.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_gainrot = ttk.Entry(tabs[t], font=common_font)
        entry_gainrot.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        label_gainflip = ttk.Label(tabs[t], text="Gain flip (up-down, left-right)")
        label_gainflip.grid(row=9, column=0, padx=10, pady=2, sticky="e")

        entry_gainflip = ttk.Entry(tabs[t], font=common_font)
        entry_gainflip.grid(row=9, column=1, padx=10, pady=2, sticky="ew")

        label_mtf = ttk.Label(tabs[t], text="MTF")
        label_mtf.grid(row=10, column=0, padx=10, pady=2, sticky="e")

        entry_mtf = ttk.Entry(tabs[t], font=common_font)
        entry_mtf.grid(row=10, column=1, padx=10, pady=2, sticky="ew")

        browse_button_mtf = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_mtf))
        browse_button_mtf.grid(row=10, column=2, padx=10, pady=2)

        #########

        corr_button = ttk.Button(tabs[t], text="Preprocess", command=lambda: corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain, notebook))
        corr_button.grid(row=11, column=0, padx=10, pady=5, sticky="e")

        stop_corr_button = ttk.Button(tabs[t], text="Stop", command=lambda: stop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain))
        stop_corr_button.grid(row=11, column=1, padx=10, pady=5, sticky="w")

        forcestop_corr_button = ttk.Button(tabs[t], text="Force Stop", command=lambda: forcestop_corr(output_text_step0, output_text_step0b, output_text_step0c, entry_sourcemovies, entry_gain, entry_optics, entry_pixelsize_corr, entry_voltage, entry_dose, entry_eergroups_corr, entry_gainrot, entry_gainflip, entry_mtf, corr_button, stop_corr_button, browse_button_gain))
        forcestop_corr_button.grid(row=11, column=1, padx=10, pady=5, sticky="e")

        ######

        label_schemer = ttk.Label(tabs[t], text="Schemer output:", font=output_font)
        label_schemer.grid(row=12, column=0, padx=10, pady=2, sticky="w")

        output_text_step0 = tk.Text(tabs[t], height=2, width=40, font=output_font)
        output_text_step0.grid(row=13, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        output_text_step0.config(highlightthickness=1, highlightbackground="grey")

        scrollbar0 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step0.config(yscrollcommand=scrollbar0.set)
        scrollbar0.config(command=output_text_step0.yview)
        scrollbar0.grid(row=13, column=2, rowspan=1, sticky="ns")


        label_monitor = ttk.Label(tabs[t], text="Preprocessing output:", font=output_font)
        label_monitor.grid(row=14, column=0, padx=10, pady=2, sticky="w")

        output_text_step0b = tk.Text(tabs[t], height=8, width=40, font=output_font)
        output_text_step0b.grid(row=15, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        output_text_step0b.config(highlightthickness=1, highlightbackground="grey")

        scrollbar0b = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step0b.config(yscrollcommand=scrollbar0b.set)
        scrollbar0b.config(command=output_text_step0b.yview)
        scrollbar0b.grid(row=15, column=2, rowspan=1, sticky="ns")


        label_monitorerr = ttk.Label(tabs[t], text="Preprocessing errors:", font=output_font)
        label_monitorerr.grid(row=16, column=0, padx=10, pady=2, sticky="w")

        output_text_step0c = tk.Text(tabs[t], height=2, width=40, font=output_font)
        output_text_step0c.grid(row=17, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        output_text_step0c.config(highlightthickness=1, highlightbackground="grey")

        scrollbar0c = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step0c.config(yscrollcommand=scrollbar0c.set)
        scrollbar0c.config(command=output_text_step0c.yview)
        scrollbar0c.grid(row=17, column=2, rowspan=1, sticky="ns")

        count_corrs_button = ttk.Button(tabs[t], text="#", command=lambda: count_mics(count_corrs_button, "MotionCorr/job002"))
        count_corrs_button.grid(row=18, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        # Allow the last row (output_text) to expand when resizing
        tabs[t].grid_rowconfigure(13, weight=1)
        tabs[t].grid_rowconfigure(15, weight=1)
        tabs[t].grid_rowconfigure(17, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["linkcorr"]["titles"][0])

    if len(tabs) > t:

        label_step1 = ttk.Label(tabs[t], text="Link micrographs", style="title.TLabel")
        label_step1.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        # label_linktype = ttk.Label(tabs[t], text="Location:")
        # label_linktype.grid(row=1, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_linktype = tk.StringVar(value="Relion")

        radio_option_linktype_corr = ttk.Radiobutton(tabs[t], text="Relion motion corr job", variable=selected_linktype, value="Relion", command=toggle_ui)
        radio_option_linktype_corr.grid(row=1, column=0, padx=5, pady=2, sticky="e")

        radio_option_linktype_other = ttk.Radiobutton(tabs[t], text="Elsewhere (wildcard)", variable=selected_linktype, value="Elsewhere", command=toggle_ui)
        radio_option_linktype_other.grid(row=1, column=1, padx=5, pady=2, sticky="w") 

        label_sourcemics = ttk.Label(tabs[t], text="Motion correction job")
        label_sourcemics.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_sourcemics = ttk.Entry(tabs[t], textvariable=typedcorrmics, font=common_font)
        entry_sourcemics.insert(0, globalcorrmics)
        entry_sourcemics.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_sourcemics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_sourcemics))
        browse_button_sourcemics.grid(row=2, column=2, padx=10, pady=2)

        label_sourcemics_elsewhere = ttk.Label(tabs[t], text="Micrograph location")
        label_sourcemics_elsewhere.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_sourcemics_elsewhere = ttk.Entry(tabs[t], font=common_font)
        entry_sourcemics_elsewhere.insert(0, "/path/to/Grid*/Data/*_fractions.mrc")
        entry_sourcemics_elsewhere.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        label_suffix = ttk.Label(tabs[t], text="Micrograph suffix")
        label_suffix.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_suffix = ttk.Entry(tabs[t], textvariable=typedsuffix, font=common_font)
        entry_suffix.insert(0, globalsuffix)
        entry_suffix.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_syncmics = ttk.Label(tabs[t], text="Directory to link to")
        label_syncmics.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_syncmics = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        entry_syncmics.insert(0, globalmicrographs)
        entry_syncmics.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        sync_button = ttk.Button(tabs[t], text="Link", command=lambda: sync(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere, notebook))
        sync_button.grid(row=5, column=0, padx=10, pady=5, sticky="e")

        stop_sync_button = ttk.Button(tabs[t], text="Stop", command=lambda: stop_sync(entry_sourcemics, entry_syncmics, entry_suffix, output_text_step1, sync_button, stop_sync_button, browse_button_sourcemics, selected_linktype, radio_option_linktype_corr, radio_option_linktype_other, entry_sourcemics_elsewhere))
        stop_sync_button.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        output_text_step1 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step1.grid(row=6, column=0, columnspan=2, padx=10, pady=3, sticky="nsew")
        output_text_step1.config(highlightthickness=1, highlightbackground="grey")

        scrollbar1 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step1.config(yscrollcommand=scrollbar1.set)
        scrollbar1.config(command=output_text_step1.yview)
        scrollbar1.grid(row=6, column=2, rowspan=1, sticky="ns")

        count_miclinks_button = ttk.Button(tabs[t], text="#", command=lambda: count_mics(count_miclinks_button, entry_syncmics.get()))
        count_miclinks_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        # Allow the last row (output_text) to expand when resizing
        tabs[t].grid_rowconfigure(6, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step0d = ttk.Label(tabs[t], text="Display the micrographs", style="title.TLabel")
        label_step0d.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_corrmics = ttk.Label(tabs[t], text="Micrograph directory")
        label_corrmics.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_corrmics = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        #entry_corrmics.insert(0, globalmicrographs)
        entry_corrmics.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_corrmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_corrmics))
        browse_button_corrmics.grid(row=1, column=2, padx=10, pady=2)

        # label_corrsuffix = ttk.Label(tabs[t], text="Micrograph suffix")
        # label_corrsuffix.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        # entry_corrsuffix = ttk.Entry(tabs[t], textvariable=typedsuffix, font=common_font)
        # entry_corrsuffix.insert(0, globalsuffix)
        # entry_corrsuffix.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        label_todisplay_step0d = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step0d.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step0d = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        entry_todisplay_step0d.insert(0, globalnumdisplay)
        entry_todisplay_step0d.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_order0d = ttk.Label(tabs[t], text="Order:")
        label_order0d.grid(row=5, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step0d = tk.StringVar(value="First")

        radio_option_first_step0d = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step0d, value="First")
        radio_option_first_step0d.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step0d = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step0d, value="Last")
        radio_option_last_step0d.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step0d = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step0d, value="Random")
        radio_option_random_step0d.grid(row=7, column=1, padx=5, pady=2, sticky="w") 

        filter_checkbox = tk.IntVar(value=1)

        label_filterflag = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag.grid(row=8, column=0, padx=10, pady=3, sticky="e")

        filter_checkbox_button = tk.Checkbutton(tabs[t], variable=filter_checkbox)
        filter_checkbox_button.grid(row=8, column=1, padx=10, pady=3, sticky="w")

        display_corrmics_button = ttk.Button(tabs[t], text="Display", command=lambda: displaycorr(output_text_step0d, entry_corrmics, entry_todisplay_step0d, selected_order_step0d, filter_checkbox))
        display_corrmics_button.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

        output_text_step0d = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step0d.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step0d.config(highlightthickness=1, highlightbackground="grey")

        scrollbar0d = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step0d.config(yscrollcommand=scrollbar0d.set)
        scrollbar0d.config(command=output_text_step0d.yview)
        scrollbar0d.grid(row=10, column=2, rowspan=1, sticky="ns")

        # count_corrs_button_disp = ttk.Button(tabs[t], text="#", command=lambda: count_mics(count_corrs_button_disp, entry_corrmics.get()))
        # count_corrs_button_disp.grid(row=10, column=0, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["pickfil"]["titles"][0])

    if len(tabs) > t:

        label_step2 = ttk.Label(tabs[t], text="Pick with Cryolo", style="title.TLabel")
        label_step2.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_micrographs_topick = ttk.Label(tabs[t], text="Directory to pick")
        label_micrographs_topick.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_micrographs_topick = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        #entry_micrographs_topick.insert(0, "Micrographs")
        entry_micrographs_topick.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_micrographs_topick = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_micrographs_topick))
        browse_button_micrographs_topick.grid(row=1, column=2, padx=10, pady=2)

        label_pixel_size = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        #entry_pixel_size.insert(0, globalpixelsize)
        entry_pixel_size.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        label_cryolo_model = ttk.Label(tabs[t], text="Cryolo model")
        label_cryolo_model.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_cryolo_model = ttk.Entry(tabs[t], font=common_font)
        entry_cryolo_model.insert(0, "/cephfs/chaaban/CryoloModels/MTs/201028_model_K3_1p11apix.h5")
        entry_cryolo_model.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        browse_button_cryolo_model = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_cryolo_model))
        browse_button_cryolo_model.grid(row=3, column=2, padx=10, pady=2)

        label_threshold = ttk.Label(tabs[t], text="Threshold")
        label_threshold.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_threshold = ttk.Entry(tabs[t], font=common_font)
        entry_threshold.insert(0, "0.2")
        entry_threshold.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_projectname = ttk.Label(tabs[t], text="Cryolo subdirectory")
        label_projectname.grid(row=5, column=0, padx=10, pady=2, sticky="e")

        entry_projectname = ttk.Entry(tabs[t], font=common_font)
        entry_projectname.insert(0, "MTs")
        entry_projectname.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        label_pickname = ttk.Label(tabs[t], text="Picking job name")
        label_pickname.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_pickname = ttk.Entry(tabs[t], font=common_font)
        entry_pickname.insert(0, "allpicks_0p2")
        entry_pickname.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        label_gpu = ttk.Label(tabs[t], text="GPU (space-separated)")
        label_gpu.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_gpu = ttk.Entry(tabs[t], font=common_font)
        entry_gpu.insert(0, "0")
        entry_gpu.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_picksubset = ttk.Label(tabs[t], text="Subset")
        label_picksubset.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_picksubset = ttk.Entry(tabs[t], font=common_font)
        entry_picksubset.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        output_text_step2 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step2.grid(row=10, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step2.config(highlightthickness=1, highlightbackground="grey")

        pick_operation_fil = CryoloPickOperation()

        pick_button = ttk.Button(tabs[t], text="Pick", command=lambda: pick_operation_fil.pick(output_text_step2, 253, entry_micrographs_topick, entry_pixel_size, entry_cryolo_model, entry_threshold, entry_projectname, entry_pickname, entry_gpu, pick_button, stop_pick_button, browse_button_micrographs_topick, browse_button_cryolo_model, entry_picksubset,resetpicks_button, notebook, "pickfil"))
        pick_button.grid(row=9, column=0, padx=10, pady=5, sticky="e")

        stop_pick_button = ttk.Button(tabs[t], text="Stop", command=lambda: pick_operation_fil.stop_pick(output_text_step2))
        stop_pick_button.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        resetpicks_button = ttk.Button(tabs[t], text="Reset", command=lambda: reset_picks(resetpicks_button,os.path.join("Cryolo", entry_projectname.get(), entry_pickname.get())))
        resetpicks_button.grid(row=9, column=1, padx=10, pady=5, sticky="e")

        scrollbar2 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step2.config(yscrollcommand=scrollbar2.set)
        scrollbar2.config(command=output_text_step2.yview)
        scrollbar2.grid(row=10, column=2, rowspan=1, sticky="ns")

        count_filpicks_button = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_filpicks_button,
            entry_micrographs_topick.get(),
            os.path.join("Cryolo", entry_projectname.get(),entry_pickname.get(),"STAR"),
            ".star"))
        count_filpicks_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step3 = ttk.Label(tabs[t], text="Display the Cryolo picks", style="title.TLabel")
        label_step3.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_pickedmics_dir = ttk.Label(tabs[t], text="Micrograph directory")
        label_pickedmics_dir.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_pickedmics_dir = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        #entry_pickedmics_dir.insert(0, "Micrographs")
        entry_pickedmics_dir.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_pickedmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_pickedmics_dir))
        browse_button_pickedmics.grid(row=1, column=2, padx=10, pady=2)

        label_picks_dir = ttk.Label(tabs[t], text="Cryolo picking directory")
        label_picks_dir.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_picks_dir = ttk.Entry(tabs[t], font=common_font)
        entry_picks_dir.insert(0, "Cryolo/MTs/allpicks_0p2")
        entry_picks_dir.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_picks_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_picks_dir))
        browse_button_picks_dir.grid(row=2, column=2, padx=10, pady=2)

        # count_picks_button = ttk.Button(tabs[t], text="Count", command=lambda: count_picks(text_count, entry_pickedmics_dir, entry_picks_dir))
        # count_picks_button.grid(row=3, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_count = ttk.Label(tabs[t], text="")
        # text_count.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        #

        label_todisplay_step3 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step3.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step3 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step3.insert(0, globalnumdisplay)
        entry_todisplay_step3.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_order3 = ttk.Label(tabs[t], text="Order:")
        label_order3.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step3 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step3 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step3, value="First")
        radio_option_first_step3.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step3 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step3, value="Last")
        radio_option_last_step3.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step3 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step3, value="Random")
        radio_option_random_step3.grid(row=6, column=1, padx=5, pady=2, sticky="w")

        label_picktype = ttk.Label(tabs[t], text="Filetype:")
        label_picktype.grid(row=7, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_picktype = tk.StringVar(value="STAR")  # Default selection

        radio_option_star = ttk.Radiobutton(tabs[t], text="STAR", variable=selected_picktype, value="STAR")
        radio_option_star.grid(row=7, column=1, padx=5, pady=2, sticky="w")

        radio_option_cbox = ttk.Radiobutton(tabs[t], text="CBOX", variable=selected_picktype, value="CBOX")
        radio_option_cbox.grid(row=8, column=1, padx=5, pady=2, sticky="w")    
     
        filter_forpicks_checkbox = tk.IntVar(value=1)

        label_forpicks_filterflag = ttk.Label(tabs[t], text="Filter micrographs?")
        label_forpicks_filterflag.grid(row=9, column=0, padx=10, pady=3, sticky="e")

        filter_forpicks_checkbox_button = tk.Checkbutton(tabs[t], variable=filter_forpicks_checkbox)
        filter_forpicks_checkbox_button.grid(row=9, column=1, padx=10, pady=3, sticky="w")

        display_picks_button = ttk.Button(tabs[t], text="Display picks", command=lambda: display(output_text_step3, entry_pickedmics_dir, entry_picks_dir, entry_todisplay_step3, selected_order_step3, selected_picktype, filter_forpicks_checkbox))
        display_picks_button.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

        output_text_step3 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step3.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step3.config(highlightthickness=1, highlightbackground="grey")

        scrollbar3 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step3.config(yscrollcommand=scrollbar3.set)
        scrollbar3.config(command=output_text_step3.yview)
        scrollbar3.grid(row=11, column=2, rowspan=1, sticky="ns")


        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(11, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["mcf"]["titles"][0])

    if len(tabs) > t:

        label_step4 = ttk.Label(tabs[t], text="Multi-Curve-Fitting", style="title.TLabel")
        label_step4.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_coordinate_dir = ttk.Label(tabs[t], text="Cryolo STAR output")
        label_coordinate_dir.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_coordinate_dir = ttk.Entry(tabs[t], textvariable=typedpickdir, font=common_font)
        entry_coordinate_dir.insert(0, globalpickdir)
        entry_coordinate_dir.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_coordinate_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_coordinate_dir))
        browse_coordinate_dir.grid(row=1, column=2, padx=10, pady=2)

        label_tomcfmics_dir = ttk.Label(tabs[t], text="Micrograph directory")
        label_tomcfmics_dir.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_tomcfmics_dir = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        entry_tomcfmics_dir.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_tomcfmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_tomcfmics_dir))
        browse_button_tomcfmics.grid(row=2, column=2, padx=10, pady=2)

        label_suffix_step4 = ttk.Label(tabs[t], text="Micrograph suffix")
        label_suffix_step4.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_suffix_step4 = ttk.Entry(tabs[t], textvariable=typedsuffix, font=common_font)
        entry_suffix_step4.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_pixel_size_step4 = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size_step4.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size_step4 = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        entry_pixel_size_step4.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_samplestep = ttk.Label(tabs[t], text="Step size (Å)")
        label_samplestep.grid(row=5, column=0, padx=10, pady=2, sticky="e")

        entry_samplestep = ttk.Entry(tabs[t], font=common_font)
        entry_samplestep.insert(0, "41")
        entry_samplestep.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        label_anglechange = ttk.Label(tabs[t], text="Max angle change per 4nm")
        label_anglechange.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_anglechange = ttk.Entry(tabs[t], font=common_font)
        entry_anglechange.insert(0, "20")
        entry_anglechange.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        label_minseed = ttk.Label(tabs[t], text="Min to seed filament")
        label_minseed.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_minseed = ttk.Entry(tabs[t], font=common_font)
        entry_minseed.insert(0, "3")
        entry_minseed.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_polynomial = ttk.Label(tabs[t], text="Polynomial")
        label_polynomial.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_polynomial = ttk.Entry(tabs[t], font=common_font)
        entry_polynomial.insert(0, "2")
        entry_polynomial.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        mcf_operation = MCFOperation()

        mcf_button = ttk.Button(tabs[t], text="Fit", command=lambda: mcf_operation.mcf(output_text_step4, entry_coordinate_dir, entry_suffix_step4, entry_pixel_size_step4, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics, notebook, "mcf"))
        mcf_button.grid(row=9, column=0, padx=10, pady=5, sticky="e")

        stop_mcf_button = ttk.Button(tabs[t], text="Stop", command=lambda: mcf_operation.stop_mcf(output_text_step4, entry_coordinate_dir, entry_suffix_step4, entry_pixel_size_step4, entry_samplestep, entry_anglechange, entry_minseed, entry_polynomial, mcf_button, stop_mcf_button, browse_coordinate_dir, entry_tomcfmics_dir, browse_button_tomcfmics, "mcf"))
        stop_mcf_button.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        output_text_step4 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step4.grid(row=10, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step4.config(highlightthickness=1, highlightbackground="grey")

        scrollbar4 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step4.config(yscrollcommand=scrollbar4.set)
        scrollbar4.config(command=output_text_step4.yview)
        scrollbar4.grid(row=10, column=2, rowspan=1, sticky="ns")

        count_mcfs_button = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_mcfs_button,
            entry_tomcfmics_dir.get(),
            os.path.join(entry_coordinate_dir.get(),f"MCF-{entry_samplestep.get()}-{entry_anglechange.get()}-{entry_minseed.get()}-{entry_polynomial.get()}"),
            "_resam_Zscore.star"))
        count_mcfs_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step5 = ttk.Label(tabs[t], text="    Display the fit result    ", style="title.TLabel")
        label_step5.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_mcfedmics_dir = ttk.Label(tabs[t], text="Micrograph directory")
        label_mcfedmics_dir.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_mcfedmics_dir = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        #entry_mcfedmics_dir.insert(0, "Micrographs")
        entry_mcfedmics_dir.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_mcfedmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_mcfedmics_dir))
        browse_button_mcfedmics.grid(row=1, column=2, padx=10, pady=2)

        label_mcfcoordinate_dir = ttk.Label(tabs[t], text="Fit directory")
        label_mcfcoordinate_dir.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_mcfcoordinate_dir = ttk.Entry(tabs[t], textvariable=typedmcfdir, font=common_font)
        entry_mcfcoordinate_dir.insert(0, globalmcfdir)
        entry_mcfcoordinate_dir.grid(row=2, column=1, padx=10, pady=2, sticky="ew")  

        browse_button_mcfcoordinate_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_mcfcoordinate_dir))
        browse_button_mcfcoordinate_dir.grid(row=2, column=2, padx=10, pady=2)

        # count_fits_button = ttk.Button(tabs[t], text="Count", command=lambda: count_fits(text_countfits, entry_mcfedmics_dir, entry_mcfcoordinate_dir))
        # count_fits_button.grid(row=3, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_countfits = ttk.Label(tabs[t], text="")
        # text_countfits.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        ##

        label_todisplay_step5 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step5.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step5 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step5.insert(0, "50")
        entry_todisplay_step5.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_order5 = ttk.Label(tabs[t], text="Order:")
        label_order5.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step5 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step5 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step5, value="First")
        radio_option_first_step5.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step5 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step5, value="Last")
        radio_option_last_step5.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step5 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step5, value="Random")
        radio_option_random_step5.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        filter_formcf_checkbox5 = tk.IntVar(value=1)

        label_filterflag5 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag5.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        filter_formcf_checkbox_button5 = tk.Checkbutton(tabs[t], variable=filter_formcf_checkbox5)
        filter_formcf_checkbox_button5.grid(row=7, column=1, padx=10, pady=3, sticky="w")

        display_mcfedpicks_button = ttk.Button(tabs[t], text="Display fit", command=lambda: displaymcf(output_text_step5, entry_mcfedmics_dir, entry_mcfcoordinate_dir, entry_todisplay_step5, selected_order_step5, filter_formcf_checkbox5))
        display_mcfedpicks_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        output_text_step5 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step5.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step5.config(highlightthickness=1, highlightbackground="grey")

        scrollbar5 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step5.config(yscrollcommand=scrollbar5.set)
        scrollbar5.config(command=output_text_step5.yview)
        scrollbar5.grid(row=9, column=2, rowspan=1, sticky="ns")


        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(9, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["split"]["titles"][0])

    if len(tabs) > t:

        label_step6 = ttk.Label(tabs[t], text="Curve splitting", style="title.TLabel")
        label_step6.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_splitcoordinate_dir = ttk.Label(tabs[t], text="Fit STAR files")
        label_splitcoordinate_dir.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_splitcoordinate_dir = ttk.Entry(tabs[t], textvariable=typedmcfdir, font=common_font)
        entry_splitcoordinate_dir.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_split_coordinate_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitcoordinate_dir))
        browse_button_split_coordinate_dir.grid(row=1, column=2, padx=10, pady=2)

        label_tosplitmics_dir = ttk.Label(tabs[t], text="Micrograph directory")
        label_tosplitmics_dir.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_tosplitmics_dir = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        entry_tosplitmics_dir.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_tosplitmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_tosplitmics_dir))
        browse_button_tosplitmics.grid(row=2, column=2, padx=10, pady=2)

        label_splitvalue = ttk.Label(tabs[t], text="Split value")
        label_splitvalue.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_splitvalue = ttk.Entry(tabs[t], font=common_font)
        entry_splitvalue.insert(0, "10")
        entry_splitvalue.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        split_operation = SplitOperation()

        split_button = ttk.Button(tabs[t], text="Split", command=lambda: split_operation.split(output_text_step6, entry_splitcoordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics, notebook, "split"))
        split_button.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        stop_split_button = ttk.Button(tabs[t], text="Stop", command=lambda: split_operation.stop_split(output_text_step6, entry_splitcoordinate_dir, entry_splitvalue, split_button, stop_split_button, browse_button_split_coordinate_dir, entry_tosplitmics_dir, browse_button_tosplitmics, "split"))
        stop_split_button.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        output_text_step6 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step6.grid(row=5, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step6.config(highlightthickness=1, highlightbackground="grey")

        scrollbar6 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step6.config(yscrollcommand=scrollbar6.set)
        scrollbar6.config(command=output_text_step6.yview)
        scrollbar6.grid(row=5, column=2, rowspan=1, sticky="ns")

        count_splits_button = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_splits_button,
            entry_tosplitmics_dir.get(),
            os.path.join(entry_splitcoordinate_dir.get(),f"Split-{entry_splitvalue.get()}"),
            "_resam_Zscore_helix_split.txt"))
        count_splits_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(5, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step7 = ttk.Label(tabs[t], text="    Display the split result    ", style="title.TLabel")
        label_step7.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_splitedmics_dir = ttk.Label(tabs[t], text="Micrograph directory")
        label_splitedmics_dir.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_splitedmics_dir = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        #entry_splitedmics_dir.insert(0, "Micrographs")
        entry_splitedmics_dir.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_splitedmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitedmics_dir))
        browse_button_splitedmics.grid(row=1, column=2, padx=10, pady=2)

        entry_splitcoordinate_dir_step7 = ttk.Label(tabs[t], text="Split directory")
        entry_splitcoordinate_dir_step7.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_splitcoordinate_dir_step7 = ttk.Entry(tabs[t], textvariable=typedsplitdir, font=common_font)
        entry_splitcoordinate_dir_step7.insert(0, globalsplitdir)
        entry_splitcoordinate_dir_step7.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_splitcoordinate_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitcoordinate_dir_step7))
        browse_button_splitcoordinate_dir.grid(row=2, column=2, padx=10, pady=2)

        label_todisplay_step7 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step7.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step7 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step7.insert(0, "50")
        entry_todisplay_step7.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_order7 = ttk.Label(tabs[t], text="Order:")
        label_order7.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step7 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step7 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step7, value="First")
        radio_option_first_step7.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step7 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step7, value="Last")
        radio_option_last_step7.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step7 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step7, value="Random")
        radio_option_random_step7.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        filter_forsplit_checkbox7 = tk.IntVar(value=1)

        label_filterflag7 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag7.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        filter_forsplit_checkbox_button7 = tk.Checkbutton(tabs[t], variable=filter_forsplit_checkbox7)
        filter_forsplit_checkbox_button7.grid(row=7, column=1, padx=10, pady=3, sticky="w")

        display_splitedpicks_button = ttk.Button(tabs[t], text="Display splits", command=lambda: displaysplit(output_text_step7, entry_splitedmics_dir, entry_splitcoordinate_dir_step7, entry_todisplay_step7, selected_order_step7, filter_forsplit_checkbox7))
        display_splitedpicks_button.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        output_text_step7 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step7.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step7.config(highlightthickness=1, highlightbackground="grey")

        scrollbar7 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step7.config(yscrollcommand=scrollbar7.set)
        scrollbar7.config(command=output_text_step7.yview)
        scrollbar7.grid(row=9, column=2, rowspan=1, sticky="ns")

        # count_splits_button_disp = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_splits_button_disp, entry_splitedmics_dir.get(), entry_splitcoordinate_dir_step7.get(), "_resam_Zscore_helix_split.txt"))
        # count_splits_button_disp.grid(row=9, column=0, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(9, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["sub"]["titles"][0])

    if len(tabs) > t:

        label_step8 = ttk.Label(tabs[t], text="Subtract the filaments", style="title.TLabel")
        label_step8.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_mictosub_dir = ttk.Label(tabs[t], text="Micrographs to subtract")
        label_mictosub_dir.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_mictosub_dir = ttk.Entry(tabs[t], textvariable=typedmicrographs, font=common_font)
        #entry_mictosub_dir.insert(0, "Micrographs")
        entry_mictosub_dir.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_mictosub = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_mictosub_dir))
        browse_button_mictosub.grid(row=1, column=2, padx=10, pady=2)

        label_coordstosub = ttk.Label(tabs[t], text="Directory with split filaments")
        label_coordstosub.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_coordstosub = ttk.Entry(tabs[t], textvariable=typedsplitdir, font=common_font)
        entry_coordstosub.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_coordstosub = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_coordstosub))
        browse_button_coordstosub.grid(row=2, column=2, padx=10, pady=2)

        label_suboutput = ttk.Label(tabs[t], text="Output directory")
        label_suboutput.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_suboutput = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        entry_suboutput.insert(0, globalsubmicrographs)
        entry_suboutput.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_automask = ttk.Label(tabs[t], text="Masking:")
        label_automask.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_automask = tk.StringVar(value="Auto (masking and searching)")  # Default selection

        radio_option_auto = ttk.Radiobutton(tabs[t], text="Auto", variable=selected_automask, value="Auto", command=toggle_ui)
        radio_option_auto.grid(row=4, column=1, padx=5, pady=2, sticky="w")  

        radio_option_manual = ttk.Radiobutton(tabs[t], text="Manual", variable=selected_automask, value="Manual", command=toggle_ui)
        radio_option_manual.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        selected_automask.set("Auto")

        label_mask = ttk.Label(tabs[t], text="Mask file")
        label_mask.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_mask = ttk.Entry(tabs[t], font=common_font)
        entry_mask.insert(0, "/cephfs2/chaaban/gui/MT-290A_mask_angpix1p1A_box364X36.mrc")
        entry_mask.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        browse_button_mask = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_mask))
        browse_button_mask.grid(row=6, column=2, padx=10, pady=2)

        label_pixel_size_step8 = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size_step8.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size_step8 = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        entry_pixel_size_step8.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_searchstart = ttk.Label(tabs[t], text="Search start")
        label_searchstart.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_searchstart = ttk.Entry(tabs[t], font=common_font)
        entry_searchstart.insert(0, "57")
        entry_searchstart.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        label_searchend = ttk.Label(tabs[t], text="Search end")
        label_searchend.grid(row=9, column=0, padx=10, pady=2, sticky="e")

        entry_searchend = ttk.Entry(tabs[t], font=common_font)
        entry_searchend.insert(0, "172")
        entry_searchend.grid(row=9, column=1, padx=10, pady=2, sticky="ew")

        subtract_operation = SubtractOperation()

        subtract_button = ttk.Button(tabs[t], text="Subtract", command=lambda: subtract_operation.subtract(output_text_step8, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask, radio_option_manual, radio_option_auto, entry_pixel_size_step8, entry_mask, entry_searchstart, entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub, browse_button_coordstosub, browse_button_mask, notebook, "sub"))
        subtract_button.grid(row=10, column=0, padx=10, pady=5, sticky="e")

        stop_subtract_button = ttk.Button(tabs[t], text="Stop", command=lambda: subtract_operation.stop_subtract(output_text_step8, entry_mictosub_dir, entry_coordstosub, entry_suboutput, selected_automask, radio_option_manual, radio_option_auto, entry_pixel_size_step8, entry_mask, entry_searchstart, entry_searchend, subtract_button, stop_subtract_button, browse_button_mictosub, browse_button_coordstosub, browse_button_mask, "sub"))
        stop_subtract_button.grid(row=10, column=1, padx=10, pady=5, sticky="w")

        output_text_step8 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step8.grid(row=11, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step8.config(highlightthickness=1, highlightbackground="grey")

        scrollbar8 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step8.config(yscrollcommand=scrollbar8.set)
        scrollbar8.config(command=output_text_step8.yview)
        scrollbar8.grid(row=11, column=2, rowspan=1, sticky="ns")

        count_subtractions_button = ttk.Button(tabs[t], text="#", command=lambda: count_mics(count_subtractions_button, entry_suboutput.get()))
        count_subtractions_button.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(11, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step9 = ttk.Label(tabs[t], text="Display the subtraction result", style="title.TLabel")
        label_step9.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_subtractedmics = ttk.Label(tabs[t], text="Micrograph directory")
        label_subtractedmics.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_subtractedmics = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        #entry_subtractedmics.insert(0, "SubtractedMicrographs")
        entry_subtractedmics.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_subtractedmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_subtractedmics))
        browse_button_subtractedmics.grid(row=1, column=2, padx=10, pady=2)

        # count_subs_button = ttk.Button(tabs[t], text="Count", command=lambda: count_subs(text_count_subs, entry_subtractedmics))
        # count_subs_button.grid(row=2, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_count_subs = ttk.Label(tabs[t], text="")
        # text_count_subs.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        showcoords_checkbox = tk.IntVar()

        label_checkbox = ttk.Label(tabs[t], text="Overlay split coordinates?")
        label_checkbox.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        checkbox = tk.Checkbutton(tabs[t], variable=showcoords_checkbox, command=toggle_ui)
        checkbox.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        label_splitcoordinate_step9 = ttk.Label(tabs[t], text="Split directory")
        label_splitcoordinate_step9.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_splitcoordinate_step9 = ttk.Entry(tabs[t], textvariable=typedsplitdir, font=common_font)
        #entry_splitcoordinate_step9.insert(0, "Cryolo/MTs/allpicks_0p2/STAR")
        entry_splitcoordinate_step9.grid(row=3, column=1, padx=10, pady=2, sticky="ew")  

        browse_button_splitcoordinate_step9 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitcoordinate_step9))
        browse_button_splitcoordinate_step9.grid(row=3, column=2, padx=10, pady=2)

        #

        label_todisplay_step9 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step9.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step9 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step9.insert(0, "50")
        entry_todisplay_step9.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_order9 = ttk.Label(tabs[t], text="Order:")
        label_order9.grid(row=5, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step9 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step9 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step9, value="First")
        radio_option_first_step9.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step9 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step9, value="Last")
        radio_option_last_step9.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step9 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step9, value="Random")
        radio_option_random_step9.grid(row=7, column=1, padx=5, pady=2, sticky="w") 

        filter_forsub_checkbox9 = tk.IntVar(value=1)

        label_filterflag9 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag9.grid(row=8, column=0, padx=10, pady=3, sticky="e")

        filter_forsub_checkbox_button9 = tk.Checkbutton(tabs[t], variable=filter_forsub_checkbox9)
        filter_forsub_checkbox_button9.grid(row=8, column=1, padx=10, pady=3, sticky="w")

        display_subtractedmics_button = ttk.Button(tabs[t], text="Display subtraction", command=lambda: displaysub(output_text_step9, entry_subtractedmics, showcoords_checkbox, entry_splitcoordinate_step9, entry_todisplay_step9, selected_order_step9, filter_forsub_checkbox9))
        display_subtractedmics_button.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

        output_text_step9 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step9.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step9.config(highlightthickness=1, highlightbackground="grey")

        scrollbar9 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step9.config(yscrollcommand=scrollbar9.set)
        scrollbar9.config(command=output_text_step9.yview)
        scrollbar9.grid(row=10, column=2, rowspan=1, sticky="ns")


        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["pickcomp"]["titles"][0])

    if len(tabs) > t:

        label_step11 = ttk.Label(tabs[t], text="Pick with Cryolo", style="title.TLabel")
        label_step11.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_submicrographs_topick = ttk.Label(tabs[t], text="Micrographs directory to pick")
        label_submicrographs_topick.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_submicrographs_topick = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        entry_submicrographs_topick.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_submicrographs_topick = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_micrographs_topick))
        browse_button_submicrographs_topick.grid(row=1, column=2, padx=10, pady=2)

        label_pixel_size_subpick = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size_subpick.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size_subpick = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        entry_pixel_size_subpick.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        label_cryolo_model_complex = ttk.Label(tabs[t], text="Cryolo model")
        label_cryolo_model_complex.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_cryolo_model_complex = ttk.Entry(tabs[t], font=common_font)
        entry_cryolo_model_complex.insert(0, "/cephfs/chaaban/CryoloModels/cryolo_model_box580_batch3_3valid.h5")
        entry_cryolo_model_complex.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        browse_button_cryolo_model_complex = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_cryolo_model))
        browse_button_cryolo_model_complex.grid(row=3, column=2, padx=10, pady=2)

        label_threshold_complex = ttk.Label(tabs[t], text="Threshold")
        label_threshold_complex.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_threshold_complex = ttk.Entry(tabs[t], font=common_font)
        entry_threshold_complex.insert(0, "0.28")
        entry_threshold_complex.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_projectname_complex = ttk.Label(tabs[t], text="Cryolo subdirectory name")
        label_projectname_complex.grid(row=5, column=0, padx=10, pady=2, sticky="e")

        entry_projectname_complex = ttk.Entry(tabs[t], font=common_font)
        entry_projectname_complex.insert(0, "Complex")
        entry_projectname_complex.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        label_pickname_complex = ttk.Label(tabs[t], text="Cryolo picking job name")
        label_pickname_complex.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_pickname_complex = ttk.Entry(tabs[t], font=common_font)
        entry_pickname_complex.insert(0, "allpicks_0p28")
        entry_pickname_complex.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        label_gpu_complex = ttk.Label(tabs[t], text="GPU (space-separated)")
        label_gpu_complex.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_gpu_complex = ttk.Entry(tabs[t], font=common_font)
        entry_gpu_complex.insert(0, "0")
        entry_gpu_complex.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_picksubset_complex = ttk.Label(tabs[t], text="Subset")
        label_picksubset_complex.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_picksubset_complex = ttk.Entry(tabs[t], font=common_font)
        entry_picksubset_complex.insert(0, "")
        entry_picksubset_complex.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        output_text_step11 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step11.grid(row=10, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step11.config(highlightthickness=1, highlightbackground="grey")

        pick_operation_complex = CryoloPickOperation()

        pickcomplex_button = ttk.Button(tabs[t], text="Pick", command=lambda: pick_operation_complex.pick(output_text_step11, 638, entry_submicrographs_topick, entry_pixel_size_subpick, entry_cryolo_model_complex, entry_threshold_complex, entry_projectname_complex, entry_pickname_complex, entry_gpu_complex, pickcomplex_button, stop_pickcomplex_button, browse_button_submicrographs_topick, browse_button_cryolo_model_complex, entry_picksubset_complex, resetcomplexpicks_button, notebook, "pickcomp"))
        pickcomplex_button.grid(row=9, column=0, padx=10, pady=5, sticky="e")

        stop_pickcomplex_button = ttk.Button(tabs[t], text="Stop", command=lambda: pick_operation_complex.stop_pick(output_text_step11))
        stop_pickcomplex_button.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        resetcomplexpicks_button = ttk.Button(tabs[t], text="Reset", command=lambda: reset_picks(resetcomplexpicks_button,os.path.join("Cryolo", entry_projectname_complex.get(), entry_pickname_complex.get())))
        resetcomplexpicks_button.grid(row=9, column=1, padx=10, pady=5, sticky="e")

        scrollbar11 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step11.config(yscrollcommand=scrollbar11.set)
        scrollbar11.config(command=output_text_step11.yview)
        scrollbar11.grid(row=10, column=2, rowspan=1, sticky="ns")

        count_complexmics_button = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_complexmics_button,
            entry_submicrographs_topick.get(),
            os.path.join("Cryolo", entry_projectname_complex.get(),entry_pickname_complex.get(),"STAR"),
            ".star"))
        count_complexmics_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        count_complexpicks_button = ttk.Button(tabs[t], text="#", command=lambda: count_picks(count_complexpicks_button,
            os.path.join("Cryolo", entry_projectname_complex.get(),entry_pickname_complex.get(),"STAR"),
            ".star"))
        count_complexpicks_button.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="e")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step12 = ttk.Label(tabs[t], text="Display the Cryolo picks", style="title.TLabel")
        label_step12.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_complex_pickedmics_dir = ttk.Label(tabs[t], text="Micrograph directory")
        label_complex_pickedmics_dir.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_complex_pickedmics_dir = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        entry_complex_pickedmics_dir.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_complex_pickedmics = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_complex_pickedmics_dir))
        browse_button_complex_pickedmics.grid(row=1, column=2, padx=10, pady=2)

        label_complex_picks_dir = ttk.Label(tabs[t], text="Cryolo picking directory")
        label_complex_picks_dir.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_complex_picks_dir = ttk.Entry(tabs[t], font=common_font)
        entry_complex_picks_dir.insert(0, "Cryolo/Complex/allpicks_0p28")
        entry_complex_picks_dir.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_picks_dir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_complex_picks_dir))
        browse_button_picks_dir.grid(row=2, column=2, padx=10, pady=2)

        # count_complex_picks_button = ttk.Button(tabs[t], text="Count", command=lambda: count_complexpicks(text_complex_count, entry_complex_pickedmics_dir, entry_complex_picks_dir))
        # count_complex_picks_button.grid(row=3, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_complex_count = ttk.Label(tabs[t], text="")
        # text_complex_count.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        label_todisplay_step12 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step12.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step12 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        entry_todisplay_step12.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_complex_picktype = ttk.Label(tabs[t], text="Order:")
        label_complex_picktype.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step12 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step12 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step12, value="First")
        radio_option_first_step12.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step12 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step12, value="Last")
        radio_option_last_step12.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step12 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step12, value="Random")
        radio_option_random_step12.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        #

        label_complex_picktype = ttk.Label(tabs[t], text="Filetype:")
        label_complex_picktype.grid(row=7, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_complex_picktype = tk.StringVar(value="STAR")  # Default selection

        radio_complex_option_star = ttk.Radiobutton(tabs[t], text="STAR", variable=selected_complex_picktype, value="STAR")
        radio_complex_option_star.grid(row=7, column=1, padx=5, pady=2, sticky="w")

        radio_complex_option_cbox = ttk.Radiobutton(tabs[t], text="CBOX", variable=selected_complex_picktype, value="CBOX")
        radio_complex_option_cbox.grid(row=8, column=1, padx=5, pady=2, sticky="w")  

        filter_forcomplex_checkbox = tk.IntVar(value=1)

        label_filterflag12 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag12.grid(row=9, column=0, padx=10, pady=3, sticky="e")

        filter_forcomplex_checkbox_button = tk.Checkbutton(tabs[t], variable=filter_forcomplex_checkbox)
        filter_forcomplex_checkbox_button.grid(row=9, column=1, padx=10, pady=3, sticky="w")

        display_complex_picks_button = ttk.Button(tabs[t], text="Display picks", command=lambda: displaycomplex(output_text_step12, entry_complex_pickedmics_dir, entry_complex_picks_dir, entry_todisplay_step12, selected_order_step12, selected_complex_picktype, filter_forcomplex_checkbox))
        display_complex_picks_button.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

        output_text_step12 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step12.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step12.config(highlightthickness=1, highlightbackground="grey")

        scrollbar12 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step12.config(yscrollcommand=scrollbar12.set)
        scrollbar12.config(command=output_text_step12.yview)
        scrollbar12.grid(row=11, column=2, rowspan=1, sticky="ns")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(11, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["pickfil2"]["titles"][0])

    if len(tabs) > t:

        label_step16 = ttk.Label(tabs[t], text="Pick with Cryolo", style="title.TLabel")
        label_step16.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_micrographs_topick16 = ttk.Label(tabs[t], text="Directory to pick")
        label_micrographs_topick16.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_micrographs_topick16 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        #entry_micrographs_topick.insert(0, "Micrographs")
        entry_micrographs_topick16.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_micrographs_topick16 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_micrographs_topick16))
        browse_button_micrographs_topick16.grid(row=1, column=2, padx=10, pady=2)

        label_pixel_size16 = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size16.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size16 = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        #entry_pixel_size.insert(0, globalpixelsize)
        entry_pixel_size16.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        label_cryolo_model16 = ttk.Label(tabs[t], text="Cryolo model")
        label_cryolo_model16.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_cryolo_model16 = ttk.Entry(tabs[t], font=common_font)
        entry_cryolo_model16.insert(0, "/cephfs/chaaban/CryoloModels/MTs/201028_model_K3_1p11apix.h5")
        entry_cryolo_model16.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        browse_button_cryolo_model16 = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_cryolo_model16))
        browse_button_cryolo_model16.grid(row=3, column=2, padx=10, pady=2)

        label_threshold16 = ttk.Label(tabs[t], text="Threshold")
        label_threshold16.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_threshold16 = ttk.Entry(tabs[t], font=common_font)
        entry_threshold16.insert(0, "0.2")
        entry_threshold16.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_projectname = ttk.Label(tabs[t], text="Cryolo subdirectory")
        label_projectname.grid(row=5, column=0, padx=10, pady=2, sticky="e")

        entry_projectname16 = ttk.Entry(tabs[t], font=common_font)
        entry_projectname16.insert(0, "MTs-round2")
        entry_projectname16.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        label_pickname16 = ttk.Label(tabs[t], text="Picking job name")
        label_pickname16.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_pickname16 = ttk.Entry(tabs[t], font=common_font)
        entry_pickname16.insert(0, "allpicks_0p2")
        entry_pickname16.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        label_gpu16 = ttk.Label(tabs[t], text="GPU (space-separated)")
        label_gpu16.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_gpu16 = ttk.Entry(tabs[t], font=common_font)
        entry_gpu16.insert(0, "0")
        entry_gpu16.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_picksubset16 = ttk.Label(tabs[t], text="Subset")
        label_picksubset16.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_picksubset16 = ttk.Entry(tabs[t], font=common_font)
        entry_picksubset16.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        output_text_step16 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step16.grid(row=10, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step16.config(highlightthickness=1, highlightbackground="grey")

        pick_operation_fil2 = CryoloPickOperation()

        pick_button16 = ttk.Button(tabs[t], text="Pick", command=lambda: pick_operation_fil2.pick(output_text_step16, 253, entry_micrographs_topick16, entry_pixel_size16, entry_cryolo_model16, entry_threshold16, entry_projectname16, entry_pickname16, entry_gpu16, pick_button16, stop_pick_button16, browse_button_micrographs_topick16, browse_button_cryolo_model16, entry_picksubset16, resetpicks16_button, notebook, "pickfil2"))
        pick_button16.grid(row=9, column=0, padx=10, pady=5, sticky="e")

        stop_pick_button16 = ttk.Button(tabs[t], text="Stop", command=lambda: pick_operation_fil2.stop_pick(output_text_step16))
        stop_pick_button16.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        resetpicks16_button = ttk.Button(tabs[t], text="Reset", command=lambda: reset_picks(resetpicks16_button,os.path.join("Cryolo", entry_projectname16.get(), entry_pickname16.get())))
        resetpicks16_button.grid(row=9, column=1, padx=10, pady=5, sticky="e")

        scrollbar16 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step16.config(yscrollcommand=scrollbar16.set)
        scrollbar16.config(command=output_text_step16.yview)
        scrollbar16.grid(row=10, column=2, rowspan=1, sticky="ns")

        count_filpicks_button16 = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_filpicks_button16,
            entry_micrographs_topick16.get(),
            os.path.join("Cryolo", entry_projectname16.get(),entry_pickname16.get(),"STAR"),
            ".star"))
        count_filpicks_button16.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step17 = ttk.Label(tabs[t], text="Display the Cryolo picks", style="title.TLabel")
        label_step17.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_pickedmics_dir17 = ttk.Label(tabs[t], text="Micrograph directory")
        label_pickedmics_dir17.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_pickedmics_dir17 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        #entry_pickedmics_dir17.insert(0, "Micrographs")
        entry_pickedmics_dir17.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_pickedmics17 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_pickedmics_dir17))
        browse_button_pickedmics17.grid(row=1, column=2, padx=10, pady=2)

        label_picks_dir17 = ttk.Label(tabs[t], text="Cryolo picking directory")
        label_picks_dir17.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_picks_dir17 = ttk.Entry(tabs[t], font=common_font)
        entry_picks_dir17.insert(0, "Cryolo/MTs-round2/allpicks_0p2")
        entry_picks_dir17.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_picks_dir17 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_picks_dir17))
        browse_button_picks_dir17.grid(row=2, column=2, padx=10, pady=2)

        # count_picks_button = ttk.Button(tabs[t], text="Count", command=lambda: count_picks(text_count, entry_pickedmics_dir, entry_picks_dir))
        # count_picks_button.grid(row=3, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_count = ttk.Label(tabs[t], text="")
        # text_count.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        label_todisplay_step17 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step17.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step17 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step17.insert(0, globalnumdisplay)
        entry_todisplay_step17.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_order17 = ttk.Label(tabs[t], text="Order:")
        label_order17.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step17 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step17 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step17, value="First")
        radio_option_first_step17.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step17 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step17, value="Last")
        radio_option_last_step17.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step17 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step17, value="Random")
        radio_option_random_step17.grid(row=6, column=1, padx=5, pady=2, sticky="w")

        label_picktype17 = ttk.Label(tabs[t], text="Filetype:")
        label_picktype17.grid(row=7, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_picktype17 = tk.StringVar(value="STAR")  # Default selection

        radio_option_star17 = ttk.Radiobutton(tabs[t], text="STAR", variable=selected_picktype17, value="STAR")
        radio_option_star17.grid(row=7, column=1, padx=5, pady=2, sticky="w")

        radio_option_cbox17 = ttk.Radiobutton(tabs[t], text="CBOX", variable=selected_picktype17, value="CBOX")
        radio_option_cbox17.grid(row=8, column=1, padx=5, pady=2, sticky="w")    
     
        filter_forpicks_checkbox17 = tk.IntVar(value=1)

        label_forpicks_filterflag17 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_forpicks_filterflag17.grid(row=9, column=0, padx=10, pady=3, sticky="e")

        filter_forpicks_checkbox_button17 = tk.Checkbutton(tabs[t], variable=filter_forpicks_checkbox17)
        filter_forpicks_checkbox_button17.grid(row=9, column=1, padx=10, pady=3, sticky="w")

        display_picks_button = ttk.Button(tabs[t], text="Display picks", command=lambda: display(output_text_step17, entry_pickedmics_dir17, entry_picks_dir17, entry_todisplay_step17, selected_order_step17, selected_picktype17, filter_forpicks_checkbox17))
        display_picks_button.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

        output_text_step17 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step17.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step17.config(highlightthickness=1, highlightbackground="grey")

        scrollbar17 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step17.config(yscrollcommand=scrollbar17.set)
        scrollbar17.config(command=output_text_step17.yview)
        scrollbar17.grid(row=11, column=2, rowspan=1, sticky="ns")


        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(11, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["mcf2"]["titles"][0])

    if len(tabs) > t:

        label_step18 = ttk.Label(tabs[t], text="Multi-Curve-Fitting", style="title.TLabel")
        label_step18.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_coordinate_dir18 = ttk.Label(tabs[t], text="Cryolo STAR output")
        label_coordinate_dir18.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_coordinate_dir18 = ttk.Entry(tabs[t], textvariable=typedpickdir2, font=common_font)
        entry_coordinate_dir18.insert(0, globalpickdir2)
        entry_coordinate_dir18.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_coordinate_dir18 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_coordinate_dir18))
        browse_coordinate_dir18.grid(row=1, column=2, padx=10, pady=2)

        label_tomcfmics_dir18 = ttk.Label(tabs[t], text="Micrograph directory")
        label_tomcfmics_dir18.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_tomcfmics_dir18 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        entry_tomcfmics_dir18.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_tomcfmics18 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_tomcfmics_dir18))
        browse_button_tomcfmics18.grid(row=2, column=2, padx=10, pady=2)

        label_suffix_step18 = ttk.Label(tabs[t], text="Micrograph suffix")
        label_suffix_step18.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_suffix_step18 = ttk.Entry(tabs[t], textvariable=typedsuffix2, font=common_font)
        entry_suffix_step18.insert(0,globalsuffix2)
        entry_suffix_step18.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_pixel_size_step18 = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size_step18.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size_step18 = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        entry_pixel_size_step18.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_samplestep18 = ttk.Label(tabs[t], text="Step size (Å)")
        label_samplestep18.grid(row=5, column=0, padx=10, pady=2, sticky="e")

        entry_samplestep18 = ttk.Entry(tabs[t], font=common_font)
        entry_samplestep18.insert(0, "41")
        entry_samplestep18.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        label_anglechange18 = ttk.Label(tabs[t], text="Max angle change per 4nm")
        label_anglechange18.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_anglechange18 = ttk.Entry(tabs[t], font=common_font)
        entry_anglechange18.insert(0, "20")
        entry_anglechange18.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        label_minseed18 = ttk.Label(tabs[t], text="Min to seed filament")
        label_minseed18.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_minseed18 = ttk.Entry(tabs[t], font=common_font)
        entry_minseed18.insert(0, "3")
        entry_minseed18.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_polynomial18 = ttk.Label(tabs[t], text="Polynomial")
        label_polynomial18.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_polynomial18 = ttk.Entry(tabs[t], font=common_font)
        entry_polynomial18.insert(0, "2")
        entry_polynomial18.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        mcf_operation18 = MCFOperation()

        mcf_button18 = ttk.Button(tabs[t], text="Fit", command=lambda: mcf_operation18.mcf(output_text_step18, entry_coordinate_dir18, entry_suffix_step18, entry_pixel_size_step18, entry_samplestep18, entry_anglechange18, entry_minseed18, entry_polynomial18, mcf_button18, stop_mcf_button18, browse_coordinate_dir18, entry_tomcfmics_dir18, browse_button_tomcfmics18, notebook, "mcf2"))
        mcf_button18.grid(row=9, column=0, padx=10, pady=5, sticky="e")

        stop_mcf_button18 = ttk.Button(tabs[t], text="Stop", command=lambda: mcf_operation18.stop_mcf(output_text_step18, entry_coordinate_dir18, entry_suffix_step18, entry_pixel_size_step18, entry_samplestep18, entry_anglechange18, entry_minseed18, entry_polynomial18, mcf_button18, stop_mcf_button18, browse_coordinate_dir18, entry_tomcfmics_dir18, browse_button_tomcfmics18, "mcf2"))
        stop_mcf_button18.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        output_text_step18 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step18.grid(row=10, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step18.config(highlightthickness=1, highlightbackground="grey")

        scrollbar18 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step18.config(yscrollcommand=scrollbar18.set)
        scrollbar18.config(command=output_text_step18.yview)
        scrollbar18.grid(row=10, column=2, rowspan=1, sticky="ns")

        count_mcfs_button18 = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_mcfs_button18,
            entry_tomcfmics_dir18.get(),
            os.path.join(entry_coordinate_dir18.get(),f"MCF-{entry_samplestep18.get()}-{entry_anglechange18.get()}-{entry_minseed18.get()}-{entry_polynomial18.get()}"),
            "_resam_Zscore.star"))
        count_mcfs_button18.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step19 = ttk.Label(tabs[t], text="    Display the fit result    ", style="title.TLabel")
        label_step19.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_mcfedmics_dir19 = ttk.Label(tabs[t], text="Micrograph directory")
        label_mcfedmics_dir19.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_mcfedmics_dir19 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        #entry_mcfedmics_dir19.insert(0, "Micrographs")
        entry_mcfedmics_dir19.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_mcfedmics19 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_mcfedmics_dir19))
        browse_button_mcfedmics19.grid(row=1, column=2, padx=10, pady=2)

        label_mcfcoordinate_dir19 = ttk.Label(tabs[t], text="Fit directory")
        label_mcfcoordinate_dir19.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_mcfcoordinate_dir19 = ttk.Entry(tabs[t], textvariable=typedmcfdir2, font=common_font)
        entry_mcfcoordinate_dir19.insert(0, globalmcfdir2)
        entry_mcfcoordinate_dir19.grid(row=2, column=1, padx=10, pady=2, sticky="ew")  

        browse_button_mcfcoordinate_dir19 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_mcfcoordinate_dir19))
        browse_button_mcfcoordinate_dir19.grid(row=2, column=2, padx=10, pady=2)

        # count_fits_button = ttk.Button(tabs[t], text="Count", command=lambda: count_fits(text_countfits, entry_mcfedmics_dir, entry_mcfcoordinate_dir))
        # count_fits_button.grid(row=3, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_countfits = ttk.Label(tabs[t], text="")
        # text_countfits.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        ##

        label_todisplay_step19 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step19.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step19 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step19.insert(0, "50")
        entry_todisplay_step19.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_order19 = ttk.Label(tabs[t], text="Order:")
        label_order19.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step19 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step19 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step19, value="First")
        radio_option_first_step19.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step19 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step19, value="Last")
        radio_option_last_step19.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step19 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step19, value="Random")
        radio_option_random_step19.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        filter_formcf_checkbox19 = tk.IntVar(value=1)

        label_filterflag19 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag19.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        filter_formcf_checkbox_button19 = tk.Checkbutton(tabs[t], variable=filter_formcf_checkbox19)
        filter_formcf_checkbox_button19.grid(row=7, column=1, padx=10, pady=3, sticky="w")

        display_mcfedpicks_button19 = ttk.Button(tabs[t], text="Display fit", command=lambda: displaymcf(output_text_step19, entry_mcfedmics_dir19, entry_mcfcoordinate_dir19, entry_todisplay_step19, selected_order_step19, filter_formcf_checkbox19))
        display_mcfedpicks_button19.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        output_text_step19 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step19.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step19.config(highlightthickness=1, highlightbackground="grey")

        scrollbar19 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step19.config(yscrollcommand=scrollbar19.set)
        scrollbar19.config(command=output_text_step19.yview)
        scrollbar19.grid(row=9, column=2, rowspan=1, sticky="ns")


        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(9, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["split2"]["titles"][0])

    if len(tabs) > t:

        label_step20 = ttk.Label(tabs[t], text="Curve splitting", style="title.TLabel")
        label_step20.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_splitcoordinate_dir20 = ttk.Label(tabs[t], text="Fit STAR files")
        label_splitcoordinate_dir20.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_splitcoordinate_dir20 = ttk.Entry(tabs[t], textvariable=typedmcfdir2, font=common_font)
        #entry_splitcoordinate_dir20.insert(0, globalmcfdir2)
        entry_splitcoordinate_dir20.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_split_coordinate_dir20 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitcoordinate_dir20))
        browse_button_split_coordinate_dir20.grid(row=1, column=2, padx=10, pady=2)

        label_tosplitmics_dir20 = ttk.Label(tabs[t], text="Micrograph directory")
        label_tosplitmics_dir20.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_tosplitmics_dir20 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        entry_tosplitmics_dir20.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_tosplitmics20 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_tosplitmics_dir20))
        browse_button_tosplitmics20.grid(row=2, column=2, padx=10, pady=2)

        label_splitvalue20 = ttk.Label(tabs[t], text="Split value")
        label_splitvalue20.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_splitvalue20 = ttk.Entry(tabs[t], font=common_font)
        entry_splitvalue20.insert(0, "10")
        entry_splitvalue20.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        split_operation20 = SplitOperation()

        split_button20 = ttk.Button(tabs[t], text="Split", command=lambda: split_operation20.split(output_text_step20, entry_splitcoordinate_dir20, entry_splitvalue20, split_button20, stop_split_button20, browse_button_split_coordinate_dir20, entry_tosplitmics_dir20, browse_button_tosplitmics20, notebook, "split2"))
        split_button20.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        stop_split_button20 = ttk.Button(tabs[t], text="Stop", command=lambda: split_operation20.stop_split(output_text_step20, entry_splitcoordinate_dir20, entry_splitvalue20, split_button20, stop_split_button20, browse_button_split_coordinate_dir20, entry_tosplitmics_dir20, browse_button_tosplitmics20, "split2"))
        stop_split_button20.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        output_text_step20 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step20.grid(row=5, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step20.config(highlightthickness=1, highlightbackground="grey")

        scrollbar20 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step20.config(yscrollcommand=scrollbar20.set)
        scrollbar20.config(command=output_text_step20.yview)
        scrollbar20.grid(row=5, column=2, rowspan=1, sticky="ns")

        count_splits_button20 = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_splits_button20,
            entry_tosplitmics_dir20.get(),
            os.path.join(entry_splitcoordinate_dir20.get(),f"Split-{entry_splitvalue20.get()}"),
            "_resam_Zscore_helix_split.txt"))
        count_splits_button20.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(5, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step21 = ttk.Label(tabs[t], text="    Display the split result    ", style="title.TLabel")
        label_step21.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_splitedmics_dir21 = ttk.Label(tabs[t], text="Micrograph directory")
        label_splitedmics_dir21.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_splitedmics_dir21 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        #entry_splitedmics_dir21.insert(0, "Micrographs")
        entry_splitedmics_dir21.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_splitedmics21 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitedmics_dir21))
        browse_button_splitedmics21.grid(row=1, column=2, padx=10, pady=2)

        entry_splitcoordinate_dir_step21 = ttk.Label(tabs[t], text="Split directory")
        entry_splitcoordinate_dir_step21.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_splitcoordinate_dir_step21 = ttk.Entry(tabs[t], textvariable=typedsplitdir2, font=common_font)
        entry_splitcoordinate_dir_step21.insert(0, globalsplitdir2)
        entry_splitcoordinate_dir_step21.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_splitcoordinate_dir21 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitcoordinate_dir_step21))
        browse_button_splitcoordinate_dir21.grid(row=2, column=2, padx=10, pady=2)

        # count_splits_button = ttk.Button(tabs[t], text="Count", command=lambda: count_splits(text_countsplits, entry_splitedmics_dir, entry_splitcoordinate_dir_step7))
        # count_splits_button.grid(row=3, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_countsplits = ttk.Label(tabs[t], text="")
        # text_countsplits.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        label_todisplay_step21 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step21.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step21 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step21.insert(0, "50")
        entry_todisplay_step21.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_order21 = ttk.Label(tabs[t], text="Order:")
        label_order21.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step21 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step21 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step21, value="First")
        radio_option_first_step21.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step21 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step21, value="Last")
        radio_option_last_step21.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step21 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step21, value="Random")
        radio_option_random_step21.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        filter_forsplit_checkbox21 = tk.IntVar(value=1)

        label_filterflag21 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag21.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        filter_forsplit_checkbox_button21 = tk.Checkbutton(tabs[t], variable=filter_forsplit_checkbox21)
        filter_forsplit_checkbox_button21.grid(row=7, column=1, padx=10, pady=3, sticky="w")

        display_splitedpicks_button21 = ttk.Button(tabs[t], text="Display splits", command=lambda: displaysplit(output_text_step21, entry_splitedmics_dir21, entry_splitcoordinate_dir_step21, entry_todisplay_step21, selected_order_step21, filter_forsplit_checkbox21))
        display_splitedpicks_button21.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        output_text_step21 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step21.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step21.config(highlightthickness=1, highlightbackground="grey")

        scrollbar21 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step21.config(yscrollcommand=scrollbar21.set)
        scrollbar21.config(command=output_text_step21.yview)
        scrollbar21.grid(row=9, column=2, rowspan=1, sticky="ns")

        # count_splits_button_disp = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_splits_button_disp, entry_splitedmics_dir.get(), entry_splitcoordinate_dir_step7.get(), "_resam_Zscore_helix_split.txt"))
        # count_splits_button_disp.grid(row=9, column=0, padx=10, pady=10, sticky="w")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(9, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["sub2"]["titles"][0])

    if len(tabs) > t:

        label_step22 = ttk.Label(tabs[t], text="Subtract the filaments", style="title.TLabel")
        label_step22.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_mictosub_dir22 = ttk.Label(tabs[t], text="Micrographs to subtract")
        label_mictosub_dir22.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_mictosub_dir22 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        #entry_mictosub_dir22.insert(0, "Micrographs")
        entry_mictosub_dir22.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_mictosub22 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_mictosub_dir22))
        browse_button_mictosub22.grid(row=1, column=2, padx=10, pady=2)

        label_coordstosub22 = ttk.Label(tabs[t], text="Directory with split filaments")
        label_coordstosub22.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_coordstosub22 = ttk.Entry(tabs[t], textvariable=typedsplitdir2, font=common_font)
        entry_coordstosub22.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_coordstosub22 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_coordstosub22))
        browse_button_coordstosub22.grid(row=2, column=2, padx=10, pady=2)

        label_suboutput22 = ttk.Label(tabs[t], text="Output directory")
        label_suboutput22.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_suboutput22 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs2, font=common_font)
        entry_suboutput22.insert(0, globalsubmicrographs2)
        entry_suboutput22.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_automask22 = ttk.Label(tabs[t], text="Masking:")
        label_automask22.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_automask22 = tk.StringVar(value="Auto (masking and searching)")  # Default selection

        radio_option_auto22 = ttk.Radiobutton(tabs[t], text="Auto", variable=selected_automask22, value="Auto", command=toggle_ui)
        radio_option_auto22.grid(row=4, column=1, padx=5, pady=2, sticky="w")  

        radio_option_manual22 = ttk.Radiobutton(tabs[t], text="Manual", variable=selected_automask22, value="Manual", command=toggle_ui)
        radio_option_manual22.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        selected_automask22.set("Auto")

        label_mask22 = ttk.Label(tabs[t], text="Mask file")
        label_mask22.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_mask22 = ttk.Entry(tabs[t], font=common_font)
        entry_mask22.insert(0, "/cephfs2/chaaban/gui/MT-290A_mask_angpix1p1A_box364X36.mrc")
        entry_mask22.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        browse_button_mask22 = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_mask22))
        browse_button_mask22.grid(row=6, column=2, padx=10, pady=2)

        label_pixel_size_step22 = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size_step22.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size_step22 = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        entry_pixel_size_step22.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_searchstart22 = ttk.Label(tabs[t], text="Search start")
        label_searchstart22.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_searchstart22 = ttk.Entry(tabs[t], font=common_font)
        entry_searchstart22.insert(0, "57")
        entry_searchstart22.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        label_searchend22 = ttk.Label(tabs[t], text="Search end")
        label_searchend22.grid(row=9, column=0, padx=10, pady=2, sticky="e")

        entry_searchend22 = ttk.Entry(tabs[t], font=common_font)
        entry_searchend22.insert(0, "172")
        entry_searchend22.grid(row=9, column=1, padx=10, pady=2, sticky="ew")

        subtract_operation22 = SubtractOperation()

        subtract_button22 = ttk.Button(tabs[t], text="Subtract", command=lambda: subtract_operation22.subtract(output_text_step22, entry_mictosub_dir22, entry_coordstosub22, entry_suboutput22, selected_automask22, radio_option_manual22, radio_option_auto22, entry_pixel_size_step22, entry_mask22, entry_searchstart22, entry_searchend22, subtract_button22, stop_subtract_button22, browse_button_mictosub22, browse_button_coordstosub22, browse_button_mask22, notebook, "sub2"))
        subtract_button22.grid(row=10, column=0, padx=10, pady=5, sticky="e")

        stop_subtract_button22 = ttk.Button(tabs[t], text="Stop", command=lambda: subtract_operation22.stop_subtract(output_text_step22, entry_mictosub_dir22, entry_coordstosub22, entry_suboutput22, selected_automask22, radio_option_manual22, radio_option_auto22, entry_pixel_size_step22, entry_mask22, entry_searchstart22, entry_searchend22, subtract_button22, stop_subtract_button22, browse_button_mictosub22, browse_button_coordstosub22, browse_button_mask22, "sub2"))
        stop_subtract_button22.grid(row=10, column=1, padx=10, pady=5, sticky="w")

        output_text_step22 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step22.grid(row=11, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step22.config(highlightthickness=1, highlightbackground="grey")

        scrollbar22 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step22.config(yscrollcommand=scrollbar22.set)
        scrollbar22.config(command=output_text_step22.yview)
        scrollbar22.grid(row=11, column=2, rowspan=1, sticky="ns")

        count_subtractions_button22 = ttk.Button(tabs[t], text="#", command=lambda: count_mics(count_subtractions_button22, entry_suboutput22.get()))
        count_subtractions_button22.grid(row=12, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(11, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step23 = ttk.Label(tabs[t], text="Display the subtraction result", style="title.TLabel")
        label_step23.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_subtractedmics23 = ttk.Label(tabs[t], text="Micrograph directory")
        label_subtractedmics23.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_subtractedmics23 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs2, font=common_font)
        #entry_subtractedmics23.insert(0, "SubtractedMicrographs")
        entry_subtractedmics23.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_subtractedmics23 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_subtractedmics23))
        browse_button_subtractedmics23.grid(row=1, column=2, padx=10, pady=2)

        # count_subs_button = ttk.Button(tabs[t], text="Count", command=lambda: count_subs(text_count_subs, entry_subtractedmics))
        # count_subs_button.grid(row=2, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_count_subs = ttk.Label(tabs[t], text="")
        # text_count_subs.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        showcoords_checkbox23 = tk.IntVar()

        label_checkbox23 = ttk.Label(tabs[t], text="Overlay split coordinates?")
        label_checkbox23.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        checkbox23 = tk.Checkbutton(tabs[t], variable=showcoords_checkbox23, command=toggle_ui)
        checkbox23.grid(row=2, column=1, padx=10, pady=2, sticky="w")

        label_splitcoordinate_step23 = ttk.Label(tabs[t], text="Split directory")
        label_splitcoordinate_step23.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_splitcoordinate_step23 = ttk.Entry(tabs[t], textvariable=typedsplitdir2, font=common_font)
        #entry_splitcoordinate_step9.insert(0, "Cryolo/MTs/allpicks_0p2/STAR")
        entry_splitcoordinate_step23.grid(row=3, column=1, padx=10, pady=2, sticky="ew")  

        browse_button_splitcoordinate_step23 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_splitcoordinate_step23))
        browse_button_splitcoordinate_step23.grid(row=3, column=2, padx=10, pady=2)

        #

        label_todisplay_step23 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step23.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step23 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        #entry_todisplay_step23.insert(0, "50")
        entry_todisplay_step23.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_order23 = ttk.Label(tabs[t], text="Order:")
        label_order23.grid(row=5, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step23 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step23 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step23, value="First")
        radio_option_first_step23.grid(row=5, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step23 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step23, value="Last")
        radio_option_last_step23.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step23 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step23, value="Random")
        radio_option_random_step23.grid(row=7, column=1, padx=5, pady=2, sticky="w") 

        filter_forsub_checkbox23 = tk.IntVar(value=1)

        label_filterflag23 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag23.grid(row=8, column=0, padx=10, pady=3, sticky="e")

        filter_forsub_checkbox_button23 = tk.Checkbutton(tabs[t], variable=filter_forsub_checkbox23)
        filter_forsub_checkbox_button23.grid(row=8, column=1, padx=10, pady=3, sticky="w")

        display_subtractedmics_button23 = ttk.Button(tabs[t], text="Display subtraction", command=lambda: displaysub(output_text_step23, entry_subtractedmics23, showcoords_checkbox23, entry_splitcoordinate_step23, entry_todisplay_step23, selected_order_step23, filter_forsub_checkbox23))
        display_subtractedmics_button23.grid(row=9, column=0, columnspan=2, padx=10, pady=5)

        output_text_step23 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step23.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step23.config(highlightthickness=1, highlightbackground="grey")

        scrollbar23 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step23.config(yscrollcommand=scrollbar23.set)
        scrollbar23.config(command=output_text_step23.yview)
        scrollbar23.grid(row=10, column=2, rowspan=1, sticky="ns")


        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text=flagmap["pickcomp2"]["titles"][0])

    if len(tabs) > t:

        label_step24 = ttk.Label(tabs[t], text="Pick with Cryolo", style="title.TLabel")
        label_step24.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_submicrographs_topick24 = ttk.Label(tabs[t], text="Micrographs directory to pick")
        label_submicrographs_topick24.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_submicrographs_topick24 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs2, font=common_font)
        entry_submicrographs_topick24.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_submicrographs_topick24 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_micrographs_topick24))
        browse_button_submicrographs_topick24.grid(row=1, column=2, padx=10, pady=2)

        label_pixel_size_subpick24 = ttk.Label(tabs[t], text="Pixel size (Å/pixel)")
        label_pixel_size_subpick24.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_pixel_size_subpick24 = ttk.Entry(tabs[t], textvariable=typedpixelsize, font=common_font)
        entry_pixel_size_subpick24.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        label_cryolo_model_complex24 = ttk.Label(tabs[t], text="Cryolo model")
        label_cryolo_model_complex24.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_cryolo_model_complex24 = ttk.Entry(tabs[t], font=common_font)
        entry_cryolo_model_complex24.insert(0, "/cephfs/chaaban/CryoloModels/cryolo_model_box580_batch3_3valid.h5")
        entry_cryolo_model_complex24.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        browse_button_cryolo_model_complex24 = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_cryolo_model))
        browse_button_cryolo_model_complex24.grid(row=3, column=2, padx=10, pady=2)

        label_threshold_complex24 = ttk.Label(tabs[t], text="Threshold")
        label_threshold_complex24.grid(row=4, column=0, padx=10, pady=2, sticky="e")

        entry_threshold_complex24 = ttk.Entry(tabs[t], font=common_font)
        entry_threshold_complex24.insert(0, "0.28")
        entry_threshold_complex24.grid(row=4, column=1, padx=10, pady=2, sticky="ew")

        label_projectname_complex24 = ttk.Label(tabs[t], text="Cryolo subdirectory name")
        label_projectname_complex24.grid(row=5, column=0, padx=10, pady=2, sticky="e")

        entry_projectname_complex24 = ttk.Entry(tabs[t], font=common_font)
        entry_projectname_complex24.insert(0, "Complex-round2")
        entry_projectname_complex24.grid(row=5, column=1, padx=10, pady=2, sticky="ew")

        label_pickname_complex24 = ttk.Label(tabs[t], text="Cryolo picking job name")
        label_pickname_complex24.grid(row=6, column=0, padx=10, pady=2, sticky="e")

        entry_pickname_complex24 = ttk.Entry(tabs[t], font=common_font)
        entry_pickname_complex24.insert(0, "allpicks_0p28")
        entry_pickname_complex24.grid(row=6, column=1, padx=10, pady=2, sticky="ew")

        label_gpu_complex24 = ttk.Label(tabs[t], text="GPU (space-separated)")
        label_gpu_complex24.grid(row=7, column=0, padx=10, pady=2, sticky="e")

        entry_gpu_complex24 = ttk.Entry(tabs[t], font=common_font)
        entry_gpu_complex24.insert(0, "0")
        entry_gpu_complex24.grid(row=7, column=1, padx=10, pady=2, sticky="ew")

        label_picksubset_complex24 = ttk.Label(tabs[t], text="Subset")
        label_picksubset_complex24.grid(row=8, column=0, padx=10, pady=2, sticky="e")

        entry_picksubset_complex24 = ttk.Entry(tabs[t], font=common_font)
        entry_picksubset_complex24.insert(0, "")
        entry_picksubset_complex24.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        output_text_step24 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step24.grid(row=10, column=0, columnspan=2, padx=10, pady=4, sticky="nsew")
        output_text_step24.config(highlightthickness=1, highlightbackground="grey")

        pick_operation_complex24 = CryoloPickOperation()

        pickcomplex_button24 = ttk.Button(tabs[t], text="Pick", command=lambda: pick_operation_complex24.pick(output_text_step24, 638, entry_submicrographs_topick24, entry_pixel_size_subpick24, entry_cryolo_model_complex24, entry_threshold_complex24, entry_projectname_complex24, entry_pickname_complex24, entry_gpu_complex24, pickcomplex_button24, stop_pickcomplex_button24, browse_button_submicrographs_topick24, browse_button_cryolo_model_complex24, entry_picksubset_complex24, resetcomplexpicks24_button, notebook, "pickcomp2"))
        pickcomplex_button24.grid(row=9, column=0, padx=10, pady=5, sticky="e")

        stop_pickcomplex_button24 = ttk.Button(tabs[t], text="Stop", command=lambda: pick_operation_complex24.stop_pick(output_text_step24))
        stop_pickcomplex_button24.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        resetcomplexpicks24_button = ttk.Button(tabs[t], text="Reset", command=lambda: reset_picks(resetcomplexpicks24_button,os.path.join("Cryolo", entry_projectname_complex24.get(), entry_pickname_complex24.get())))
        resetcomplexpicks24_button.grid(row=9, column=1, padx=10, pady=5, sticky="e")

        scrollbar24 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step24.config(yscrollcommand=scrollbar24.set)
        scrollbar24.config(command=output_text_step24.yview)
        scrollbar24.grid(row=10, column=2, rowspan=1, sticky="ns")

        count_complexmics_button24 = ttk.Button(tabs[t], text="#", command=lambda: count_corresponding_mics(count_complexmics_button24,
            entry_submicrographs_topick24.get(),
            os.path.join("Cryolo", entry_projectname_complex24.get(),entry_pickname_complex24.get(),"STAR"),
            ".star"))
        count_complexmics_button24.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        count_complexpicks_button24 = ttk.Button(tabs[t], text="#", command=lambda: count_picks(count_complexpicks_button24,
            os.path.join("Cryolo", entry_projectname_complex24.get(),entry_pickname_complex24.get(),"STAR"),
            ".star"))
        count_complexpicks_button24.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="e")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(10, weight=1)

    t+=1
    notebook.tab(t, text="         *         ")

    if len(tabs) > t:

        label_step25 = ttk.Label(tabs[t], text="Display the Cryolo picks", style="title.TLabel")
        label_step25.grid(row=0, column=0, columnspan=2, padx=10, pady=20)

        label_complex_pickedmics_dir25 = ttk.Label(tabs[t], text="Micrograph directory")
        label_complex_pickedmics_dir25.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        entry_complex_pickedmics_dir25 = ttk.Entry(tabs[t], textvariable=typedsubmicrographs2, font=common_font)
        entry_complex_pickedmics_dir25.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        browse_button_complex_pickedmics25 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_complex_pickedmics_dir25))
        browse_button_complex_pickedmics25.grid(row=1, column=2, padx=10, pady=2)

        label_complex_picks_dir25 = ttk.Label(tabs[t], text="Cryolo picking directory")
        label_complex_picks_dir25.grid(row=2, column=0, padx=10, pady=2, sticky="e")

        entry_complex_picks_dir25 = ttk.Entry(tabs[t], font=common_font)
        entry_complex_picks_dir25.insert(0, "Cryolo/Complex-round2/allpicks_0p28")
        entry_complex_picks_dir25.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        browse_button_picks_dir25 = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_complex_picks_dir25))
        browse_button_picks_dir25.grid(row=2, column=2, padx=10, pady=2)

        # count_complex_picks_button = ttk.Button(tabs[t], text="Count", command=lambda: count_complexpicks(text_complex_count, entry_complex_pickedmics_dir, entry_complex_picks_dir))
        # count_complex_picks_button.grid(row=3, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        # text_complex_count = ttk.Label(tabs[t], text="")
        # text_complex_count.grid(row=3, column=1, padx=10, pady=2, sticky="w")

        label_todisplay_step25 = ttk.Label(tabs[t], text="Display (\"all\" for everything)")
        label_todisplay_step25.grid(row=3, column=0, padx=10, pady=2, sticky="e")

        entry_todisplay_step25 = ttk.Entry(tabs[t], textvariable=typednumdisplay, font=common_font)
        entry_todisplay_step25.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        label_complex_picktype25 = ttk.Label(tabs[t], text="Order:")
        label_complex_picktype25.grid(row=4, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_order_step25 = tk.StringVar(value="First")  # Default selection

        radio_option_first_step25 = ttk.Radiobutton(tabs[t], text="First", variable=selected_order_step25, value="First")
        radio_option_first_step25.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        radio_option_last_step25 = ttk.Radiobutton(tabs[t], text="Last", variable=selected_order_step25, value="Last")
        radio_option_last_step25.grid(row=5, column=1, padx=5, pady=2, sticky="w") 

        radio_option_random_step25 = ttk.Radiobutton(tabs[t], text="Random", variable=selected_order_step25, value="Random")
        radio_option_random_step25.grid(row=6, column=1, padx=5, pady=2, sticky="w") 

        #

        label_complex_picktype25 = ttk.Label(tabs[t], text="Filetype:")
        label_complex_picktype25.grid(row=7, column=0, columnspan=1, padx=10, pady=2, sticky="e")

        selected_complex_picktype25 = tk.StringVar(value="STAR")  # Default selection

        radio_complex_option_star25 = ttk.Radiobutton(tabs[t], text="STAR", variable=selected_complex_picktype25, value="STAR")
        radio_complex_option_star25.grid(row=7, column=1, padx=5, pady=2, sticky="w")

        radio_complex_option_cbox25 = ttk.Radiobutton(tabs[t], text="CBOX", variable=selected_complex_picktype25, value="CBOX")
        radio_complex_option_cbox25.grid(row=8, column=1, padx=5, pady=2, sticky="w")      

        filter_forcomplex_checkbox25 = tk.IntVar(value=1)

        label_filterflag25 = ttk.Label(tabs[t], text="Filter micrographs?")
        label_filterflag25.grid(row=9, column=0, padx=10, pady=3, sticky="e")

        filter_forcomplex_checkbox_button25 = tk.Checkbutton(tabs[t], variable=filter_forcomplex_checkbox25)
        filter_forcomplex_checkbox_button25.grid(row=9, column=1, padx=10, pady=3, sticky="w")

        display_complex_picks_button25 = ttk.Button(tabs[t], text="Display picks", command=lambda: displaycomplex(output_text_step25, entry_complex_pickedmics_dir25, entry_complex_picks_dir25, entry_todisplay_step25, selected_order_step25, selected_complex_picktype25, filter_forcomplex_checkbox25))
        display_complex_picks_button25.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

        output_text_step25 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step25.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step25.config(highlightthickness=1, highlightbackground="grey")

        scrollbar25 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step25.config(yscrollcommand=scrollbar25.set)
        scrollbar25.config(command=output_text_step25.yview)
        scrollbar25.grid(row=11, column=2, rowspan=1, sticky="ns")

        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(11, weight=1)

    t+=1
    notebook.tab(t, text="     Merge      ")

    if len(tabs) > t:

        label_step26 = ttk.Label(tabs[t], text="Merge sequential subtractions", style="title.TLabel")
        label_step26.grid(row=0, column=0, columnspan=2, padx=10, pady=8)

        label_firstsub = ttk.Label(tabs[t], text="First subtracted micrographs")
        label_firstsub.grid(row=1, column=0, padx=10, pady=3, sticky="e")

        entry_firstsub = ttk.Entry(tabs[t], textvariable=typedsubmicrographs, font=common_font)
        entry_firstsub.grid(row=1, column=1, padx=10, pady=3, sticky="ew")

        browse_button_firstsub = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_firstsub))
        browse_button_firstsub.grid(row=1, column=2, padx=10, pady=3)

        label_secondsub = ttk.Label(tabs[t], text="Second subtracted micrographs")
        label_secondsub.grid(row=2, column=0, padx=10, pady=3, sticky="e")

        entry_secondsub = ttk.Entry(tabs[t], textvariable=typedsubmicrographs2, font=common_font)
        entry_secondsub.grid(row=2, column=1, padx=10, pady=3, sticky="ew")

        browse_button_secondsub = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_secondsub))
        browse_button_secondsub.grid(row=2, column=2, padx=10, pady=3)

        label_outputsubmerge = ttk.Label(tabs[t], text="Output directory")
        label_outputsubmerge.grid(row=3, column=0, padx=10, pady=3, sticky="e")

        entry_outputsubmerge = ttk.Entry(tabs[t], font=common_font)
        entry_outputsubmerge.insert(0, "SubtractedMicrographs-merged")
        entry_outputsubmerge.grid(row=3, column=1, padx=10, pady=3, sticky="ew")

        submerge_button = ttk.Button(tabs[t], text="Merge subtractions", command=lambda: submerge(output_text_step26, entry_firstsub, browse_button_firstsub, entry_secondsub, browse_button_secondsub, entry_outputsubmerge, submerge_button))
        submerge_button.grid(row=4, column=0, columnspan=2, padx=10, pady=3)

        output_text_step26 = tk.Text(tabs[t], height=2, width=40, font=output_font)
        output_text_step26.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step26.config(highlightthickness=1, highlightbackground="grey")

        # scrollbar26 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        # output_text_step26.config(yscrollcommand=scrollbar26.set)
        # scrollbar26.config(command=output_text_step26.yview)
        # scrollbar26.grid(row=5, column=2, rowspan=1, sticky="ns")

        label_step26_2 = ttk.Label(tabs[t], text="Merge sequential picks", style="title.TLabel")
        label_step26_2.grid(row=6, column=0, columnspan=2, padx=10, pady=8)

        label_firstpicks = ttk.Label(tabs[t], text="First complex picks")
        label_firstpicks.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        entry_firstpicks = ttk.Entry(tabs[t], font=common_font)
        entry_firstpicks.insert(0, "Cryolo/Complex/allpicks_0p28/STAR")
        entry_firstpicks.grid(row=7, column=1, padx=10, pady=3, sticky="ew")

        browse_button_firstpicks = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_firstpicks))
        browse_button_firstpicks.grid(row=7, column=2, padx=10, pady=3)

        label_firstpicks = ttk.Label(tabs[t], text="Second complex picks")
        label_firstpicks.grid(row=8, column=0, padx=10, pady=3, sticky="e")

        entry_secondpicks = ttk.Entry(tabs[t], font=common_font)
        entry_secondpicks.insert(0, "Cryolo/Complex-round2/allpicks_0p28/STAR")
        entry_secondpicks.grid(row=8, column=1, padx=10, pady=3, sticky="ew")

        browse_button_secondpicks = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_secondpicks))
        browse_button_secondpicks.grid(row=8, column=2, padx=10, pady=3)

        label_outputpickmerge = ttk.Label(tabs[t], text="Output directory")
        label_outputpickmerge.grid(row=9, column=0, padx=10, pady=3, sticky="e")

        entry_outputpickmerge = ttk.Entry(tabs[t], font=common_font)
        entry_outputpickmerge.insert(0, "SubtractedMicrographs-merged")
        entry_outputpickmerge.grid(row=9, column=1, padx=10, pady=3, sticky="ew")

        pickmerge_button = ttk.Button(tabs[t], text="Merge picks", command=lambda: pickmerge(output_text_step26_2, entry_firstpicks, browse_button_firstpicks, entry_secondpicks, browse_button_secondpicks, entry_outputpickmerge, pickmerge_button))
        pickmerge_button.grid(row=10, column=0, columnspan=2, padx=10, pady=3)

        output_text_step26_2 = tk.Text(tabs[t], height=2, width=40, font=output_font)
        output_text_step26_2.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step26_2.config(highlightthickness=1, highlightbackground="grey")

        # scrollbar26_2 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        # output_text_step26_2.config(yscrollcommand=scrollbar26_2.set)
        # scrollbar26_2.config(command=output_text_step26_2.yview)
        # scrollbar26_2.grid(row=11, column=2, rowspan=1, sticky="ns")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(5, weight=1)
        tabs[t].grid_rowconfigure(11, weight=1)


    t+=1
    notebook.tab(t, text="    Prep star    ")

    if len(tabs) > t:

        label_step10 = ttk.Label(tabs[t], text="Modify micrograph star file", style="title.TLabel")
        label_step10.grid(row=0, column=0, columnspan=2, padx=10, pady=8)

        label1_step10 = ttk.Label(tabs[t], text="Run only after subtraction (or merging if subtrated twice) is complete")
        label1_step10.grid(row=1, column=0, columnspan=2, padx=10, pady=8)

        label_micstar = ttk.Label(tabs[t], text="Micrograph star file")
        label_micstar.grid(row=2, column=0, padx=10, pady=3, sticky="e")

        entry_micstar = ttk.Entry(tabs[t], font=common_font)
        entry_micstar.insert(0, "CtfFind/job003/micrographs_ctf.star")
        entry_micstar.grid(row=2, column=1, padx=10, pady=3, sticky="ew")

        browse_button_micstar = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_micstar))
        browse_button_micstar.grid(row=2, column=2, padx=10, pady=3)

        label_prefix = ttk.Label(tabs[t], text="Micrograph prefix")
        label_prefix.grid(row=3, column=0, padx=10, pady=3, sticky="e")

        entry_prefix = ttk.Entry(tabs[t], font=common_font)
        entry_prefix.insert(0, "FoilHole")
        entry_prefix.grid(row=3, column=1, padx=10, pady=3, sticky="ew")

        label_submicsdir = ttk.Label(tabs[t], text="Subtracted micrographs")
        label_submicsdir.grid(row=4, column=0, padx=10, pady=3, sticky="e")

        entry_submicsdir = ttk.Entry(tabs[t], font=common_font)
        entry_submicsdir.insert(0, "SubtractedMicrographs")
        entry_submicsdir.grid(row=4, column=1, padx=10, pady=3, sticky="ew")

        browse_button_submicsdir = ttk.Button(tabs[t], text="...", command=lambda: browse_directory(entry_submicsdir))
        browse_button_submicsdir.grid(row=4, column=2, padx=10, pady=3)

        label_outstar = ttk.Label(tabs[t], text="Output name")
        label_outstar.grid(row=5, column=0, padx=10, pady=3, sticky="e")

        entry_outstar = ttk.Entry(tabs[t], font=common_font)
        entry_outstar.insert(0, "micrographs_ctf_sub.star")
        entry_outstar.grid(row=5, column=1, padx=10, pady=3, sticky="ew")

        fixstar_button = ttk.Button(tabs[t], text="Fix", command=lambda: fixstar(output_text_step10, entry_micstar, entry_prefix, entry_submicsdir, entry_outstar, fixstar_button))
        fixstar_button.grid(row=6, column=0, columnspan=2, padx=10, pady=3)

        output_text_step10 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step10.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step10.config(highlightthickness=1, highlightbackground="grey")

        scrollbar10 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step10.config(yscrollcommand=scrollbar10.set)
        scrollbar10.config(command=output_text_step10.yview)
        scrollbar10.grid(row=7, column=2, rowspan=1, sticky="ns")


        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(7, weight=1)

    t+=1
    notebook.tab(t, text="      Extract     ")

    if len(tabs) > t:

        label_step11 = ttk.Label(tabs[t], text="Import coordinates and Extract particles", style="title.TLabel")
        label_step11.grid(row=0, column=0, columnspan=2, padx=10, pady=8)

        label1_step11 = ttk.Label(tabs[t], text="Import: Run only after Prep Star is complete")
        label1_step11.grid(row=1, column=0, columnspan=2, padx=10, pady=8)

        label_subcoords = ttk.Label(tabs[t], text="Coordinates (wildcard)")
        label_subcoords.grid(row=2, column=0, padx=10, pady=3, sticky="e")

        entry_subcoords = ttk.Entry(tabs[t], font=common_font)
        entry_subcoords.insert(0, "SubtractedMicrographs/*.star")
        entry_subcoords.grid(row=2, column=1, padx=10, pady=3, sticky="ew")

        import_button = ttk.Button(tabs[t], text="Import", command=lambda: relionimport(output_text_step11a, entry_micstar11, entry_subcoords))
        import_button.grid(row=3, column=0, columnspan=2, padx=10, pady=3)

        output_text_step11a = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step11a.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step11a.config(highlightthickness=1, highlightbackground="grey")

        label2_step11 = ttk.Label(tabs[t], text="Extract: Run only after Import is complete")
        label2_step11.grid(row=5, column=0, columnspan=2, padx=10, pady=8)

        label_micstar11 = ttk.Label(tabs[t], text="Subtracted micrograph star file")
        label_micstar11.grid(row=6, column=0, padx=10, pady=3, sticky="e")

        entry_micstar11 = ttk.Entry(tabs[t], font=common_font)
        entry_micstar11.insert(0, "CtfFind/job003/micrographs_ctf_sub.star")
        entry_micstar11.grid(row=6, column=1, padx=10, pady=3, sticky="ew")

        browse_button_micstar11 = ttk.Button(tabs[t], text="...", command=lambda: browse_file(entry_micstar11))
        browse_button_micstar11.grid(row=6, column=2, padx=10, pady=3)

        label_boxsize = ttk.Label(tabs[t], text="Box size (pixels)")
        label_boxsize.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        entry_boxsize = ttk.Entry(tabs[t], font=common_font)
        entry_boxsize.insert(0, "800")
        entry_boxsize.grid(row=7, column=1, padx=10, pady=3, sticky="ew")

        label_rescaledbox = ttk.Label(tabs[t], text="Rescaled box size (pixels)")
        label_rescaledbox.grid(row=8, column=0, padx=10, pady=3, sticky="e")

        entry_rescaledbox = ttk.Entry(tabs[t], font=common_font)
        entry_rescaledbox.insert(0, "220")
        entry_rescaledbox.grid(row=8, column=1, padx=10, pady=3, sticky="ew")

        label_importjob = ttk.Label(tabs[t], text="Import job (from above)")
        label_importjob.grid(row=9, column=0, padx=10, pady=3, sticky="e")

        entry_importjob = ttk.Entry(tabs[t], font=common_font)
        entry_importjob.insert(0, "job004")
        entry_importjob.grid(row=9, column=1, padx=10, pady=3, sticky="ew")

        extract_button = ttk.Button(tabs[t], text="Extract", command=lambda: relionextract(output_text_step11b, entry_micstar11, entry_importjob, entry_boxsize, entry_rescaledbox))
        extract_button.grid(row=10, column=0, columnspan=2, padx=10, pady=3)

        output_text_step11b = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step11b.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step11b.config(highlightthickness=1, highlightbackground="grey")

        scrollbar11 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step11.config(yscrollcommand=scrollbar11.set)
        scrollbar11.config(command=output_text_step11.yview)
        scrollbar11.grid(row=11, column=2, rowspan=1, sticky="ns")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(11, weight=1)

    t+=1
    notebook.tab(t, text="      Hetero      ")

    if len(tabs) > t:

        label_step12 = ttk.Label(tabs[t], text="Heterogeneous Refinement in CryoSparc", style="title.TLabel")
        label_step12.grid(row=0, column=0, columnspan=2, padx=10, pady=8)

        label1_step12 = ttk.Label(tabs[t], text="Run only after Relion Extract job is complete")
        label1_step12.grid(row=1, column=0, columnspan=2, padx=10, pady=8)

        label_license = ttk.Label(tabs[t], text="CryoSparc License")
        label_license.grid(row=2, column=0, padx=10, pady=3, sticky="e")

        entry_license = ttk.Entry(tabs[t], font=common_font)
        entry_license.insert(0, "9e024538-d7a7-11ed-ab66-33a6c3f6abfb")
        #entry_license.insert(0, "XXXXXXXX-XXXX-XXXX-XXXXX-XXXXXXXXXXXX")
        entry_license.grid(row=2, column=1, padx=10, pady=3, sticky="ew")

        label_host = ttk.Label(tabs[t], text="Host")
        label_host.grid(row=3, column=0, padx=10, pady=3, sticky="e")

        entry_host = ttk.Entry(tabs[t], font=common_font)
        entry_host.insert(0, "flash")
        entry_host.grid(row=3, column=1, padx=10, pady=3, sticky="ew")

        label_port = ttk.Label(tabs[t], text="Port")
        label_port.grid(row=4, column=0, padx=10, pady=3, sticky="e")

        entry_port = ttk.Entry(tabs[t], font=common_font)
        entry_port.insert(0, "43434")
        entry_port.grid(row=4, column=1, padx=10, pady=3, sticky="ew")

        label_email = ttk.Label(tabs[t], text="Email")
        label_email.grid(row=5, column=0, padx=10, pady=3, sticky="e")

        entry_email = ttk.Entry(tabs[t], font=common_font)
        entry_email.insert(0, "chaaban@mrc-lmb.cam.ac.uk")
        entry_email.grid(row=5, column=1, padx=10, pady=3, sticky="ew")

        label_pass = ttk.Label(tabs[t], text="Password")
        label_pass.grid(row=6, column=0, padx=10, pady=3, sticky="e")

        entry_pass = ttk.Entry(tabs[t], font=common_font, show="*")
        entry_pass.insert(0, "xxxxxxxx")
        entry_pass.grid(row=6, column=1, padx=10, pady=3, sticky="ew")

        label_project = ttk.Label(tabs[t], text="Project UID")
        label_project.grid(row=7, column=0, padx=10, pady=3, sticky="e")

        entry_project = ttk.Entry(tabs[t], font=common_font)
        entry_project.insert(0, "P11")
        entry_project.grid(row=7, column=1, padx=10, pady=3, sticky="ew")

        createworkspace_button = ttk.Button(tabs[t], text="Create workspace", command=lambda: cscreateworkspace(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacename))
        createworkspace_button.grid(row=8, column=0, columnspan=1, padx=10, pady=3, sticky="e")

        entry_workspacename = ttk.Entry(tabs[t], font=common_font)
        entry_workspacename.insert(0, "Heterogeneous")
        entry_workspacename.grid(row=8, column=1, padx=10, pady=2, sticky="ew")

        label_workspacenum = ttk.Label(tabs[t], text="Workspace UID")
        label_workspacenum.grid(row=9, column=0, padx=10, pady=2, sticky="e")

        entry_workspacenum = ttk.Entry(tabs[t], font=common_font)
        entry_workspacenum.insert(0, "W4")
        entry_workspacenum.grid(row=9, column=1, padx=10, pady=2, sticky="ew")

        import_button = ttk.Button(tabs[t], text="Import particles", command=lambda: csimportparts(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_particles))
        import_button.grid(row=10, column=0, columnspan=1, padx=10, pady=3, sticky="e")

        entry_particles = ttk.Entry(tabs[t], font=common_font)
        entry_particles.insert(0, "Extract/job005/particles.star")
        entry_particles.grid(row=10, column=1, padx=10, pady=3, sticky="ew")

        importvols_button = ttk.Button(tabs[t], text="Import volumes", command=lambda: csimportvols(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_importvols))
        importvols_button.grid(row=11, column=0, columnspan=1, padx=10, pady=3, sticky="e")

        entry_importvols = ttk.Entry(tabs[t], font=common_font)
        entry_importvols.insert(0, "/cephfs/edamico/Cryosparc/VolumesForHetRef/J139_class_0*_00182_volume.mrc")
        entry_importvols.grid(row=11, column=1, padx=10, pady=3, sticky="ew")

        hetero_button = ttk.Button(tabs[t], text="Hetero. (Jparts-Jvols)", command=lambda: cshetero(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_hetero))
        hetero_button.grid(row=12, column=0, columnspan=1, padx=10, pady=3, sticky="e")

        entry_hetero = ttk.Entry(tabs[t], font=common_font)
        entry_hetero.insert(0, "J1-J2")
        entry_hetero.grid(row=12, column=1, padx=10, pady=3, sticky="ew")

        nonunif_button = ttk.Button(tabs[t], text="Nonunif. (Jhetero-class#)", command=lambda: csnonunif(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_goodclass))
        nonunif_button.grid(row=13, column=0, columnspan=1, padx=10, pady=3, sticky="e")

        entry_goodclass = ttk.Entry(tabs[t], font=common_font)
        entry_goodclass.insert(0, "J3-4")
        entry_goodclass.grid(row=13, column=1, padx=10, pady=3, sticky="ew")

        convert_button = ttk.Button(tabs[t], text="Convert (Jnonunif)", command=lambda: cs2star(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_convertjob, entry_particles))
        convert_button.grid(row=14, column=0, columnspan=1, padx=10, pady=3, sticky="e")

        entry_convertjob = ttk.Entry(tabs[t], font=common_font)
        entry_convertjob.insert(0, "J4")
        entry_convertjob.grid(row=14, column=1, padx=10, pady=3, sticky="ew")

        output_text_step12 = tk.Text(tabs[t], height=5, width=40, font=output_font)
        output_text_step12.grid(row=15, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        output_text_step12.config(highlightthickness=1, highlightbackground="grey")

        scrollbar11 = ttk.Scrollbar(tabs[t], orient=tk.VERTICAL)
        output_text_step12.config(yscrollcommand=scrollbar11.set)
        scrollbar11.config(command=output_text_step11.yview)
        scrollbar11.grid(row=15, column=2, rowspan=1, sticky="ns")

        # Allow both columns to expand when resizing
        tabs[t].grid_columnconfigure(0, weight=1)
        tabs[t].grid_columnconfigure(1, weight=1)

        tabs[t].grid_rowconfigure(15, weight=1)

    ##########
    #PARAMS

    notebook.tab(0, text="  SUBFLOW  ")
    label_hq = ttk.Label(tabs[0], text=f"SUBFLOW {subflow.__version__}", style="title.TLabel")
    label_hq.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    loadsettings_button = ttk.Button(tabs[0], text="Load parameters", command=lambda: browseload_params(paramsdict))
    loadsettings_button.grid(row=1, column=0, padx=10, columnspan=1, pady=10, sticky="ew")

    savesettings_button = ttk.Button(tabs[0], text="Save parameters", command=lambda: saveparams(paramsdict))
    savesettings_button.grid(row=1, column=1, padx=10, columnspan=1, pady=10, sticky="ew")

    eer_var = tk.IntVar()

    label_eer_checkbox = ttk.Label(tabs[0], text="EER")
    label_eer_checkbox.grid(row=2, column=0, padx=10, pady=2, sticky="e")

    eer_switch = ttk.Checkbutton(tabs[0], variable=eer_var, command=toggle_eer_propagate, style="Switch.TCheckbutton")
    eer_switch.grid(row=2, column=1, padx=10, pady=2, sticky="w")

    doublesub_var = tk.IntVar()

    label_doublesub_checkbox = ttk.Label(tabs[0], text="Subtract twice")
    label_doublesub_checkbox.grid(row=3, column=0, padx=10, pady=2, sticky="e")

    doublesub_switch = ttk.Checkbutton(tabs[0], variable=doublesub_var, command=toggle_doublesub_propagate, style="Switch.TCheckbutton")
    doublesub_switch.grid(row=3, column=1, padx=10, pady=4, sticky="w")

    startall_button = ttk.Button(tabs[0], text="Start all", command=startall)
    startall_button.grid(row=4, column=0, padx=10, pady=4, sticky="ew")

    stopall_button = ttk.Button(tabs[0], text="Stop all", command=stopall)
    stopall_button.grid(row=4, column=1, padx=10, pady=4, sticky="ew")

    output_text_hq = tk.Text(tabs[0], height=5, width=40, font=output_font)
    output_text_hq.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    tabs[0].grid_columnconfigure(0, weight=1)
    tabs[0].grid_columnconfigure(1, weight=1)

    tabs[0].grid_rowconfigure(5, weight=1)

    ##########

    paramsdict = {
        "output_text_hq": output_text_hq,
        "eer_var": eer_var,
        "doublesub_var": doublesub_var,
        "entry_scopesourcemovies": entry_scopesourcemovies,
        "entry_syncmovies": entry_syncmovies,
        "entry_eer_dir": entry_eer_dir,
        "entry_eergroups": entry_eergroups,
        "entry_tif_dir": entry_tif_dir,
        "entry_eerprocs": entry_eerprocs,
        "convertgain_checkbox": convertgain_checkbox,
        "entry_gainm1": entry_gainm1,
        "entry_sourcemovies": entry_sourcemovies,
        "entry_gain": entry_gain,
        "entry_optics": entry_optics,
        "entry_pixelsize_corr": entry_pixelsize_corr,
        "entry_voltage": entry_voltage,
        "entry_dose": entry_dose,
        "show_adv": show_adv,
        "entry_eergroups_corr": entry_eergroups_corr,
        "entry_gainrot": entry_gainrot,
        "entry_gainflip": entry_gainflip,
        "entry_mtf": entry_mtf,
        "selected_linktype": selected_linktype,
        "entry_sourcemics_elsewhere": entry_sourcemics_elsewhere,
        "entry_sourcemics": entry_sourcemics,
        "entry_syncmics": entry_syncmics,
        "entry_suffix": entry_suffix,
        "entry_corrmics": entry_corrmics,
        "entry_micrographs_topick": entry_micrographs_topick,
        "entry_pixel_size": entry_pixel_size,
        "entry_cryolo_model": entry_cryolo_model,
        "entry_threshold": entry_threshold,
        "entry_projectname": entry_projectname,
        "entry_pickname": entry_pickname,
        "entry_gpu": entry_gpu,
        "entry_picksubset": entry_picksubset,
        "entry_pickedmics_dir": entry_pickedmics_dir,
        "entry_picks_dir": entry_picks_dir,
        "entry_todisplay_step3": entry_todisplay_step3,
        "selected_picktype": selected_picktype,
        "entry_coordinate_dir": entry_coordinate_dir,
        "entry_suffix_step4": entry_suffix_step4,
        "entry_pixel_size_step4": entry_pixel_size_step4,
        "entry_samplestep": entry_samplestep,
        "entry_anglechange": entry_anglechange,
        "entry_minseed": entry_minseed,
        "entry_polynomial": entry_polynomial,
        "entry_mcfedmics_dir": entry_mcfedmics_dir,
        "entry_mcfcoordinate_dir": entry_mcfcoordinate_dir,
        "entry_splitcoordinate_dir": entry_splitcoordinate_dir,
        "entry_splitvalue": entry_splitvalue,
        "entry_splitedmics_dir": entry_splitedmics_dir,
        "entry_splitcoordinate_dir_step7": entry_splitcoordinate_dir_step7,
        "entry_mictosub_dir": entry_mictosub_dir,
        "entry_coordstosub": entry_coordstosub,
        "entry_suboutput": entry_suboutput,
        "selected_automask": selected_automask,
        "entry_mask": entry_mask,
        "entry_pixel_size_step8": entry_pixel_size_step8,
        "entry_searchstart": entry_searchstart,
        "entry_searchend": entry_searchend,
        "entry_subtractedmics": entry_subtractedmics,
        "entry_submicrographs_topick": entry_submicrographs_topick,
        "entry_pixel_size_subpick": entry_pixel_size_subpick,
        "entry_cryolo_model_complex": entry_cryolo_model_complex,
        "entry_threshold_complex": entry_threshold_complex,
        "entry_projectname_complex": entry_projectname_complex,
        "entry_pickname_complex": entry_pickname_complex,
        "entry_gpu_complex": entry_gpu_complex,
        "entry_picksubset_complex": entry_picksubset_complex,
        "entry_complex_pickedmics_dir": entry_complex_pickedmics_dir,
        "entry_complex_picks_dir": entry_complex_picks_dir,
        "entry_micrographs_topick16": entry_micrographs_topick16,
        "entry_pixel_size16": entry_pixel_size16,
        "entry_cryolo_model16": entry_cryolo_model16,
        "entry_threshold16": entry_threshold16,
        "entry_projectname16": entry_projectname16,
        "entry_pickname16": entry_pickname16,
        "entry_gpu16": entry_gpu16,
        "entry_picksubset16": entry_picksubset16,
        "entry_pickedmics_dir17": entry_pickedmics_dir17,
        "entry_picks_dir17": entry_picks_dir17,
        "entry_coordinate_dir18": entry_coordinate_dir18,
        "entry_suffix_step18": entry_suffix_step18,
        "entry_pixel_size_step18": entry_pixel_size_step18,
        "entry_samplestep18": entry_samplestep18,
        "entry_anglechange18": entry_anglechange18,
        "entry_minseed18": entry_minseed18,
        "entry_polynomial18": entry_polynomial18,
        "entry_mcfedmics_dir19": entry_mcfedmics_dir19,
        "entry_mcfcoordinate_dir19": entry_mcfcoordinate_dir19,
        "entry_splitcoordinate_dir20": entry_splitcoordinate_dir20,
        "entry_splitvalue20": entry_splitvalue20,
        "entry_splitedmics_dir21": entry_splitedmics_dir21,
        "entry_splitcoordinate_dir_step21": entry_splitcoordinate_dir_step21,
        "entry_mictosub_dir22": entry_mictosub_dir22,
        "entry_coordstosub22": entry_coordstosub22,
        "entry_suboutput22": entry_suboutput22,
        "selected_automask22": selected_automask22,
        "entry_mask22": entry_mask22,
        "entry_pixel_size_step22": entry_pixel_size_step22,
        "entry_searchstart22": entry_searchstart22,
        "entry_searchend22": entry_searchend22,
        "entry_subtractedmics23": entry_subtractedmics23,
        "entry_submicrographs_topick24": entry_submicrographs_topick24,
        "entry_pixel_size_subpick24": entry_pixel_size_subpick24,
        "entry_cryolo_model_complex24": entry_cryolo_model_complex24,
        "entry_threshold_complex24": entry_threshold_complex24,
        "entry_projectname_complex24": entry_projectname_complex24,
        "entry_pickname_complex24": entry_pickname_complex24,
        "entry_gpu_complex24": entry_gpu_complex24,
        "entry_picksubset_complex24": entry_picksubset_complex24,
        "entry_complex_pickedmics_dir25": entry_complex_pickedmics_dir25,
        "entry_complex_picks_dir25": entry_complex_picks_dir25,
        "entry_firstsub": entry_firstsub,
        "entry_secondsub": entry_secondsub,
        "entry_outputsubmerge": entry_outputsubmerge,
        "entry_firstpicks": entry_firstpicks,
        "entry_secondpicks": entry_secondpicks,
        "entry_outputpickmerge": entry_outputpickmerge,
        "entry_micstar": entry_micstar,
        "entry_prefix": entry_prefix,
        "entry_submicsdir": entry_submicsdir,
        "entry_outstar": entry_outstar,
        "entry_subcoords": entry_subcoords,
        "entry_micstar11": entry_micstar11,
        "entry_boxsize": entry_boxsize,
        "entry_rescaledbox": entry_rescaledbox,
        "entry_importjob": entry_importjob,
        "entry_license": entry_license,
        "entry_host": entry_host,
        "entry_port": entry_port,
        "entry_email": entry_email,
        "entry_project": entry_project,
        "entry_workspacename": entry_workspacename,
        "entry_workspacenum": entry_workspacenum,
        "entry_particles": entry_particles,
        "entry_importvols": entry_importvols,
        "entry_hetero": entry_hetero,
        "entry_goodclass": entry_goodclass,
        "entry_convertjob": entry_convertjob
    }


    # entry_suboutput.bind("<FocusOut>", lambda event: quarantined_focusout(event, entry_suboutput.get(), text_quarantined, unquarantine_button))
    entry_projectname.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_pickname.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_anglechange.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_samplestep.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_minseed.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_polynomial.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_splitvalue.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_threshold.bind("<FocusOut>", lambda eventthresh: thresh_focusout(eventthresh, 1, entry_threshold.get(), entry_projectname.get(), entry_pickname.get(), entry_samplestep.get(), entry_anglechange.get(), entry_minseed.get(), entry_polynomial.get(), entry_splitvalue.get(), entry_picks_dir, entry_coordinate_dir, entry_mcfcoordinate_dir, entry_splitcoordinate_dir, entry_splitcoordinate_dir_step7, entry_coordstosub, entry_splitcoordinate_step9))
    entry_projectname_complex.bind("<FocusOut>", lambda eventpickcomplex: pickdir_complex_focusout(eventpickcomplex, entry_projectname_complex.get(), entry_pickname_complex.get(), entry_complex_picks_dir, entry_firstpicks))
    entry_pickname_complex.bind("<FocusOut>", lambda eventpickcomplex: pickdir_complex_focusout(eventpickcomplex, entry_projectname_complex.get(), entry_pickname_complex.get(), entry_complex_picks_dir, entry_firstpicks))
    entry_threshold_complex.bind("<FocusOut>", lambda eventthresh: thresh_focusout_complex(eventthresh, 1, entry_projectname_complex.get(), entry_threshold_complex.get(), entry_complex_picks_dir, entry_firstpicks))

    entry_projectname16.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_pickname16.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_anglechange18.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_samplestep18.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_minseed18.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_polynomial18.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_splitvalue20.bind("<FocusOut>", lambda eventpick: pickdir_focusout(eventpick, entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_threshold16.bind("<FocusOut>", lambda eventthresh: thresh_focusout(eventthresh, 2, entry_threshold16.get(), entry_projectname16.get(), entry_pickname16.get(), entry_samplestep18.get(), entry_anglechange18.get(), entry_minseed18.get(), entry_polynomial18.get(), entry_splitvalue20.get(), entry_picks_dir17, entry_coordinate_dir18, entry_mcfcoordinate_dir19, entry_splitcoordinate_dir20, entry_splitcoordinate_dir_step21, entry_coordstosub22, entry_splitcoordinate_step23))
    entry_projectname_complex24.bind("<FocusOut>", lambda eventpickcomplex: pickdir_complex_focusout(eventpickcomplex, entry_projectname_complex24.get(), entry_pickname_complex24.get(), entry_complex_picks_dir25, entry_secondpicks))
    entry_pickname_complex24.bind("<FocusOut>", lambda eventpickcomplex: pickdir_complex_focusout(eventpickcomplex, entry_projectname_complex24.get(), entry_pickname_complex24.get(), entry_complex_picks_dir25, entry_secondpicks))
    entry_threshold_complex24.bind("<FocusOut>", lambda eventthresh: thresh_focusout_complex(eventthresh, 2, entry_projectname_complex24.get(), entry_threshold_complex24.get(), entry_complex_picks_dir25, entry_secondpicks))

    typedmovies.trace("w", set_movies)
    typedpixelsize.trace("w", set_pixelsize)
    typednumdisplay.trace("w", set_numdisplay)
    typedmicrographs.trace("w", set_micrographs)
    typedpickdir.trace("w", set_pickdir)
    typedpickdir2.trace("w", set_pickdir2)
    typedsuffix.trace("w", set_suffix)
    typedsuffix2.trace("w", set_suffix2)
    typedsubmicrographs.trace("w", set_submicrographs)
    typedsubmicrographs2.trace("w", set_submicrographs2)
    typedmcfdir.trace("w", set_mcfdir)
    typedmcfdir2.trace("w", set_mcfdir2)
    typedsplitdir.trace("w", set_splitdir)
    typedsplitdir2.trace("w", set_splitdir2)

    toggle_ui()

    ############
    # Show displays

    global hiddentabs
    hiddentabs = {}

    toggletabs = [4,6,8,10,12,14,16,18,20,22,24]
    for t in toggletabs:
        hiddentabs[t+1] = True
        notebook.tab(t+1, state="hidden")

    def tabclick(event):
        global hiddentabs

        clickedtab = notebook.tk.call(notebook._w, "identify", "tab", event.x, event.y)
        previoustab = notebook.index(notebook.select())

        if clickedtab == previoustab and clickedtab in toggletabs:
            if hiddentabs[clickedtab+1]:
                notebook.tab(clickedtab+1, state="normal")
                hiddentabs[clickedtab+1] = False
            else:
                notebook.tab(clickedtab+1, state="hidden")
                hiddentabs[clickedtab+1] = True
        # elif clickedtab != previoustab and clickedtab != previoustab+1:
        #     for t in toggletabs:
        #         if not hiddentabs[t+1]:
        #             notebook.tab(t+1, state="hidden")
        #             hiddentabs[t+1] = True

    notebook.bind('<Button-1>', tabclick)

    #############
    # Load last settings if available

    if os.path.exists("Subflow/subflow-last.txt"):
        try:
            with open("Subflow/subflow-last.txt", 'r') as file:
                file_path = file.readline()
            loadparams(paramsdict, file_path)
        except Exception as e:
            output_text_hq.insert(tk.END, f"Could not load latest settings from Subflow/subflow-last.txt: {str(e)}\n")

    ############
    # Exit

    def custom_message_box(parent, title, message):
        top = tk.Toplevel(parent)
        top.title(title)

        top.transient(parent) #appear on top of window
        
        label = ttk.Label(top, text=message, anchor="center", justify="center")
        label.pack(padx=20, pady=5)
        
        ok_button = ttk.Button(top, text="Close subflow", command=root.destroy)
        ok_button.pack(pady=5)

    def on_delete():
        custom_message_box(root, "Exit Confirmation", "Did you kill all GPU jobs?\n(Motion correction, CTF estimation, Cryolo picking)\n\n Did you kill all mpirun jobs?\n(EER conversion).")

    root.protocol("WM_DELETE_WINDOW", on_delete)

    ##############
    root.mainloop()
