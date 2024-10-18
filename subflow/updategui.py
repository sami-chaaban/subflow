import threading
import time

linkmov_alias = "linkmov"
linkmov_index = 1
linkmov_titles = ["◌  Link mov   ", "●  Link mov   "]
update_linkmov_flag_lock = threading.Lock()
update_linkmov_flag = False
update_linkmov_already_flag = False

eertotif_alias = "eertotif"
eertotif_index = 2
eertotif_titles = ["◌   eer to tif   ", "●   eer to tif   "]
update_eertotif_flag_lock = threading.Lock()
update_eertotif_flag = False
update_eertotif_already_flag = False

preprocess_alias = "preprocess"
preprocess_index = 3
preprocess_titles = ["◌   Preproc    ", "●   Preproc    "]
update_preprocess_flag_lock = threading.Lock()
update_preprocess_flag = False
update_preprocess_already_flag = False

linkcorr_alias = "linkcorr"
linkcorr_index = 4
linkcorr_titles = ["◌  Link mic    ", "●  Link mic    "]
update_linkcorr_flag_lock = threading.Lock()
update_linkcorr_flag = False
update_linkcorr_already_flag = False

pickfil_alias = "pickfil"
pickfil_index = 6
pickfil_titles = ["◌    Pick fil     ", "●    Pick fil     "]
update_pickfil_flag_lock = threading.Lock()
update_pickfil_flag = False
update_pickfil_already_flag = False

mcf_alias = "mcf"
mcf_index = 8
mcf_titles = ["◌  Fit curves  ", "●  Fit curves  "]
update_mcf_flag_lock = threading.Lock()
update_mcf_flag = False
update_mcf_already_flag = False

split_alias = "split"
split_index = 10
split_titles = ["◌    Split fil     ", "●    Split fil     "]
update_split_flag_lock = threading.Lock()
update_split_flag = False
update_split_already_flag = False

sub_alias = "sub"
sub_index = 12
sub_titles = ["◌  Subtract    ", "●  Subtract    "]
update_sub_flag_lock = threading.Lock()
update_sub_flag = False
update_sub_already_flag = False

pickcomp_alias = "pickcomp"
pickcomp_index = 14
pickcomp_titles = ["◌ Pick comp  ", "● Pick comp  "]
update_pickcomp_flag_lock = threading.Lock()
update_pickcomp_flag = False
update_pickcomp_already_flag = False    

pickfil2_alias = "pickfil2"
pickfil2_index = 16
pickfil2_titles = pickfil_titles
update_pickfil2_flag_lock = threading.Lock()
update_pickfil2_flag = False
update_pickfil2_already_flag = False

mcf2_alias = "mcf2"
mcf2_index = 18
mcf2_titles = mcf_titles
update_mcf2_flag_lock = threading.Lock()
update_mcf2_flag = False
update_mcf2_already_flag = False

split2_alias = "split2"
split2_index = 20
split2_titles = split_titles
update_split2_flag_lock = threading.Lock()
update_split2_flag = False
update_split2_already_flag = False

sub2_alias = "sub2"
sub2_index = 22
sub2_titles = sub_titles
update_sub2_flag_lock = threading.Lock()
update_sub2_flag = False
update_sub2_already_flag = False

pickcomp2_alias = "pickcomp2"
pickcomp2_index = 24
pickcomp2_titles = pickcomp_titles
update_pickcomp2_flag_lock = threading.Lock()
update_pickcomp2_flag = False
update_pickcomp2_already_flag = False

