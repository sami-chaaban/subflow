# subflow

1. [Workflow Overview](#workflow)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Troubleshooting](#troubleshooting)
5. [License](#license)

## Workflow Overview<a name="workflow"></a>

&#8595; *on-the-fly*
* Monitors incoming files for on-the-fly processing of movies, micrographs, and particles.

* Aligns movie frames and estimates CTF values using Relion schemes (Burt et al., 2024).

* Monitors preprocessed micrographs and picks filaments using crYOLO (Wagner et al., 2020).

* Subtracts those filaments from micrographs using the lattice-subtraction scripts (Chai et al., 2022).

* Filaments are split before subtraction to reduce artefacts induced by bending.

* Allows for two rounds of filament picking and subtraction if requested.

* Picks particles from subtracted micrographs using crYOLO (Wagner et al., 2019).

* Allows viewing of micrographs and picked coordinates (if available) to monitor progress.

&#8593; *on-the-fly*

* Prepares Relion .star files with the modified paths to the subtracted micrographs.

* Extracts particles, imports them to cryoSPARC (Punjani et al., 2017).

* Performs heterogeneous refinement in cryoSPARC with user-defined volumes to extract a good class.

* Converts the particles back to Relion .star format using pyem (Asarnow et al., 2019).

## Installation<a name="installation"></a>

* Set up a fresh conda environment with Python >= 3.9: `conda create -n subflow python=3.9`

* Activate the environment: `conda activate subflow`

* Install subflow: **`pip install subflow`**

* Follow the instructions to install [Relion](https://github.com/3dem/relion) and [cryoSPARC](https://guide.cryosparc.com/)

* Install [crYOLO](https://cryolo.readthedocs.io/en/stable/index.html) and [pyem](https://github.com/asarnow/pyem) into their own anaconda environments

* Download the [multi-curve-fitting](https://github.com/PengxinChai/multi-curve-fitting) and [filament subtraction](https://github.com/PengxinChai/tubulin-lattice-subtraction) scripts.

* Edit the config.json file in the subflow installation to point to the correct crYOLO and pyem files, as well as the multi-curve-fitting and subtraction scripts

## Usage<a name="usage"></a>

Start the GUI by running the following with the conda environment active:

```
subflow &
```

![Main window](https://github.com/sami-chaaban/subflow/blob/main/examples/Main-window.png?raw=true "Main window")

* After saving parameters to a file (e.g. subflow.txt), re-opening the GUI at a later date opens the previous parameters. Saving is not automatic.

![Save parameters](https://github.com/sami-chaaban/subflow/blob/main/examples/Save-parameters.png?raw=true "Save parameters")

* Tabs with hollow cirtlces can be run on-the-fly (i.e. monitor files from the previous step). They turn into a black dot once they are running.

![Start link movies](https://github.com/sami-chaaban/subflow/blob/main/examples/Start-link-movies.png?raw=true "Start link movies")

![Start link micrographs](https://github.com/sami-chaaban/subflow/blob/main/examples/Start-link-micrographs.png?raw=true "Start link micrographs")

* Clicking twice on a tab reveals a display tab to view the resulting micrographs for that step.

![First click](https://github.com/sami-chaaban/subflow/blob/main/examples/Link-micrographs.png?raw=true "First click")

![Second click](https://github.com/sami-chaaban/subflow/blob/main/examples/View-micrographs.png?raw=true "Second click")

## Troubleshooting<a name="troubleshooting"></a>

* If Subflow crashes while Relion jobs are rerunning in the Preproc tab, they will continue to run. You can check this by running the Relion GUI. You may need to kill those jobs before being able to run Preproc again, or just continue in the Relion GUI.

* Since cryosparc-tools is set to version 4.6.0 in the installation, your cryoSPARC installation must be 4.6.0. Otherwise cryosparc-tools needs to be downgraded or upgraded.

## License<a name="license"></a>

This project is licensed under the MIT License - see the [LICENSE.txt](https://github.com/sami-chaaban/alphascreen/blob/main/LICENSE.txt) file for details.
