import subprocess
import time

"""
Definiton of the input parameter
"""
jobStartNumber = 1

# tv_eps, tv_epsp, tv_alpha, tv_beta, tv_weight, tv_lr, tv_iters
parameter = [
    [0.01, 0.005, 0.4, 1.4, 0.1, 0.5, 150]
]

# output dir name
dataDir = "Relion-luo"

# refine3d input
particleStar = "particles.star"
initialModel = "job005_it280_class004.mrc"
iniHigh = "20"
particleDiameter = "200"
symmetry = "C1"
angpix = "1.35"
useAdaptiveFraction = True
adaptiveFraction = "0.9"

# maskcreate input
iniThreshold = "0.01"

# postprocess input
useMtfFile = False
mtfFile = "falcon_mtf_300kv.star"


def executeSubProcess(command=[], logDir="", jobName=""):
    p = subprocess.run(args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    with open(logDir + "/" + jobName, "w") as f:
        f.writelines(p.stdout)
    if p.returncode == 0:
        print(time.asctime(), f"\t{jobName} executed successfully!")
    else:
        print(time.asctime(), f"\tError in {jobName}! Please check the log.")


def commandContent(jobStartNumber, parameter):
    for i in range(len(parameter)):
        job = str(jobStartNumber + i)
        if jobStartNumber + i < 10:
            job = "0" + job
        mkDir = [
            "mkdir",
            "-p",
            f"{dataDir}/job0{job}"
        ]
        refine3D = [
            "mpirun",
            "--allow-run-as-root",
            "-n",
            "5",
            "/relion-luo/build/bin/relion_refine_mpi",
            "--o",
            f"{dataDir}/job0{job}/run",
            "--auto_refine",
            "--split_random_halves",
            "--i", 
            f"{particleStar}",
            "--ref",
            f"{initialModel}",
            "--ini_high", 
            f"{iniHigh}",
            "--dont_combine_weights_via_disc",
            "–no_parallel_disc_io",
            "--pool",
            "3",
            "--ctf",
            "--ctf_corrected_ref",
            "--iter",
            "25",
            "--tau2_fudge",
            "4",
            "--particle_diameter",
            f"{particleDiameter}",
            "--flatten_solvent",
            "--zero_mask",
            "--oversampling",
            "1",
            "--healpix_order",
            "2",
            "--auto_local_healpix_order",
            "4",
            "--offset_range",
            "5",
            "--offset_step",
            "2",
            "--sym",
            f"{symmetry}",
            "--low_resol_join_halves",
            "50",
            "--norm",
            "--scale",
            "--j",
            "8",
            "--gpu",
            "0,1,2,3",
            "--angpix",
            f"{angpix}",
            "--tv_eps",
            f"{parameter[i][0]}",
            "--tv_epsp",
            f"{parameter[i][1]}",
            "--tv_alpha",
            f"{parameter[i][2]}",
            "--tv_beta",
            f"{parameter[i][3]}",
            "--tv_weight",
            f"{parameter[i][4]}",
            "--tv_lr",
            f"{parameter[i][5]}",
            "--tv_iters",
            f"{parameter[i][6]}",
            "--tv"
        ]
        if useAdaptiveFraction:
            refine3D.append("--adaptive_fraction")
            refine3D.append(f"{adaptiveFraction}")

        maskCreate = [
            "/relion-luo/build/bin/relion_mask_create",
            "--i",
            f"{dataDir}/job0{job}/run_class001.mrc",
            "--o",
            f"{dataDir}/job0{job}/mask.mrc",
            "--ini_threshold",
            f"{iniThreshold}",
            "--width_soft_edge",
            "6",
            "--lowpass",
            "15",
            "--extend_inimask",
            "2",
            "--angpix",
            f"{angpix}"
        ]

        postProcess = [
            "/relion-luo/build/bin/relion_postprocess",
            "--i",
            f"{dataDir}/job0{job}/run",
            "--mask",
            f"{dataDir}/job0{job}/mask.mrc",
            "--angpix",
            f"{angpix}",
            "--o",
            f"{dataDir}/job0{job}/postprocess",
            "--auto_bfac",            
        ]
        if useMtfFile:
            postProcess.append("--mtf")
            postProcess.append(f"{mtfFile}")
        
        yield job, mkDir, refine3D, maskCreate, postProcess


if __name__ == "__main__":
    logDirJobNumber = str(jobStartNumber)
    if jobStartNumber < 10:
        logDirJobNumber = "0" + logDirJobNumber
    logDir = f"ScheduleLogJob0{logDirJobNumber}"
    mkLogDir = subprocess.run(args=["mkdir", logDir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    print(time.asctime(), f"\tlog files will be saved in ScheduleLogJob0{jobStartNumber}")
    for job, mkDir, refine3D, maskCreate, postProcess in commandContent(jobStartNumber, parameter):
        executeSubProcess(command=mkDir, logDir=logDir, jobName=f"mkdirJob0{job}")
        executeSubProcess(command=refine3D, logDir=logDir, jobName=f"refineJob0{job}")
        executeSubProcess(command=maskCreate, logDir=logDir, jobName=f"maskJob0{job}")
        executeSubProcess(command=postProcess, logDir=logDir, jobName=f"postprocessJob0{job}")
        print(time.asctime(), f"\tJob0{job} has been completed.")