flagmap = {
    linkmov_alias: {
        "index": linkmov_index,
        "titles": linkmov_titles,
        "update_flag": update_linkmov_flag,
        "update_already_flag": update_linkmov_already_flag,
        "lock": threading.Lock()
    },
    eertotif_alias: {
        "index": eertotif_index,
        "titles": eertotif_titles,
        "update_flag": update_eertotif_flag,
        "update_already_flag": update_eertotif_already_flag,
        "lock": threading.Lock()
    },
    preprocess_alias: {
        "index": preprocess_index,
        "titles": preprocess_titles,
        "update_flag": update_preprocess_flag,
        "update_already_flag": update_preprocess_already_flag,
        "lock": threading.Lock()
    },
    linkcorr_alias: {
        "index": linkcorr_index,
        "titles": linkcorr_titles,
        "update_flag": update_linkcorr_flag,
        "update_already_flag": update_linkcorr_already_flag,
        "lock": threading.Lock()
    },
    pickfil_alias: {
        "index": pickfil_index,
        "titles": pickfil_titles,
        "update_flag": update_pickfil_flag,
        "update_already_flag": update_pickfil_already_flag,
        "lock": threading.Lock()
    },
    mcf_alias: {
        "index": mcf_index,
        "titles": mcf_titles,
        "update_flag": update_mcf_flag,
        "update_already_flag": update_mcf_already_flag,
        "lock": threading.Lock()
    },
    split_alias: {
        "index": split_index,
        "titles": split_titles,
        "update_flag": update_split_flag,
        "update_already_flag": update_split_already_flag,
        "lock": threading.Lock()
    },
    sub_alias: {
        "index": sub_index,
        "titles": sub_titles,
        "update_flag": update_sub_flag,
        "update_already_flag": update_sub_already_flag,
        "lock": threading.Lock()
    },
    pickcomp_alias: {
        "index": pickcomp_index,
        "titles": pickcomp_titles,
        "update_flag": update_pickcomp_flag,
        "update_already_flag": update_pickcomp_already_flag,
        "lock": threading.Lock()
    },
    pickfil2_alias: {
        "index": pickfil2_index,
        "titles": pickfil2_titles,
        "update_flag": update_pickfil2_flag,
        "update_already_flag": update_pickfil2_already_flag,
        "lock": threading.Lock()
    },
    mcf2_alias: {
        "index": mcf2_index,
        "titles": mcf2_titles,
        "update_flag": update_mcf2_flag,
        "update_already_flag": update_mcf2_already_flag,
        "lock": threading.Lock()
    },
    split2_alias: {
        "index": split2_index,
        "titles": split2_titles,
        "update_flag": update_split2_flag,
        "update_already_flag": update_split2_already_flag,
        "lock": threading.Lock()
    },
    sub2_alias: {
        "index": sub2_index,
        "titles": sub2_titles,
        "update_flag": update_sub2_flag,
        "update_already_flag": update_sub2_already_flag,
        "lock": threading.Lock()
    },
    pickcomp2_alias: {
        "index": pickcomp2_index,
        "titles": pickcomp2_titles,
        "update_flag": update_pickcomp2_flag,
        "update_already_flag": update_pickcomp2_already_flag,
        "lock": threading.Lock()
    }
}

linkmov_event = threading.Event()
eertotif_event = threading.Event()
preprocess_event = threading.Event()
linkcorr_event = threading.Event()
pickfil_event = threading.Event()
mcf_event = threading.Event()
split_event = threading.Event()
sub_event = threading.Event()
pickcomp_event = threading.Event()
pickfil2_event = threading.Event()
mcf2_event = threading.Event()
split2_event = threading.Event()
sub2_event = threading.Event()
pickcomp2_event = threading.Event()

def set_update_flag(job, value):
    global flagmap

    with flagmap[job]["lock"]:
        flagmap[job]["update_flag"] = value

def get_update_flag(job):

    global flagmap

    with flagmap[job]["lock"]:
        return flagmap[job]["update_flag"]

def set_update_already_flag(job, value):

    global flagmap

    with flagmap[job]["lock"]:
        flagmap[job]["update_already_flag"] = value

def get_update_already_flag(job):

    global flagmap

    with flagmap[job]["lock"]:
        return flagmap[job]["update_already_flag"]

def change_tabtitle(notebook, job):

    global flagmap

    thread = threading.Thread(target=change_tab_text, args=(notebook, job))
    thread.start()

def change_tab_text(notebook, job):

    global flagmap

    index = flagmap[job]["index"]
    textlst = flagmap[job]["titles"]

    i = 0
    while True:
        while get_update_flag(job):
            if not get_update_already_flag(job):
                notebook.tab(index, text=textlst[1])
                set_update_already_flag(job,True)
            time.sleep(0.8)
        notebook.tab(index, text=textlst[0])
        set_update_already_flag(job,False)
        break