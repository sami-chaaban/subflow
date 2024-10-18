import tkinter as tk
from cryosparc.tools import CryoSPARC
from cryosparc.command import CommandClient
import sys
import time
import webbrowser
from starparser import fileparser
from starparser import particleplay
import subprocess
import re
import os
import glob
import json

def getcs(mylicense,myemail,mypass,myportnum,hostname):

    try:
        cs = CryoSPARC(
            license=mylicense,
            host=hostname,
            base_port=int(myportnum),
            email=myemail,
            password=mypass,
        )   
        assert cs.test_connection()
        return(cs)
    except CommandClient.Error:
        return(None)

def cscreateworkspace(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacename):

    mylicense=entry_license.get()
    myemail=entry_email.get()
    mypass=entry_pass.get()
    myportnum = entry_port.get()
    hostname = entry_host.get()
    project_uid = entry_project.get()
    
    cs = getcs(mylicense,myemail,mypass,myportnum,hostname)

    if cs==None:
        output_text_step12.insert(tk.END, f"Error: could not connect (commandclient error).\n")
        output_text_step12.see(tk.END)
        return

    new_workspace_name = entry_workspacename.get()

    workspace = cs.create_workspace(project_uid, new_workspace_name)
    workspace_uid = workspace.uid

    output_text_step12.insert(tk.END, f"Created workspace {workspace_uid}.\n")
    output_text_step12.see(tk.END)

def checkparams(cs, project_uid, workspace_uid):

    allgood=True

    try:
        project = cs.find_project(project_uid)
    except AssertionError:
        output_text_step12.insert(tk.END, f"Error, project {project_uid} doesn't exists.\n")
        output_text_step12.see(tk.END)
        return False

    try:
        workspace = cs.find_workspace(project_uid, workspace_uid)
        if workspace.doc["deleted"]:
            output_text_step12.insert(tk.END, f"Error: {project_uid}-{workspace_uid} previously existed and was deleted.\n")
            output_text_step12.see(tk.END)
            return False
    except AssertionError:
        output_text_step12.insert(tk.END, "Error: workspace doesn't exist\n")
        output_text_step12.see(tk.END)
        return False

    return allgood

def checkjob(cs, project_uid, job_uid):

    allgood=True

    try:
        job = cs.find_job(project_uid, job_uid)
    except AssertionError:
        output_text_step12.insert(tk.END, f"Error, {job_uid} doesn't exist in {project_uid}.\n")
        output_text_step12.see(tk.END)
        return False

    return allgood

def csimportparts(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_particles):

    mylicense=entry_license.get()
    myemail=entry_email.get()
    mypass=entry_pass.get()
    myportnum = entry_port.get()
    hostname = entry_host.get()
    project_uid = entry_project.get()
    workspace_uid = entry_workspacenum.get()

    cs = getcs(mylicense,myemail,mypass,myportnum,hostname)

    if cs==None:
        output_text_step12.insert(tk.END, f"Error: could not connect (commandclient error).\n")
        output_text_step12.see(tk.END)
        return

    #allgood = checkparams(cs, project_uid, workspace_uid)

    #if not allgood:
    #    output_text_step12.insert(tk.END, "Aborted.\n")
    #    output_text_step12.see(tk.END)
    #    return

    workspace = cs.find_workspace(project_uid, workspace_uid)

    #######

    particlestar = entry_particles.get()

    if not os.path.exists(os.path.join(os.getcwd(),particlestar)):
        output_text_step12.insert(tk.END, f"Error: {os.path.join(os.getcwd(),particlestar)} doesn't exist\n")
        output_text_step12.see(tk.END)
        return

    import_particles_job = workspace.create_job(
        "import_particles",
        params={
            "particle_meta_path": os.path.join(os.getcwd(),particlestar),
        },
    )

    if not any(item['name'] == 'SLURM' for item in cs.get_lanes()):
        output_text_step12.insert(tk.END, "Error: expected a GPU lane called \"SLURM\".\n")
        output_text_step12.see(tk.END)
        return

    import_particles_job.queue("SLURM")

    output_text_step12.insert(tk.END, f"Running particle import: {import_particles_job.uid}.\n")
    output_text_step12.see(tk.END)

