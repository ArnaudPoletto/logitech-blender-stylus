# Logitech — Stylus LED Synthetic Data Generation
This repository contains the implementation and tools required to generate synthetic data for stylus LED movement in various scenes. The generated data includes image sequences captured by an infrared camera recording the stylus, held by a moving hand, with random objects for background noise.

## Repository Contents

- 📂 [`data/`](data): Contains rendered scenes and related data.
- 📂 [`generated/`](generated): Stores generated images and videos from the rendering process.
- 📂 [`notebooks/`](notebooks): Jupyter notebooks for exploration, visualization, and analysis.
- 📂 [`background_image/`](src/background_image): Implementation for background image handling, adding noise behind windows.
- 📂 [`blender_collections/`](src/blender_collections): Setup and implementation of Blender collections used in scenes.
- 📂 [`blender_objects/`](src/blender_objects): Implementation of Blender objects to place in the scene.
- 📂 [`config/`](src/config): Project configuration files.
- 📂 [`gestures/`](src/gestures): Implementation for generating arm gestures holding the stylus.
- 📂 [`input_data_generation/`](src/input_data_generation): Scripts and methods for generating data that describe the entire scene and the generation process.
- 📂 [`module_operators/`](src/module_operators): Implementation of operators on modules for various tasks.
- 📂 [`render/`](src/render): Implementation of the Blender rendering pipeline.
- 📂 [`utils/`](src/utils): Utility functions and scripts for various project implementations.
- 📝 [`run.py`](src/run.py): Script to execute a single scene generation.
- 📝 [`runs.py`](src/runs.py): Script to execute multiple scene generations, possibly in parallel.

## Installation Guide

### Prerequisites

1. **Blender**: Make sure Blender 4 is installed on your system.

2. **Python Packages**: Install the required Python packages inside Blender's Python environment. To do this, follow these steps:

   - Locate Blender's Python executable.
   - Open a terminal or command prompt and use the following command to install packages:
     ```sh
     blender_path/4.x/python/bin/python -m ensurepip
     blender_path/4.x/python/bin/python -m pip install <package_name>
     ```
     Replace `<package_name>` with the name of the package you want to install.

## Commands

### Single Scene Generation

To run a single instance of Blender for synthetic data generation, use the `run.py` script with the following command:

```sh
blender ../data/base_multi_new.blend --python run.py -- --render --quit
```

- `--render`: Flag indicating whether to render the animation after generating the scene. If omitted, the animation will not be rendered.
- `--quit`: Flag indicating whether to quit Blender after rendering the animation. If omitted, Blender will remain open.

### Multiple Scene Generation

To run multiple Blender instances for synthetic data generation, use the `runs.py` script with the following command:

```sh
python src/run_100.py --num-processes <num_processes> --total-processes <total_processes>
```

- `<num_processes>`: The number of processes to run in parallel.
- `<total_processes>`: The total number of processes to run.