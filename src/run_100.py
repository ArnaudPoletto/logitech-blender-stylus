# This script runs multiple Blender instance for synthetic data generation.
# Run this script with the following command:
# python src/run_100.py --num-processes <num_processes> --total-processes <total_processes>
# , where:
#   <num_processes> is the number of processes to run in parallel.
#   <total_processes> is the total number of processes to run.

import os
import argparse
import multiprocessing


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for Blender.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(description="Run multiple Blender instances for synthetic data generation.")

    parser.add_argument(
        "-n",
        "--num-processes",
        help="The number of processes to run.",
        type=int,
        default=1,
    )

    parser.add_argument(
        "-t",
        "--total-processes",
        help="The total number of processes to run.",
        type=int,
        default=100,
    )

    return parser


def run_instance() -> None:
    """
    Run a single Blender instance.
    """
    os.system("blender ../data/base_multi_new.blend --python run.py -- -r -q")


def main() -> None:
    """
    Run multiple Blender instances for synthetic data generation.
    """
    # Parse the arguments
    parser = get_parser()
    args = parser.parse_args()

    # Run the instances
    pool = multiprocessing.Pool(processes=args.num_processes)
    for _ in range(args.total_processes):
        pool.apply_async(run_instance)
    pool.close()
    pool.join()


if __name__ == "__main__":
    main()
