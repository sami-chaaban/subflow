
# version 30001

data_job

_rlnJobTypeLabel             relion.import.other
_rlnJobIsContinue                       0
_rlnJobIsTomo                           0
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
        Cs        2.7 
        Q0        0.1 
    angpix        1.1 
beamtilt_x          0 
beamtilt_y          0 
  do_other        Yes 
  do_queue         No 
    do_raw         No 
fn_in_other SubtractedMicrographs-merged/*.star 
 fn_in_raw Movies/EER/GridSquare*/Data/*_EER.tif 
    fn_mtf         "" 
is_multiframe        Yes 
        kV        300 
min_dedicated         24 
 node_type "Particle coordinates (*.box, *_pick.star)" 
optics_group_name     OpticsGroup1 
optics_group_particles         "" 
other_args         "" 
      qsub     sbatch 
qsubscript /public/EM/RELION/relion-slurm-cpu-4.0.sh 
 queuename    openmpi 
 