def csimportvols(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_importvols):

    mylicense=entry_license.get()
    myemail=entry_email.get()
    mypass=entry_pass.get()
    myportnum = entry_port.get()
    hostname = entry_host.get()
    project_uid = entry_project.get()
    workspace_uid = entry_workspacenum.get()

    cs = getcs(mylicense,myemail,mypass,myportnum,hostname)

    if cs==None:
        output_text_step12.insert(tk.END, f"Error: could not connect (commandclient error).\n")
        output_text_step12.see(tk.END)
        return

    allgood = checkparams(cs, project_uid, workspace_uid)

    if not allgood:
        output_text_step12.insert(tk.END, "Aborted.\n")
        output_text_step12.see(tk.END)
        return

    workspace = cs.find_workspace(project_uid, workspace_uid)

    #######

    volumes_path = entry_importvols.get()

    if not glob.glob(volumes_path):
        output_text_step12.insert(tk.END, f"Could not find {volume_path}.\n")
        output_text_step12.see(tk.END)

    import_volumes_job = workspace.create_job(
        "import_volumes",
        params={
            "volume_blob_path": volumes_path
        }
    )

    if not any(item['name'] == 'SLURM' for item in cs.get_lanes()):
        output_text_step12.insert(tk.END, "Error: expected a GPU lane called \"SLURM\".\n")
        output_text_step12.see(tk.END)
        return

    import_volumes_job.queue("SLURM")

    output_text_step12.insert(tk.END, f"Running volume import: {import_volumes_job.uid}.\n")
    output_text_step12.see(tk.END)

def cshetero(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_hetero):

    mylicense=entry_license.get()
    myemail=entry_email.get()
    mypass=entry_pass.get()
    myportnum = entry_port.get()
    hostname = entry_host.get()
    project_uid = entry_project.get()
    workspace_uid = entry_workspacenum.get()

    cs = getcs(mylicense,myemail,mypass,myportnum,hostname)

    if cs==None:
        output_text_step12.insert(tk.END, f"Error: could not connect (commandclient error).\n")
        output_text_step12.see(tk.END)
        return

    #allgood = checkparams(cs, project_uid, workspace_uid)
    #if not allgood:
    #    output_text_step12.insert(tk.END, "Aborted.\n")
    #    output_text_step12.see(tk.END)
    #    return

    workspace = cs.find_workspace(project_uid, workspace_uid)

    #######

    import_particles_job_uid, import_volumes_job_uid = entry_hetero.get().split("-")

    #allgood = checkjob(cs, project_uid, import_particles_job_uid)
    #if allgood:
    #    allgood = checkjob(cs, project_uid, import_volumes_job_uid)
    #if not allgood:
    #    output_text_step12.insert(tk.END, "Aborted.\n")
    #    output_text_step12.see(tk.END)
    #    return

    import_volumes_job = cs.find_job(project_uid, import_volumes_job_uid)

    volumenames=[]
    for voldict in import_volumes_job.doc["output_result_groups"]:
        volumenames.append(voldict["contains"][0]["group_name"])
    heteroref_job = workspace.create_job(
        "hetero_refine",
        params={
            "prepare_window_inner_radius": "0.92"
        },
        connections={
            "particles": (import_particles_job_uid, "imported_particles"),
        }
    )

    for v in volumenames:
        heteroref_job.connect("volume",import_volumes_job.uid,v)

    if not any(item['name'] == 'SLURM' for item in cs.get_lanes()):
        output_text_step12.insert(tk.END, "Error: expected a GPU lane called \"SLURM\".\n")
        output_text_step12.see(tk.END)
        return

    heteroref_job.queue("SLURM")

    output_text_step12.insert(tk.END, f"Running heterogeneous refinement: {heteroref_job.uid}.\n")
    output_text_step12.see(tk.END)

def csnonunif(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_goodclass):

    mylicense=entry_license.get()
    myemail=entry_email.get()
    mypass=entry_pass.get()
    myportnum = entry_port.get()
    hostname = entry_host.get()
    project_uid = entry_project.get()
    workspace_uid = entry_workspacenum.get()

    cs = getcs(mylicense,myemail,mypass,myportnum,hostname)

    if cs==None:
        output_text_step12.insert(tk.END, f"Error: could not connect (commandclient error).\n")
        output_text_step12.see(tk.END)
        return

    allgood = checkparams(cs, project_uid, workspace_uid)

    if not allgood:
        output_text_step12.insert(tk.END, "Aborted.\n")
        output_text_step12.see(tk.END)
        return

    workspace = cs.find_workspace(project_uid, workspace_uid)

    #######

    if len(entry_goodclass.get().split("-"))!=2:
        output_text_step12.insert(tk.END, "Error: provide the argument in the format JXX-Y where X is the job UID and Y is the good class number (starting at 0).\n")
        output_text_step12.see(tk.END)
        return
    else:
        heteroref_job_uid, goodclassnum = entry_goodclass.get().split("-")

    allgood = checkjob(cs, project_uid, heteroref_job_uid)
    if not allgood:
        output_text_step12.insert(tk.END, "Aborted.\n")
        output_text_step12.see(tk.END)
        return

    nurefine_job = workspace.create_job(
        "nonuniform_refine_new",
        params={
            "prepare_window_inner_radius": "0.92"
        },
        connections={
            "particles": (heteroref_job_uid, f"particles_class_{goodclassnum}"),
            "volume": (heteroref_job_uid, f"volume_class_{goodclassnum}")
        }
    )

    if not any(item['name'] == 'SLURM' for item in cs.get_lanes()):
        output_text_step12.insert(tk.END, "Error: expected a GPU lane called \"SLURM\".\n")
        output_text_step12.see(tk.END)
        return

    nurefine_job.queue("SLURM")

    output_text_step12.insert(tk.END, f"Running non-uniform refinement on particles_class_{goodclassnum} with volume_class_{goodclassnum}: {nurefine_job.uid}.\n")
    output_text_step12.see(tk.END)

