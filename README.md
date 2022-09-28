![image](https://user-images.githubusercontent.com/64599697/191536989-b798cdc8-6c96-4e8c-88b2-5422c033882c.png)

# Large-Scale Route Optimization Accelerator

This accelerator provides the code template to solve large-scale route optimization where the optimal solution cannot be found in reasonable time. A real world scenario is used to demontrate the use of the accelerator. The implementation leverages Azure ML to create a general optimization framework where the large-scale route optimization problem is partitioned into many smaller problems. Each smaller problem can then be solved in parallel by any optimization solver. At the end, the results from all smaller problems will be merged into the final result. 

![image](https://user-images.githubusercontent.com/64599697/191935065-15316f45-5905-4c24-a533-658c610f8c48.png)


<!-- # Overview

This repository contains the base repository for developing route optimization, where you can accelerate parallel computation using `ParallelRunStep` class. -->

## Challenges for Optimization Problem

There are some common challenges for creating a production-grade optimization application:
1. Most optimization problems are [NP-hard](https://en.wikipedia.org/wiki/NP-hardness) (route optimization falls into this category). When the scale of the problem becomes large, it is impossible to find any good solution in a reasonable time.
2. The constraints in an optimization problem may change over time as the customer's business evolves. This creates the burden for maintaining the optimization application. 
3. Deploying the optimization application in a way that can be easy to consume by the other applications is crucial.

To tackle challenge 1 and 3, in this accelarator, we will demonstrate an optimization framework using Azure ML that applies partitioning strategy to partition the large-scale route optimization problem into many smaller ones and then solve them individually. This is a practical way to solve any real-world large-scale optimization problem. We will also leverage Azure ML to deploy the optimization application as a REST API such that it can be easy to consume by other applications. 

A pure rule-based optimization application is difficult to maintain as the constraints of the problem change. A better way to tackle that is to leverage [optimization solver](https://en.wikipedia.org/wiki/List_of_optimization_software) to model the problem and then let the solver search the solution automactically. There are many optimization techniques, e.g., Linear Programming , Mixed Integer Programming, Constraint Programming. One can choose the best fit for their own problem. In thie template, we demonstrate how to use Constraint Programming to model the route optimization problem.   

## Route Optimization Example - A real customer scenario


# Solution Design


## Prerequisite


## Getting Started

1. Create environment

    Please follow the instruction with [the notebook for provisioning](./notebook/provisioning.ipynb), where you need to set up Azure environment, environmental variables, python environment, and Azure ML set-up.

2. Understand the contents

    You can understand the whole pipeline with [the notebook for aml pipeline](./notebook/aml_pipeline.ipynb).

## Code structure

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
│   │   ├── ./src/core/merger.py          # Defines logic for merging the partitioned problem result
│   │   ├── ./src/core/model.py           # Defines the modelling logic and the core optimizaiton problem
│   │   ├── ./src/core/partitioner.py     # Defines the partition strategy
│   │   ├── ./src/core/reducer.py         # Defines any heuristic for search space reduction
│   │   └── ./src/core/structure.py       # Defines basic data structure
│   ├── ./src/merge.py                    # Wrapping script for merge process
│   ├── ./src/partition.py                # Wrapping script for partition process
│   ├── ./src/reduce.py                   # Wrapping script for reduce process
│   └── ./src/solve.py                    # Wrapping script for solve process
└── ./tests
    └── ./tests/core                      # Test codes for each process
```


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
