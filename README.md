# subflow

Subflow is a GUI for subtracting filaments from cryo-EM micrographs, picking particles from the subtracted micrographs, and transferring the particles between RELION and cryoSPARC.

## Contents

- [Workflow overview](#workflow-overview)
- [Tested versions](#tested-versions)
- [Installation](#installation)
- [Configuration](#configuration)
- [Start a project](#start-a-project)
- [Using the GUI](#using-the-gui)
- [Tutorial](#tutorial)
- [Troubleshooting](#troubleshooting)
- [Citations](#citations)
- [License](#license)

## Workflow overview

The first part of the workflow can run on-the-fly. Each running step monitors the output of the previous step and processes new files as they appear. The final RELION and cryoSPARC steps are run manually after the on-the-fly processing is complete.

During this workflow, Subflow:

- Aligns movie frames and estimates CTF values using RELION schemes (Burt et al., 2024)
- Picks filaments and particles using crYOLO (Wagner et al., 2019; 2020)
- Fits coordinates to identify filaments (Chai et al., 2022)
- Splits the filaments to reduce artefacts caused by bending
- Subtracts filaments (Chai et al., 2022)
- Supports a second round of filament picking and subtraction when required
- Provides display tabs for checking micrographs and coordinates as processing continues
- Imports extracted particles and reference volumes into cryoSPARC
- Runs heterogeneous and non-uniform refinement in cryoSPARC
- Converts the selected particles back to RELION STAR format using pyem

<img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Subtracted-example.png?raw=true" alt="Example micrograph before and after filament subtraction" width="600"/>

## Tested versions

The versions below reflect the current Subflow setup. Other versions may work but have not been checked here.

| Software | Tested version | Notes |
| --- | --- | --- |
| RELION | 5.0 | Source RELION before starting Subflow so its commands are available |
| crYOLO | 1.9.1 | Install in a separate conda environment |
| cryoSPARC / cryosparc-tools | 4.6.0 / 4.6.x | Keep the cryosparc-tools version matched to cryoSPARC |
| pyem | 0.5 | Install in a separate conda environment and record the interpreter and script paths in `config.json` |

## Installation

*Typical install time is 5 minutes given that standard EM processing tools are installed*

1. Create a fresh conda environment with Python 3.9:

   ```bash
   conda create -n subflow python=3.9
   conda activate subflow
   ```

2. Install Subflow:

   ```bash
   pip install subflow
   ```
3. Download the [multi-curve-fitting](https://github.com/PengxinChai/multi-curve-fitting/blob/main/bin/mcurve_fitting_2D.py) and [filament-subtraction](https://github.com/PengxinChai/tubulin-lattice-subtraction/blob/main/bin/mrc_2d_curve_weaken_float16) scripts. Set their location in `config.json`.
   - Give execution priveledges to the script with `chmod +x mrc_2d_curve_weaken_float16`

4. If not installed already, install [RELION](https://github.com/3dem/relion) and make sure it is sourced before starting Subflow.

5. If not installed already, install [crYOLO 1.9.1](https://cryolo.readthedocs.io/en/stable/index.html) and [pyem](https://github.com/asarnow/pyem) in their own conda environments. These environments do not need to be active when Subflow starts; their executable paths are set in `config.json`.

6. If not installed already, install cryoSPARC 4.6.0 and make sure it can be reached from the computer running Subflow.


Before opening the GUI, check that RELION is available:

```bash
which relion
which relion_schemer
```

## Configuration

Create an editable copy of the example configuration in the current directory:

```bash
subflow --init
```

This creates `config.json` without changing the packaged example. Subflow refuses to overwrite the file if it already exists. To create it at a different location:

```bash
subflow --init /path/to/config.json
```

Edit the new file before processing. When the GUI starts from a directory containing `config.json`, it selects that file by default unless a saved parameter file specifies another configuration. For a configuration stored elsewhere, select it in the `Configuration` field on the `SUBFLOW` tab.

**Only config items for the jobs you intend to use will be necessary to update.**

| Setting | Purpose |
| ---  | --- |
| `cryolo_python`| Python executable in the crYOLO environment |
| `cryolo_gui` | Path to `cryolo_gui.py` |
| `cryolo_boxmanager` | Path to `cryolo_boxmanager.py` |
| `subtract_script` | Path to `mrc_2d_curve_weaken_float16` from the filament-subtraction scripts |
| `mcf_script` | Path to `mcurve_fitting_2D.py` |
| `csparc2star_python` | For STAR conversion | Python executable in the pyem environment |
| `csparc2star_script` | For STAR conversion | Path to the pyem `csparc2star.py` script |
| `relion_corr_job` | Custom RELION motion-correction `job.star` |
| `relion_ctf_job` | Custom RELION CTF-estimation `job.star` |
| `relion_extract_job` | Custom RELION extraction `job.star` |

Relion job.star files are important to include for SLURM submission that is institute-specific. Current defaults are for the MRC-LMB, but you can copy any old job.star file from an old job to get the correct `fn_motioncor2_exe`, `min_dedicated`, `nr_mpi`, `nr_thread`, `qsub`, `qsubscript`, `queuename`. Alternatively, do the preprocessing manually and use Subflow for subsequent steps.

Use absolute paths in `config.json` so that the same configuration works from different project directories.

## Start a project

Subflow uses the directory from which it is started as the project directory. Most paths shown in the GUI are relative to this directory, and processing creates folders. Create a separate project directory for each dataset and start Subflow from there:

```bash
mkdir -p /path/to/my-project
cd /path/to/my-project
conda activate subflow
subflow --init
```

Edit config.json before continuing as described above. From now on, just start subflow here with:

```bash
subflow &
```

1. Select a valid `config.json` on the `SUBFLOW` tab.
2. If doing motion correction with EER files, set `EER`
3. If planning on subtracting twice, select `Subtract twice` before editing downstream paths. Changing either switch updates several default paths and shows or hides the relevant tabs.
4. Make sure RELION is sourced and the paths in `config.json` exist.
5. Save the parameters so they can be loaded again (e.g. to `subflow.txt`).

You can start each step in its tab or use Start all to run all steps (see below) after setting appropriate parameters in each tab. See the tutorial below for an example on how to run Subflow.

## Using the GUI

<img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Main-window.png?raw=true" alt="Subflow main window" width="600"/>

### Tabs

| Tab | Purpose |
| --- | --- |
| `SUBFLOW` | Select the configuration, choose EER or double subtraction, load or save parameters, and start or stop monitors |
| `Link mov` | Link incoming movies into the project directory |
| `eer to tif` | Convert EER stacks to TIFF; shown only when `EER` is enabled |
| `Preproc` | Run RELION import, motion correction (float16), and CTF estimation |
| `Link mic` | Link corrected micrographs into `Micrographs` |
| `Pick fil` | Pick filaments as particles with crYOLO |
| `Fit curves` | Turn particle picks into filaments by fitting curves to the coordinates |
| `Split fil` | Split fitted filaments into shorter segments |
| `Subtract` | Subtract the split filaments from the micrographs |
| `Pick comp` | Pick complexes from the subtracted micrographs with crYOLO |
| Round 2 tabs | Repeat `Pick fil` through `Pick comp`; shown only when `Subtract twice` is enabled |
| `Merge` | Merge sequential subtractions and complex picks after double subtraction |
| `Prep star` | Change micrograph paths in the RELION STAR file and place particle coordinates with the subtracted micrographs |
| `Extract` | Import coordinates and extract particles in RELION (float16) |
| `Hetero` | Create a cryoSPARC workspace, import particles and volumes, run heterogeneous and non-uniform refinement, and convert selected particles back to STAR |
| `*` | In many cases, clicking the tab again lets you display and check the output |

- A hollow circle means that an on-the-fly tab is stopped.
- A black circle means that the tab is running.
- The `#` button on a processing tab counts the files produced by that stage.
- To show a QC display tab, select its processing tab and click the selected tab again. The following `*` tab appears. Repeat the click to hide it.

<img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Start-link-movies.png?raw=true" alt="Link movies tab while its monitor is running" width="600"/>

<img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Link-micrographs.png?raw=true" alt="Link micrographs processing tab" width="600"/>

<img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/View-micrographs.png?raw=true" alt="Micrograph display tab shown beside the processing tab" width="600"/>

### Save parameters

- `Save parameters` writes the current fields to the file you choose.
- Subflow records the path of the most recently saved or loaded parameter file in `Subflow/subflow-last.txt` inside the current project directory.
- Starting Subflow again from the same project directory automatically loads that parameter file.
- Starting from a different directory uses that directory's own `Subflow/subflow-last.txt`, if one exists.
- Moving or deleting the saved parameter file prevents it from being loaded automatically.
- Changes made after the last save are not recovered.
- Running and stopped states are not saved, and monitors do not restart automatically.
- The cryoSPARC password is not saved and must be entered again after restarting.

<img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Save-parameters.png?raw=true" alt="Saved Subflow parameters shown in the main output box" width="600"/>

### Start all

`Start all` starts every enabled on-the-fly step. The steps start as monitors at about the same time; Subflow does not wait for one complete stage before starting the next monitor. Each monitor waits for suitable output from the previous step.

With the default single-subtraction workflow, `Start all` starts:

```text
Link mov → Preproc → Link mic → Pick fil → Fit curves
→ Split fil → Subtract → Pick comp
```

When `EER` is enabled, it also starts `eer to tif`. When `Subtract twice` is enabled, it also starts the second filament-picking, curve-fitting, splitting, subtraction, and complex-picking monitors.

`Start all` does not run:

- `Merge`
- `Prep star`
- `Extract`
- `Hetero`

These steps require a completed upstream stage.

`Stop all` asks the running Subflow monitors to stop. If Subflow crashes or is closed while external RELION, crYOLO, or MPI jobs are running, those jobs may continue outside the GUI. Check them before starting the same stage again.

## Tutorial

*Expected tutorial time: 10 min*

This tutorial runs the on-the-fly steps on five example micrographs. Download the micrographs from Zenodo (link TBD) separately and save them in a directory of your choice before starting.

1. **Link mov** (not really necessary here since folders aren't nested)
   - Set input to `ExampleMovies/*.tif`.
   - Link to `Movies`.
   - Click `Link` and wait for the movies to appear.

2. **Preproc**
   - Set Movies to `Movies/*_EER.tif`.
   - Set Gain reference to `ExampleGainReference/Example_EER_GainReference.tif`.
   - Set Pixel size to 1.1.
   - Click `Preproc` to begin import, motion correction, and CTF estimation.

3. **Link mic**
   - Select `Relion motion corr job`.
   - Set `Motion correction job` to `MotionCorr/job002`.
   - Set `Micrograph suffix` to `EER`.

   *Alternatively, download the example micrographs and use `Elsewhere (wildcard)` to link them.*

   - Set `Directory to link to` to `Micrographs`.
   - Click `Link` and wait for all five micrographs to appear.
   - Click the `Link mic` tab twice to reveal the image display window. Click the `*` tab. (clicking `Link mic` again hides the tab).
      - Set `Micrograph directory` to `Micrographs`.
      - Click `Display` to start BoxManager.

      *You may need to move windows around to reveal the BoxManager file list window.*

   <img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Tutorial-01.png?raw=true" alt="Tutorial Step 1" width="300"/>

4. **Pick fil**
   - Set `Directory to pick` to `Micrographs`, pixel size to 1.1.
   - Set `crYOLO model` to `Chaaban-Carter crYOLO model for MTs 201028_model_K3_1p11apix.h5`.
   - Click `Pick` and wait for all five micrographs to be processed.
   - Click the `Pick fil` tab twice to reveal the image display window. Click the `*` tab. (clicking `Pick fil` again hides the tab).
      - Set `Micrograph directory` to `Micrographs`.
      - Click `Display picks` to start BoxManager.
      - Select `No` on the `Are the STAR files containing filament coordinates (start/end)?` popup.

      *Set Box size to 20 to better see coordinates.*

   <img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Tutorial-02.png?raw=true" alt="Tutorial Step 2" width="300"/>

5. **Fit curves**
   - Check the crYOLO STAR output, pixel size, micrograph directory, and micrograph suffix match previous steps.
   - Click `Fit` and wait for the fitted coordinates.
   - Optionally, click the `Fit curves` tab twice to check the coordinates.

   <img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Tutorial-03.png?raw=true" alt="Tutorial Step 3" width="300"/>

6. **Split fil**
   - Check the fitted STAR file location and splitting parameters.
   - Click `Split` and wait for the split coordinates.
   - Optionally, click the `Split fil` tab twice to check the coordinates.

7. **Subtract**
   - Check that the micrograph directory and directory with split filaments match the previous steps.
   - Set `Masking` to `Auto`.
   - Click `Subtract` and wait for all five subtracted micrographs.
   - Click the `Subtract` tab twice to reveal the image display window. Click the `*` tab. (clicking `Subtract` again hides the tab).
      - Set `Micrograph directory` to `SubtractedMicrographs`.
      - Click `Display subtraction` to start BoxManager.

   <img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Tutorial-04.png?raw=true" alt="Tutorial Step 4" width="300"/>

8. **Pick comp**
   - Set `Directory to pick` to `SubtractedMicrographs`, pixel size to 1.1.
   - Set `crYOLO model` to `Chaaban-Carter crYOLO model for Complex.h5`.
   - Click `Pick` and wait for all five micrographs to be processed.
   - Click the `Pick comp` tab twice to reveal the image display window. Click the `*` tab. (clicking `Pick comp` again hides the tab).
      - Set `Micrograph directory` to `Micrographs`.
      - Click `Display picks` to start BoxManager.
      - Select `No` on the `Are the STAR files containing filament coordinates (start/end)?` popup.

      *Set Box size to 20 to better see coordinates.*

   <img src="https://github.com/sami-chaaban/subflow/blob/main/screenshots/Tutorial-05.png?raw=true" alt="Tutorial Step 5" width="300"/>

## Troubleshooting

### Subflow closed during preprocessing

RELION jobs started from `Preproc` may continue after Subflow closes. Check the RELION GUI and the running processes before starting `Preproc` again. Either stop the old jobs or continue them through RELION.

### Previous parameters did not load

Make sure Subflow was started from the same project directory and that the saved parameter file still exists at the path recorded in `Subflow/subflow-last.txt`. Otherwise, use `Load parameters` to select it manually.

### cryoSPARC connection or version error

Check the cryoSPARC host, port, license, email, and password in the `Hetero` tab. The installed `cryosparc-tools` 4.6.x must match the cryoSPARC 4.6 installation.

## Citations

If you use Subflow, please cite the relevant manuscripts:

- Subflow interface - Ennio A. d’Amico, Sami Chaaban, Ferdos Abid Ali, Leon Michalski, Andrew P. Carter
bioRxiv 2026.04.25.720804; doi: https://doi.org/10.64898/2026.04.25.720804
- Multi-curve fitting and filament subtraction - Chai P, Rao Q, Zhang K. Multi-curve fitting and tubulin-lattice signal removal for structure determination of large microtubule-based motors. J Struct Biol. 2022 Dec;214(4):107897. doi: 10.1016/j.jsb.2022.107897. Epub 2022 Sep 8. PMID: 36089228; PMCID: PMC10321216.
- Relion 5.0 - Burt, A., Toader, B., Warshamanage, R., von Kügelgen, A., Pyle, E., Zivanov, J., Kimanius, D., Bharat, T. A. M., & Scheres, S. H. W. (2024). An image processing pipeline for electron cryo-tomography in RELION-5. FEBS open bio, 14(11), 1788–1804. https://doi.org/10.1002/2211-5463.13873
- crYOLO - Wagner, T., Merino, F., Stabrin, M., Moriya, T., Antoni, C., Apelbaum, A., Hagel, P., Sitsel, O., Raisch, T., Prumbaum, D., Quentin, D., Roderer, D., Tacke, S., Siebolds, B., Schubert, E., Shaikh, T. R., Lill, P., Gatsogiannis, C., & Raunser, S. (2019). SPHIRE-crYOLO is a fast and accurate fully automated particle picker for cryo-EM. Communications biology, 2, 218. https://doi.org/10.1038/s42003-019-0437-z
- cryoSPARC - Punjani, A., Rubinstein, J. L., Fleet, D. J., & Brubaker, M. A. (2017). cryoSPARC: algorithms for rapid unsupervised cryo-EM structure determination. Nature methods, 14(3), 290–296. https://doi.org/10.1038/nmeth.4169
- pyem - Asarnow, D., Palovcak, E. & Cheng, Y. asarnow/pyem: UCSF pyem v0.5. Zenodo doi:10.5281/zenodo.3576630 (2019)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
