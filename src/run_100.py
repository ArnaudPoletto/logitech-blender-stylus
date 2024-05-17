import os
import argparse
import multiprocessing

def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for Blender.

    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(description="Run 100 Blender arguments.")

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

def _run_instance() -> None:
    os.system('blender ../data/base_multi_new.blend --python run.py -- -r True -q True')

def main(args) -> None:
    pool = multiprocessing.Pool(processes=args.num_processes)

    for _ in range(args.total_processes):
        pool.apply_async(_run_instance)

    pool.close()
    pool.join()

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    main(args)
