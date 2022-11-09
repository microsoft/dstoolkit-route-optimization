![image](https://user-images.githubusercontent.com/64599697/191536989-b798cdc8-6c96-4e8c-88b2-5422c033882c.png)

# Large-Scale Route Optimization Accelerator

This accelerator provides the code template for solving large-scale route optimization problems. The accelerator implements a scalable optimization approach that partitions a large optimization problem into smaller problems, and solves those reduced optimization problems in parallel by leveraging Azure Machine Learning. The solutions to the smaller problems are then consolidated to form a feasible solution to the original optimization problem. A real-world route optimization scenario is used as an example to demonstrate the use of the accelerator.

![image](https://user-images.githubusercontent.com/64599697/191935065-15316f45-5905-4c24-a533-658c610f8c48.png)



<!-- ## Challenges for Optimization Application

There are some common challenges for creating a production-grade optimization application:
1. Most optimization problems are [NP-hard](https://en.wikipedia.org/wiki/NP-hardness) (route optimization falls into this category). When the scale of the problem becomes large, it is impossible to find any good solution in a reasonable time.
2. The constraints in an optimization problem may change over time as the customer's business evolves. This creates the burden for maintaining the optimization application. 
3. Deploying the optimization application in a way that can be easy to consume by other applications is also crucial in practice.

To tackle challenge 1 and 3, in this accelerator, we will demonstrate an optimization framework using Azure ML that applies partitioning strategy to partition the large-scale route optimization problem into many smaller ones and then solve them individually. This is a practical way to solve any real-world large-scale optimization problem. We will also leverage Azure ML to deploy the optimization application as a REST API such that it can be easy to consume by other applications. 

A pure rule-based optimization application is difficult to maintain as the constraints of the problem change. A better way to tackle challenge 2 is to leverage [optimization solver](https://en.wikipedia.org/wiki/List_of_optimization_software) to model the problem and then let the solver search the solution automatically. There are many optimization techniques, e.g., Linear Programming (LP), Mixed Integer Programming (MIP), [Constraint Programming](https://en.wikipedia.org/wiki/Constraint_programming), etc. One can choose the best fit for their own problem since the framework introduced in this accelerator is optimization technique agnostic. In this accelerator, we demonstrate how to use Constraint Programming to model the route optimization problem.   

Comparing to mathematical optimization techniques (e.g., LP, MIP), Constraint Programming is more expressive since it allows us to express a larger collection of problems. For example, a constraint programming model has no limitation on the arithmetic constraints that can be set on decision variables, while a mathematical programming engine is specific to a class of problems whose formulation satisfies certain mathematical properties (for example: quadratic, MIQCP, and convex vs non-convex).

Besides, Constraint programming is also an efficient approach to solve and optimize problems that are too irregular for mathematical optimization. This includes time tabling problems, sequencing problems, and allocation or rostering problems.

The reasons for these irregularities that make the problem difficult to solve for mathematical optimization can be:
* Constraints that are nonlinear in nature
* A non convex solution space that contains many locally optimal solutions
* Multiple disjunctions, which result in poor information returned by a linear relaxation of the problem

To who is interested in the detailed comparison, one can refer to this [link](https://www.ibm.com/docs/en/icos/12.8.0.0?topic=overview-constraint-programming-versus-mathematical-programming).  -->

## Route Optimization - A Real World Scenario

The example demonstrated in this solution accelerator is inspired by a real-world optimization scenario. The customer is a manufacturing company. They have warehouses in different locations. When they receive orders from their clients, a planner need to plan the item-to-truck assignment for order delivery. The planner also need to decide the route of each delivery truck, namely, the sequence of the stops to deliver orders to different destinations. A delivery assignment has its associated cost determined by the type of the assigned delivery truck and the corresponding travelling distance. The optimization objective here is to minimize the overall delivery cost. 

This is a variant of the [vehicle routing problem (VRP)](https://en.wikipedia.org/wiki/Vehicle_routing_problem). The constraints modeled in our example are:
1. There are different types of trucks we can choose from. A truck has capacity limit on both area and weight. (We assume that there is no limit on the number of trucks for each type)
2. An item is only available by a specific time. A truck can start only when all items assigned to it are available.
3. The available time difference between the earliest and last available items in the same truck should be less than a user defined limit (e.g., 4 hours).  
4. All items need to be delivered to their destinations before their deadlines.
5. Depending on the properties of products, some items can put in the same truck, but some cannot.
6. A truck can have at most N stops, where N is a user defined number.
7. A truck need to stay at each stop for M hours to unload the items, where M is a user defined number. Each stop will incur a fixed amount of cost in addition to the delivery cost. 

### Example Input

Below shows an example input of the route optimization problem. It is a set of items to be delivered, where the Item_ID uniquely defines an item.
 | Order_ID | Material_ID | Item_ID | Source | Destination | Available_Time | Deadline | Danger_Type | Area (m^2) | Weight (kg) |
 | ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- | --------------| --------------|
 | A140109 | B-6128 | P01-79c46a02-e12f-41c4-9ec9-25e48597ebfe | City_61 | City_54 | 2022-04-05 23:59:59 | 2022-04-11 23:59:59 | type_1 | 3.888 | 3092 | 
 | A140112 | B-6128 | P01-84ac394c-9f34-48e7-bd15-76f92120b624 | City_61 | City_54 | 2022-04-07 23:59:59 | 2022-04-13 23:59:59 | type_1 | 3.888 | 3092 | 
 | A140112 | B-6128 | P01-b70c94db-630a-497b-bb63-b0ad86a7dce6 | City_61 | City_54 | 2022-04-07 23:59:59 | 2022-04-13 23:59:59 | type_1 | 3.888 | 3092 | 
<!--  | A140112 | B-6128 | P01-4534a7e8-6d73-4a2e-8363-a6645d9bc345 | City_61 | City_54 | 2022-04-07 23:59:59 | 2022-04-13 23:59:59 | type_1 | 38880 | 30920000 | 
 | A140112 | B-6128 | P01-7208eb61-2cc1-4e7c-b698-e1ab2327b658 | City_61 | City_54 | 2022-04-07 23:59:59 | 2022-04-13 23:59:59 | type_1 | 38880 | 30920000 | 
 | A190223 | B-6155 | nan-4ac2f30e-bc0a-4415-8612-a6b38d833317 | City_61 | City_53 | 2022-04-06 23:59:59 | 2022-04-12 23:59:59 | type_2 | 9840 | 7640000 | 
 | A190225 | B-6155 | nan-5ae70ea9-a28e-4107-b267-5a6c84d4a3c7 | City_61 | City_53 | 2022-04-05 23:59:59 | 2022-04-11 23:59:59 | type_2 | 9840 | 7640000 | 
 | A190226 | B-6155 | nan-c9658637-b5f1-433d-885e-b3008612a73d | City_61 | City_53 | 2022-04-07 23:59:59 | 2022-04-13 23:59:59 | type_2 | 9840 | 7640000 | 
 | A190226 | B-6155 | nan-75768ff3-3dde-4952-9aa0-594c373421d1 | City_61 | City_53 | 2022-04-07 23:59:59 | 2022-04-13 23:59:59 | type_2 | 9840 | 7640000 | 
 | A190226 | B-6155 | nan-39cdd29b-baee-4ed6-bec0-33227cc8608d | City_61 | City_53 | 2022-04-07 23:59:59 | 2022-04-13 23:59:59 | type_2 | 9840 | 7640000 |  -->

 
Also assume there are 3 types of trucks available for assignment:
 | Truck Type (length in m) | Inner Size (m^2) | Weight Capacity (kg) | Cost Per KM | Speed (km/h) |
 | ----------- | ----------- | --------------|----------- |----------- |
 | 16.5 | 16.1x2.5 | 10000 | 3 | 40 |  
 | 12.5 | 12.1x2.5 | 5000 | 2 | 40 | 
 | 9.6 | 9.1x2.3 | 2000 | 1 | 40 | 
 
 ### Example Output

Below is an example output of the route assignment, where Truck_ID uniquely defines a truck. The column Shared_Truck indicates if there are items from different orders sharing the same truck.
| Truck_ID  |  Truck_Route  |  Order_ID  |  Material_ID  |  Item_ID  |  Danger_Type  |  Source  |  Destination  |  Start_Time  |  Arrival_Time  |  Deadline  |  Shared_Truck  |  Truck_Type  | 
| ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- | --------------| --------------| ----------- | --------------| --------------|
| d27e70e3-e143-4419-8c4a-2faf130e29b3  |  City_61->City_54  |  A140109  |  B-6128  |  P01-79c46a02-e12f-41c4-9ec9-25e48597ebfe  |  type_1  |  City_61  |  City_54  |  2022-04-05 23:59:59  |  2022-04-08 13:11:46  |  2022-04-11 23:59:59  |  N  |  9.6  | 
| 7fb70614-64c5-4d40-a8a2-2f6e39205a67  |  City_61->City_54  |  A140112  |  B-6128  |  P01-84ac394c-9f34-48e7-bd15-76f92120b624  |  type_1  |  City_61  |  City_54  |  2022-04-07 23:59:59  |  2022-04-10 13:11:46  |  2022-04-13 23:59:59  |  N  |  9.6  | 
| 7fb70614-64c5-4d40-a8a2-2f6e39205a67  |  City_61->City_54  |  A140112  |  B-6128  |  P01-b70c94db-630a-497b-bb63-b0ad86a7dce6  |  type_1  |  City_61  |  City_54  |  2022-04-07 23:59:59  |  2022-04-10 13:11:46  |  2022-04-13 23:59:59  |  N  |  9.6  | 



<!-- With the help of Constraint Programming, we can model all these constraints programmatically. There are a lot of CP solvers we can pick. In this accelerator, we use [Google OR-Tools](https://developers.google.com/optimization). It is open-sourced and its performance [surpasses many other solvers](https://www.minizinc.org/challenge2022/results2022.html). To learn about how to model a problem using CP in OR-Tools, one can refer to its [API documents](https://developers.google.com/optimization/reference/python/sat/python/cp_model). -->

# Solution Design

The key idea of this accelerator is to implement a general framework (illustrated by the below figure) for solving large-scale route optimization problems. The end-to-end pipeline is implemented using Azure ML pipeline consisting of 4 key steps. The complete definition of the pipeline can be found in this [notebook](./notebook/aml_pipeline.ipynb).

![image](docs/media/pipeline.png)

We use the following simplified example to illustrate the above steps.
Assume we have a set of orders as below, where we group same type (namely, having same Material_ID) of items from the same order as a single record for ease of discussion.

| Order_ID | Material_ID | Number_of_items | Weight_Per_Item | Source | Destination | Available_Time | Deadline |
| ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- |
| 1 | A | 8 | 2t | S1 | D1 | 2022-08-01 7AM | 2022-08-02 |
| 2 | B | 15 | 1t | S1 | D2 | 2022-08-01 9AM | 2022-08-03 |
| 3 | C | 18 | 1t | S1 | D3 | 2022-08-01 10AM | 2022-08-04 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| 300 | AA | 33 | 1t | S1 | D1 | 2022-08-02 10AM | 2022-08-04 |

## Step 1: Reduce the Search Space

For large-scale route optimization problems, it is often possible to apply human heuristics to pre-assign a subset of the items, effectively reducing the problem size. In some cases, we can easily find an optimal/near-optimal assignment based on simple heuristics. For example, in the above route optimization scenario, there are different types of trucks we can choose from. Among them, the biggest truck (i.e., the 10t one) is most cost effective. A simple heuristic is to fill up the biggest truck with items of the same destination. This assignment incurs the lowest delivery cost for those items. 

For example, we can apply the above heuristic to our original input and obtain the following two outcomes:
* a partial result that contains the heuristic assignment:

| Schedule_ID | Order_ID | Material_ID | Number_of_Items | Source | Destination | Truck_Type |
| --------------|----------- | ----------- | --------------| ----------- | ----------- | ----------- |
| 1 | 1 | A | 5 | S1 | D1 | 10t |
| 2 | 2 | B | 10 | S1 | D2 | 10t |
| 3 | 3 | C | 10 | S2 | D3 | 10t |
| ... | ... | ... | ... | ... | ... | ... |
| 100 | 300 | AA | 10 | S1 | D1 | 10t |
| 101 | 300 | AA | 10 | S1 | D1 | 10t |
| 102 | 300 | AA | 10 | S1 | D1 | 10t |

* the remaining unassigned items as the input for the partition step (you may compare it with the original input of the reduce step):

| Order_ID | Material_ID | Number_of_Items | Weight_Per_Item | Source | Destination | Available_Time | Deadline |
| ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- |
| 1 | A | 3 | 2t | S1 | D1 | 2022-08-01 7AM | 2022-08-02 |
| 2 | B | 5 | 1t | S1 | D2 | 2022-08-01 9AM | 2022-08-03 |
| 3 | C | 8 | 1t | S1 | D3 | 2022-08-01 10AM | 2022-08-04 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| 300 | AA | 3 | 1t | S1 | D1 | 2022-08-02 10AM | 2022-08-04 |

## Step 2: Partition the Problem

Given the reduced problem from step 1, we can apply different partition strategies to further reduce the problem space. The objective is to ensure each single partition is small enough to solve within a user defined time limit. In an ideal case, the chosen partitioning strategy should not change the optimum of the original problem. Using the above route optimization problem as an example, partitioning the items by the delivery source as below will not change the optimum of the original problem: 

* items starting from Source S1:

| Order_ID | Material_ID | Number_of_Items | Weight_Per_item | Source | Destination | Available_Time | Deadline |
| ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- |
| 1 | A | 3 | 2t | S1 | D1 | 2022-08-01 7AM | 2022-08-02 |
| 2 | B | 5 | 1t | S1 | D2 | 2022-08-01 9AM | 2022-08-03 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| 300 | AA | 3 | 1t | S1 | D1 | 2022-08-02 10AM | 2022-08-04 |

* items starting from Source S2:

| Order_ID | Material_ID | Number_of_Items | Weight_Per_Item | Source | Destination | Available_Time | Deadline |
| ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- |
| 3 | C | 8 | 1t | S1 | D3 | 2022-08-01 10AM | 2022-08-04 |
| ... | ... | ... | ... | ... | ... | ... | ... |

In the case where there are a lot of items from the same source, you may need to further partition those items such that individual problems can be solved within a given time limit. The optimality may not be guaranteed in this case. 

For example, we can further partition items from source S1 by Available_Time. The intuition is that the business constraint #3 of our problem restricts the time span of all the items in the same truck. So, grouping items with similar available time will be easier to satisfy this constraint. Below are two example partitions to illustrate the idea.

* Orders that are available on 2022-08-01:

| Order_ID | Material_ID | Number_of_Items | Weight_Per_Item | Source | Destination | Available_Time | Deadline |
| ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- |
| 1 | A | 3 | 2t | S1 | D1 | 2022-08-01 7AM | 2022-08-02 |
| 2 | B | 5 | 1t | S1 | D2 | 2022-08-01 9AM | 2022-08-03 |
| ... | ... | ... | ... | ... | ... | ... | ... |

* Orders that are available on 2022-08-02:

| Order_ID | Material_ID | Number_of_Items | Weight_Per_Item | Source | Destination | Available_Time | Deadline |
| ----------- | ----------- | --------------|----------- | ----------- | --------------| ----------- | ----------- |
| 300 | AA | 3 | 1t | S1 | D1 | 2022-08-02 10AM | 2022-08-04 |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Step 3: Solve the Smaller Problem

This step is achieved by the ParallelRunStep function provided by Azure Machine Learning. The ParallelRunStep function can be configured to solve partitioned optimization problems in parallel with a chosen optimization solver.

There are many optimization techniques, e.g., Linear Programming (LP), Mixed Integer Programming (MIP), [Constraint Programming](https://en.wikipedia.org/wiki/Constraint_programming), etc. that one can use to solve the optimization problems. The framework introduced in this accelerator is solver-agnostic. In this accelerator, we demonstrate the use of Constraint Programming for route optimization.

Comparing to mathematical optimization techniques (e.g., LP, MIP), Constraint Programming is more expressive in that it can be used to model optimization problems in forms of arbitrary constraints; for more details see [this article](https://www.ibm.com/docs/en/icos/12.8.0.0?topic=overview-constraint-programming-versus-mathematical-programming).
## Step 4: Merge the Results

Once all the smaller problems are solved, we can merge their corresponding solutions with the partial result produced in step 1 to form a feasible solution to the original optimization problem. Assume we have solved two smaller problems with their individual results as follows:

* Result for partition 1:

| Schedule_ID | Order_ID | Material_ID | Number_of_Items | Source | Destination | Truck_Type |
| --------------|----------- | ----------- | --------------| ----------- | ----------- | ----------- |
| 103 | 1 | A | 3 | S1 | D1 | 10t |
| 104 | 2 | B | 5 | S1 | D2 | 5t |
| ... | ... | ... | ... | ... | ... | ... |

* Result for partition 2:

| Schedule_ID | Order_ID | Material_ID | Number_of_Items | Source | Destination | Truck_Type |
| --------------|----------- | ----------- | --------------| ----------- | ----------- | ----------- |
| 201 | 300 | AA | 3 | S1 | D1 | 5t |
| ... | ... | ... | ... | ... | ... | ... |

We can simply concatenate the above results to form the final solution:
| Schedule_ID | Order_ID | Material_ID | Number_of_Items | Source | Destination | Truck_Type |
| --------------|----------- | ----------- | --------------| ----------- | ----------- | ----------- |
| 103 | 1 | A | 3 | S1 | D1 | 10t |
| 104 | 2 | B | 5 | S1 | D2 | 5t |
| ... | ... | ... | ... | ... | ... | ... |
| 201 | 300 | AA | 3 | S1 | D1 | 5t |
| ... | ... | ... | ... | ... | ... | ... |
     

<!-- 1. **Reduce Search Space**: Given the problem space is huge, it could be a good idea to adopt some human heuristics to assign part of the items first. There two reasons: (1) For a large-scale problem, it could end up with a lot of partitions after the second step, which means we need to launch many machines to parallel the job and it will cost a lot of money; (2) For some special cases, we may easily find an optimal/near-optimal assignment based on some simple heuristics. For example, in our route optimization scenario, there are different kind of trucks we can choose from. Among them, the biggest truck is the most cost efficient. A simple heuristic is to fill up the biggest truck by items having same destination. This heuristic gives us the lowest delivery cost for those items. After applying this heuristic, we will have (i) a partial result that contains the heuristic assignment, (ii) the remaining unassigned items as the input for the partition step.
2. **Partition Problem**: Given the reduced problem from step 1, we can apply different partition strategies to cut down the problem space. The objective here is to make sure each single partition is small enough to solve within a user defined time limit. In an ideal case, we hope the partition strategy will not hurt the optimality of the original problem. For example, in our route optimization scenario, partitioning the items by the delivery source will keep the optimality of the original problem. However, in the case that there are a lot of items are from the same source, we need to further partition those such that we can solve the problem within the time limit. The optimality may lose after that. There will be a trade-off between optimality and running time. Usually, shortening running time is more preferred.  
3. **Solve Individual Partition**: This step is achieved by ParallelRunStep in Azure ML. The ParallelRunStep will make sure items from the same partition will be assigned to the same process. Within each partition, we will input the corresponding items to our optimization program, which models the problem using our desired optimization solver (it is OR-Tools in our case). The optimization program will solve the problem and output the result to the next step. 
4. **Merge Result**: Once all the smaller problems are solved, we can merge them with the partial result produced in step 1 as the final result. There is still chance that we can further optimize the result using some simple heuristic in this final step. For example, within each partition, some items may be assigned to a smallest truck since there are no other items can be delivered together with them. However, when considering items from other partitions in the merge step, we may have chance to further combine those into a bigger truck if they all share the same destination.   

The whole Azure ML pipeline will be published as a REST API such that it can be reused by specifying different input and parameters.  -->

# Try the Accelerator

The below sections describe the detailed steps to run the accelerator.

## Prerequisite

You need to have an Azure subscription with the access to the following resources: 

| Azure Resources      | Description | Note |
| ----------- | ----------- | --------------|
| Azure Machine Leaning | To run the end-2-end pipeline   | Refer to the [instructions](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace?tabs=azure-portal#create-a-workspace) to provision an Azure ML service |

## Getting Started

1. Create a virtual environment. The solution accelerator is tested with Python 3.8. 
    ```
    conda create -n route-optimization python=3.8
    conda activate route-optimization
    ```

2. Clone the repo and install python dependencies:
    ```
    git clone https://github.com/microsoft/dstoolkit-route-optimization.git
    cd dstoolkit-route-optimization
    pip install -r requirements.txt
    ```
    
    If you are using Visual Studio Code, you will find a kernel named route-optimization in the kernel list. If you want to use Jupyter Notebook instead, create a kernel explicitly:
    ```
    python -m ipykernel install --user --name route-optimization --display-name "route-optimization"
    ```

3. Upload sample data

    We have prepared some sample input data in the [sample_data](./sample_data) directory. You need to upload all the data to the default Datastore in your Azure ML workspace. The [order_small.csv](./sample_data/order_small.csv) under this directory is a small sample, best for testing. You can alternatively use [order_large.csv](./sample_data/order_large.csv) to test parallel run. In addition, there is another file named [distance.csv](./sample_data/distance.csv) that stores the pair-wise distance between different locations. 
    
    To find your default Datastore, you can login your Azure ML studio, and click on the Datastores icon:
    
    ![image](docs/media/default-datastore.png)
    
    In the Overview page of the default Datastore, you can find the Blob container linking to this Datastore. Follow the link, you can go to the portal of the container, where you can upload the sample data.
    
    ![image](docs/media/default-container.png)
    
    For example, below we create a folder named model_input and upload all the sample data into this folder. 
    
    ![image](docs/media/upload-file.png)
    
4. Configure Environment Variables

    Create a `.env` file in the root directory of the repository, and fill in the values for the following variables (**Note**: `.env` is meant to be used in local mode. It is already added to the `.gitignore` file to avoid accidental commit of credentials to a repo):

    ```
    # Azure ML configuration
    AML_WORKSPACE_NAME=    # The name of the Azure ML workspace
    AML_SUBSCRIPTION_ID=  # The Azure subscription ID related to the above Azure ML workspace
    AML_RESOURCE_GROUP=     # The resource group of the Azure ML workspace
    ```

5. Run the optimization pipeline

    You can now create and run the whole pipeline using [the notebook for pipeline definition](./notebook/aml_pipeline.ipynb). Once the pipeline run is completed, it will output the final route assignment as a csv file to the Azure ML default Datastore under the output path you specified in the notebook (e.g., model_output in our above example). 

## Code structure

```sh
├── ./notebook
│   ├── ./notebook/aml_pipeline.ipynb     # Notebook for optimization pipeline
├── ./requirements.txt                    # Defines required libraries in Python
├── ./sample_data
│   ├── ./sample_data/distance.csv        # Sample data defining distances between locations
│   ├── ./sample_data/order_large.csv     # Large example of customers' orders
│   └── ./sample_data/order_small.csv     # Small example of customers' orders
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
