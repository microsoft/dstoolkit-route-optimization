![image](https://user-images.githubusercontent.com/64599697/191536989-b798cdc8-6c96-4e8c-88b2-5422c033882c.png)

# Large-Scale Route Optimization Accelerator

This accelerator provides the code template to solve large-scale route optimization where the optimal solution cannot be found in reasonable time. A real world scenario is used to demontrate the use of the accelerator.

<!-- # Overview

This repository contains the base repository for developing route optimization, where you can accelerate parallel computation using `ParallelRunStep` class. -->

# TBA


# Getting Started

1. Create environment

    Please follow the instruction with [the notebook for provisioning](./notebook/provisioning.ipynb), where you need to set up Azure environment, environmental variables, python environment, and Azure ML set-up.

2. Understand the contents

    You can understand the whole pipeline with [the notebook for aml pipeline](./notebook/aml_pipeline.ipynb).

# Code structure

```sh
├── ./notebook
│   ├── ./notebook/aml_pipeline.ipynb     # Notebook for optimization algorithm
│   └── ./notebook/provisioning.ipynb     # Notebook for preparing environment
├── ./requirements.txt                    # Defines required libraries in Python
├── ./sample_data
│   ├── ./sample_data/distance.csv        # Sample data defining distances between places
│   ├── ./sample_data/order_large.csv     # Sample data defining customers' orders
│   └── ./sample_data/order_small.csv     # Small sample data defining customers' orders
├── ./src
│   ├── ./src/core
│   │   ├── ./src/core/logger.py          # Defines logging features
│   │   ├── ./src/core/merger.py          # Defines merge process after divided optimization results
│   │   ├── ./src/core/model.py           # Defines dividing the whole orders into smaller chunks
│   │   ├── ./src/core/partitioner.py     # TBA
│   │   ├── ./src/core/reducer.py         # TBA
│   │   └── ./src/core/structure.py       # Defines basic data structure
│   ├── ./src/merge.py                    # Wrapping script for merge process
│   ├── ./src/partition.py                # Wrapping script for partition process
│   ├── ./src/reduce.py                   # Wrapping script for reduce process
│   └── ./src/solve.py                    # Wrapping script for solve process
└── ./tests
    └── ./tests/core                      # Test codes for each process
```


# Project

> This repo has been populated by an initial template to help get you started. Please
> make sure to update the content to build a great experience for community-building.

As the maintainer of this project, please make a few updates:

- Improving this README.MD file to provide a great experience
- Updating SUPPORT.MD with content about this project's support experience
- Understanding the security reporting process in SECURITY.MD
- Remove this section from the README

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
