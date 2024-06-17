# Rela - Validating production network changes with just a few lines of specifications
Rela is a tool for checking the correctness of network changes. It provides:
- A domain-specific language for users to describe end-to-end change impacts in a few lines.
- A verifier to check whether a network change implementation satisfies the user's specification.

We also release a [dataset](dataset/) we used to benchmark the performance of Rela tool in a complex production network. Please refer to this [documentation](dataset/README.md) for more details about this dataset.

The design of Rela language and the experience of using Rela to verify complex, realworld networks are desribed in the paper,

Xieyang Xu, Yifei Yuan, Zachary Kincaid, Arvind Krishnamurthy, Ratul
Mahajan and David Walker. 2024. Relational Network Verification. In ACM
SIGCOMM 2024 Conference (ACM SIGCOMM ’24), August 4–8, 2024, Sydney,
NSW, Australia. ACM, New York, NY, USA, 15 pages. https://doi.org/10.1145/3651890.3672238


## Install Rela
**Rela supports only Python version 3.7 at this time.** Please make sure you are in a Python virtual environement with version 3.7 when executing the following commands.

To install Rela, run the following from the root directory of this repo.
```sh
$ pip install .
```
If not already installed, please use the following to install dependencies.
```sh
$ pip install hfst tqdm pytest ipaddress
```
Verify installation with the following. All unit tests should pass with a correct installation.
```sh
$ pytest .
```


## Using Rela
See [here](examples/demo.ipynb) for a running example.
