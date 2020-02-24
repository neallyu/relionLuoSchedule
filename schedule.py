import subprocess
import time

"""
Definiton of the input parameter
"""
jobStartNumber = 2

# tv_alpha, tv_beta
parameter = [
    [0.5, 1.7],
    [0.5, 1.4],
    [0.5, 1.2]
]

dataDir = "Refine3D"


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
            f"Refine3D/job0{job}/run",
            "--auto_refine",
            "--split_random_halves",
            "--i", 
            "particles1.star",
            "--ref",
            "run_it025_class003.mrc",
            "--ini_high", 
            "50",
            "--dont_combine_weights_via_disc",
            "–no_parallel_disc_io",
            "--pool",
            "3",
            "--ctf",
            "--ctf_corrected_ref",
            "--particle_diameter",
            "200",
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
            "D2",
            "--low_resol_join_halves",
            "50",
            "--norm",
            "--scale",
            "--j",
            "8",
            "--gpu",
            "0,1,2,3",
            "--angpix",
            "1.77",
            "--tv_alpha",
            f"{parameter[i][0]}",
            "--tv_beta",
            f"{parameter[i][1]}",
            "--tv_weight",
            "0.05",
            "--tv_lr",
            "0.5",
            "--tv_iters",
            "150",
            "--tv"
        ]
        maskCreate = [
            "/relion-luo/build/bin/relion_mask_create",
            "--i",
            f"Refine3D/job0{job}/run_class001.mrc",
            "--o",
            f"Refine3D/job0{job}/mask.mrc",
            "--ini_threshold",
            "0.02",
            "--width_soft_edge",
            "6",
            "--lowpass",
            "15",
            "--extend_inimask",
            "2",
            "--angpix",
            "1.77"
        ]
        postProcess = [
            "/relion-luo/build/bin/relion_postprocess",
            "--i",
            f"Refine3D/job0{job}/run",
            "--mask",
            f"Refine3D/job0{job}/mask.mrc",
            "--angpix",
            "1.77",
            "--o",
            f"Refine3D/job0{job}/postprocess",
            "--auto_bfac"
        ]
        yield job, mkDir, refine3D, maskCreate, postProcess


if __name__ == "__main__":
    logDir = f"ScheduleLogJob0{jobStartNumber}"
    mkLogDir = subprocess.run(args=["mkdir", logDir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    print(time.asctime(), f"\tlog files will be saved in ScheduleLogJob0{jobStartNumber}")
    for job, mkDir, refine3D, maskCreate, postProcess in commandContent(jobStartNumber, parameter):
        executeSubProcess(command=mkDir, logDir=logDir, jobName=f"mkdirJob0{job}")
        executeSubProcess(command=refine3D, logDir=logDir, jobName=f"refineJob0{job}")
        executeSubProcess(command=maskCreate, logDir=logDir, jobName=f"maskJob0{job}")
        executeSubProcess(command=postProcess, logDir=logDir, jobName=f"postprocessJob0{job}")
        print(time.asctime(), f"\tJob0{job} has been completed.")