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

<img src="https://github.com/sami-chaaban/subflow/blob/main/examples/Subtracted-example.png?raw=true" alt="Subtracted example" width="600"/>

## Installation<a name="installation"></a>

* Set up a fresh conda environment with Python >= 3.9: `conda create -n subflow python=3.9`

* Activate the environment: `conda activate subflow`

* Install subflow: **`pip install subflow`**

* Follow the instructions to install [Relion](https://github.com/3dem/relion) and [cryoSPARC](https://guide.cryosparc.com/)

* Install [crYOLO 1.9.1](https://cryolo.readthedocs.io/en/stable/index.html) and [pyem](https://github.com/asarnow/pyem) into their own anaconda environments

* Download the [multi-curve-fitting](https://github.com/PengxinChai/multi-curve-fitting) and [filament subtraction](https://github.com/PengxinChai/tubulin-lattice-subtraction) scripts.

* Edit the config.json file in the subflow installation to point to the correct crYOLO and pyem files, as well as the multi-curve-fitting and subtraction scripts

## Usage<a name="usage"></a>

Start the GUI by running the following with the conda environment active:

```
subflow &
```

<img src="https://github.com/sami-chaaban/subflow/blob/main/examples/Main-window.png?raw=true" alt="Main window" width="600"/>

* After saving parameters to a file (e.g. subflow.txt), re-opening the GUI at a later date opens the previous parameters. Saving is not automatic.

<img src="https://github.com/sami-chaaban/subflow/blob/main/examples/Save-parameters.png?raw=true" alt="Save parameters" width="600"/>

* Tabs with hollow circles can be run on-the-fly (i.e. monitor files from the previous step). They turn into a black dot once they are running.

<img src="https://github.com/sami-chaaban/subflow/blob/main/examples/Start-link-movies.png?raw=true" alt="Start link movies" width="600"/>

* Clicking twice on a tab toggles the following `*` display tab to view results for that step.

<img src="https://github.com/sami-chaaban/subflow/blob/main/examples/Link-micrographs.png?raw=true" alt="First click" width="600"/>

<img src="https://github.com/sami-chaaban/subflow/blob/main/examples/View-micrographs.png?raw=true" alt="Second click" width="600"/>

**Tab Order**
1. `SUBFLOW` — Global settings: config path, `EER` toggle, `Subtract twice` toggle, load/save parameters, start/stop all.
1. `Link mov` — Link incoming movies into the working directory.
1. `eer to tif` — Convert EER stacks to TIFF (run if using EER).
1. `Preproc` — Relion import, motion correction, and CTF estimation.
1. `Link mic` — Link corrected micrographs into `Micrographs`.
1. `*` (Display micrographs) — QC linked micrographs.
1. `Pick fil` — crYOLO filament picking on micrographs.
1. `*` (Display picks) — QC filament picks.
1. `Fit curves` — Multi-curve fitting on filament picks.
1. `*` (Display fit) — QC fitted curves.
1. `Split fil` — Split fitted filaments into shorter segments.
1. `*` (Display splits) — QC split results.
1. `Subtract` — Lattice subtraction using split filaments.
1. `*` (Display subtraction) — QC subtracted micrographs (optionally overlay split coords).
1. `Pick comp` — crYOLO picking of complexes on subtracted micrographs.
1. `*` (Display comp picks) — QC complex picks.

The next block appears only when `Subtract twice` is enabled in `SUBFLOW`:
1. `Pick fil` (round 2) — Filament picking on the first subtraction.
1. `*` (Display picks) — QC filament picks (round 2).
1. `Fit curves` (round 2) — Curve fitting (round 2).
1. `*` (Display fit) — QC fit results (round 2).
1. `Split fil` (round 2) — Split filaments (round 2).
1. `*` (Display splits) — QC split results (round 2).
1. `Subtract` (round 2) — Second subtraction pass.
1. `*` (Display subtraction) — QC subtracted micrographs (round 2).
1. `Pick comp` (round 2) — Complex picking on round-2 subtractions.
1. `*` (Display comp picks) — QC complex picks (round 2).

1. `Merge` — Merge sequential subtractions and/or complex picks (used with double subtraction).
1. `Prep star` — Fix micrograph `.star` paths to subtracted micrographs and link picks into that directory.
1. `Extract` — Relion import + extract particles from the subtracted micrographs.
1. `Hetero` — cryoSPARC workspace, import particles/volumes, heterogeneous refinement.

## Troubleshooting<a name="troubleshooting"></a>

* If Subflow crashes while Relion jobs are running in the Preproc tab, they will continue to run. You can check this by checking the Relion GUI. You may need to kill those jobs before being able to run Preproc again, or just continue in the Relion GUI.

* Since cryosparc-tools is set to version 4.6.0 in the installation, your cryoSPARC installation must be 4.6.0. Otherwise cryosparc-tools needs to be downgraded/upgraded.

## License<a name="license"></a>

This project is licensed under the MIT License - see the [LICENSE.txt](https://github.com/sami-chaaban/alphascreen/blob/main/LICENSE.txt) file for details.
