# Prevent numpy from using multiple threads, because we do not need to parallelize the computation and it created a lot of overhead
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

from objecttracker import run_stage

if __name__ == '__main__':
    run_stage()