def cs2star(output_text_step12, entry_license, entry_host, entry_port, entry_email, entry_pass, entry_project, entry_workspacenum, entry_convertjob, entry_particles):

    mylicense=entry_license.get()
    myemail=entry_email.get()
    mypass=entry_pass.get()
    myportnum = entry_port.get()
    hostname = entry_host.get()
    project_uid = entry_project.get()
    workspace_uid = entry_workspacenum.get()

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as config_file:
        config = json.load(config_file)

    csparc2star_python = config.get("csparc2star_python") 
    csparc2star_script = config.get("csparc2star_script") 

    cs = getcs(mylicense,myemail,mypass,myportnum,hostname)

    if cs==None:
        output_text_step12.insert(tk.END, f"Error: could not connect (commandclient error).\n")
        output_text_step12.see(tk.END)
        return

    allgood = checkparams(cs, project_uid, workspace_uid)

    if not allgood:
        output_text_step12.insert(tk.END, "Aborted.\n")
        output_text_step12.see(tk.END)
        return

    workspace = cs.find_workspace(project_uid, workspace_uid)

    ####

    nurefine_job_uid = entry_convertjob.get()

    allgood = checkjob(cs, project_uid, nurefine_job_uid)
    if not allgood:
        output_text_step12.insert(tk.END, "Aborted.\n")
        output_text_step12.see(tk.END)
        return

    nurefine_job = cs.find_job(project_uid, nurefine_job_uid)

    def extract_number(filename):
        match = re.search(r'_(\d{3})_particles\.cs$', filename)
        return int(match.group(1)) if match else None

    numbered_files = []
    for i in nurefine_job.list_files():
        if "_particles.cs" in i:
            number = extract_number(i)
            if number is not None:
                numbered_files.append((number, i))

    nurefine_cs = max(numbered_files, key=lambda x: x[0])[1]

    output_text_step12.insert(tk.END, f"Copying {nurefine_cs}...\n")
    output_text_step12.see(tk.END)

    nurefine_job.download_file(nurefine_cs, nurefine_cs)

    nurefine_map = nurefine_cs.replace("particles.cs", "volume_map.mrc")

    output_text_step12.insert(tk.END, f"Copying {nurefine_map}...\n")
    output_text_step12.see(tk.END)

    nurefine_job.download_file(nurefine_map, nurefine_map)

    nurefine_star = nurefine_cs.replace("cs","star")

    output_text_step12.insert(tk.END, f"Converting to star using csparc2star.py...\n")
    output_text_step12.see(tk.END)

    subprocess.run([csparc2star_python, csparc2star_script, nurefine_cs, nurefine_star])

    ####Fix star

    original_particlestar = entry_particles.get()

    output_text_step12.insert(tk.END, f"Fixing {nurefine_star} using data from {original_particlestar}...\n")
    output_text_step12.see(tk.END)

    if not os.path.exists(original_particlestar):
        output_text_step12.insert(tk.END, f"Error: {original_particlestar} doesn't exist\n")
        output_text_step12.see(tk.END)
        return

    originalparticles, originalmetadata = fileparser.getparticles(original_particlestar)

    first_value = originalparticles['_rlnImageName'].iloc[0]
    stack_path = first_value.split('@')[1].rsplit('/', 1)[0]

    subprocess.run(["sed", "-i", f"s|J[0-9]\\+/imported/[0-9]\\+_|{stack_path}/|g", nurefine_star])

    particles, metadata = fileparser.getparticles(nurefine_star)

    particles["_rlnCoordinateX"]=particles["_rlnOpticsGroup"]
    particles["_rlnCoordinateY"]=particles["_rlnOpticsGroup"]
    particles["_rlnMicrographName"]=particles["_rlnOpticsGroup"]
    metadata[3].append("_rlnCoordinateX")
    metadata[3].append("_rlnCoordinateY")
    metadata[3].append("_rlnMicrographName")

    importparticles = particleplay.importpartvalues(particles, originalparticles, ["_rlnCoordinateX", "_rlnCoordinateY", "_rlnMicrographName"])

    metadata[2]["_rlnOpticsGroupName"]=originalmetadata[2]["_rlnOpticsGroupName"]
    metadata[2]["_rlnOpticsGroup"]=originalmetadata[2]["_rlnOpticsGroup"]
    importparticles["_rlnOpticsGroup"]=originalmetadata[2]["_rlnOpticsGroup"][0]

    fileparser.writestar(importparticles, metadata, nurefine_star)

    output_text_step12.insert(tk.END, f"Fixed {nurefine_star}.\n")
    output_text_step12.see(tk.END)
