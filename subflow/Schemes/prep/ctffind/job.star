
# version 30001

data_job

_rlnJobTypeLabel             relion.ctffind.ctffind4
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
       box        512 
   ctf_win         -1 
      dast        500 
     dfmax      40000 
     dfmin       2000 
    dfstep        500 
    do_EPA         No 
do_ignore_ctffind_params        Yes 
do_phaseshift         No 
  do_queue         Yes 
fn_ctffind_exe /public/EM/ctffind/ctffind.exe
fn_gctf_exe /public/EM/Gctf/bin/Gctf
   gpu_ids         "" 
input_star_mics MotionCorr/job002/corrected_micrographs.star
min_dedicated         24 
    nr_mpi          112 
other_args         "" 
other_gctf_args         "" 
 phase_max        180 
 phase_min          0 
phase_step         10 
      qsub       sbatch 
qsubscript /public/EM/RELION/relion-slurm-cpu-5.0.sh 
 queuename    openmpi 
    resmax          5 
    resmin         30 
slow_search         Yes 
use_ctffind4        Yes 
  use_gctf         No 
use_given_ps        Yes 
  use_noDW        No 
 
