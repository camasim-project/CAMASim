# 🛠️ CAMASim
Content addressable memory (CAM) [wiki](https://en.wikipedia.org/wiki/Content-addressable_memory) stands out as an efficient hardware solution for memory-intensive search operations by supporting parallel computation in memory [intro](https://ieeexplore.ieee.org/abstract/document/9720562). 

CAMASim is a comprehensive simulation framework for evaluating content-addressable memory based accelerators in different memory-intensive CAM-compatiable application for both
application **accuracy** with hardware constraints and **hardware performance**.
We provide a Easy-to-use, Modular and Extendible package of simulating CAM-based accelerators. It comes with function simulator and performance evaluator which can be used to easily build custom search schemes. You can use it with any CAM-compatible applications with cam.write() and cam.query().

If you want to learn more info about the simulator, please refer to the following manuscript [link](https://arxiv.org/abs/2403.03442)

## Quick Start
### Get the tool from GitHub
```
git clone https://github.com/camasim-project/CAMASim.git
```
### Dependencies
The dependencies required for CAMASim are listed in `pyproject.toml`. We use [uv](https://docs.astral.sh/uv/) to manage these dependencies. You can install them by running:

1. `uv sync`
2. Followed by sourcing the virtual environment with: `. .venv/bin/activate`

### Run examples
#### Decision Tree Inference on CAM
The example/DecisionTree directory contains scripts for converting a decision tree into CAM format and performing inference with CAM, using the iris dataset. Run the command below to see performance metrics and simulation results from CAMASim:
```sh
python example/DecisionTree/example.py
```

## Integrate in your own applications
- Step 0: Prepare user-defined config. Modify cam simulation config file *cam_config* and prepare user-defined cricuit-level data in *CAMASim/performance/cost_config.json* if needed.
- Step 1: Extract stored data *CAM_Data* and query data *CAM_Query* in user-defined application.
- Step 2: Load CAM simulation config.
- Step 3: Initialize *CAMASim* class with config
- Step 4: Simulate **write** opeartion on *CAM_Data* 
- Step 5: simulate **query** opeartion *CAM_Query* 

```
# Step 2 Example
import json

def load_config():
    script_path = os.path.abspath(__file__) 
    script_dir = os.path.split(script_path)[0] 
    with open(script_dir+ '/cam_config.json', 'r') as f:
        config = json.load(f)
    return config

## Step 3-5 Example
from CAMASim.CAMASim import CAMASim

def simCAM(CAM_Data, CAM_Query):
    cam_config = load_config()
    cam = CAMASim(cam_config)
    cam.write(CAM_Data)
    CAM_pred_ids, _, _ = cam.query(CAM_Query) # Accuracy Evaluation
```


## File Description
- camasim/ 	Library source files with function simulator, layer, and device definition
- camasim/function	Function simulator and basic modules.
- camsim/performance	Performance evaluator.
- camsim/arch	Architecture estimator. (Default arch based on majority voting type arch proposed in [link](https://www.nature.com/articles/s41598-022-23116-w))
- examples/	Example for decision tree. More coming.

## Citation
If you find this code useful in your work, please cite it using the following BibTeX:

```
@misc{li2024CAMASim,
      title={CAMASim: A Comprehensive Simulation Framework for Content-Addressable Memory based Accelerators}, 
      author={M. Li and S. Liu and M.  Sharifi and X. Hu},
      year={2024},
      eprint={2403.03442},
      archivePrefix={arXiv}
}
```


## Further info on EVACAM Integration
### What is EVACAM
Eva-CAM is a *circuit/architecture-level* modeling and evaluation tool for content addressable memories (CAMs) that can project the area, timing, dynamic energy, and leakage power of NVM-based CAMs. Please go to [EVACAM github repository](https://github.com/eva-cam/EvaCAM) for more detailed information.

### Why CAMASim and EVACAM can Work Together?
CAMASim is an chip-level performance and application accuracy simulator while EVACAM gives detailed hardware costs, therefore the two simulators are perfectly  complementary to each other and can work together to give better results. When EVACAM is enabled, CAMASim will pass the CAM configuration it received to EVACAM, and read from EVACAM's performance evaluation on power and latency for whole-chip performance evaluation. 

If EVACAM is not enabled, CAMASim will read from user-defined performance data for specific CAM configurations, which should be stored in `CAMASim/performance/cost_config.json`. In the repo, we also provide FeFET-based TCAM and MCAM SPICE simulation results. 

### How to enable EVACAM?
EVACAM is integrated as a git submodule within CAMASim to enhance functionality. To align with CAMASim's requirements, we've forked and slightly modified the original EVACAM, with our adapted version available at [this repo](https://github.com/Andyliu92/EvaCAM-for-CAMASim).

```sh
git submodule init
git submodule update
```

To activate EVACAM's features during simulations in CAMASim, include "useEVACAMCost": true within the array section of your CAM simulation's configuration file. For instance, in the decision tree example (`example/DecisionTree/cam_config.json`), adjust the array section as follows:

```json
    "array":{
        "row": 128,
        "col": 128,
        "sensing": "exact",
        "cell": "ACAM",
        "bit": 3,
        "useEVACAMCost": true
    },
```
This setup allows CAMASim to utilize EVACAM's evaluations of latency and power for more accurate simulation outcomes. Please note that EVACAM is written in C/C++. Compilation of is needed for the first run of EVACAM. We use `g++` to compile. Please make sure that `g++` is available in your environment.
