import subprocess

"""
Definiton of the input parameter
"""
jobStartNumber = 54

# tv_alpha, tv_beta
parameter = [
    [0.5, 1.4],
    [0.5, 1.2]
]


def executeSubProcess(command=[], jobName=""):
    p = subprocess.run(args=command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    with open(jobName, "w") as f:
        f.writelines(p.stdout)
    if p.returncode == 0:
        print(f"{jobName} executed successfully!")
    else:
        print(f"Error in {jobName}! Please check the log.")


def commandContent(jobStartNumber, parameter):
    for i in range(len(parameter)):
        job = jobStartNumber + i
        mkDir = [
            "mkdir",
            f"Refine3D/job0{job}"
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
    for job, mkDir, refine3D, maskCreate, postProcess in commandContent(jobStartNumber, parameter):
        executeSubProcess(command=mkDir, jobName=f"mkdir_job0{job}")
        executeSubProcess(command=refine3D, jobName=f"refine_job0{job}")
        executeSubProcess(command=maskCreate, jobName=f"mask_job0{job}")
        executeSubProcess(command=postProcess, jobName=f"postprocess_job0{job}")
        print(f"job0{job} has been finished")