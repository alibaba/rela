# Rela - Validating production network changes with just a few lines of specifications
Rela is a tool for checking the correctness of network changes. It provides:
- A domain-specific language for users to describe end-to-end change impacts in a few lines.
- A verifier to check whether a network change implementation satisfies the user's specification.

We also release a [dataset](dataset/) we used to benchmark the performance of Rela tool in a complex production network. The dataset is sampled and anonymized before releasing.

The design of Rela language and the experience of using Rela to verify complex, realworld networks are desribed in the paper,

Xieyang Xu, Yifei Yuan, Zachary Kincaid, Arvind Krishnamurthy, Ratul
Mahajan and David Walker. 2024. Relational Network Verification. In ACM
SIGCOMM 2024 Conference (ACM SIGCOMM ’24), August 4–8, 2024, Sydney,
NSW, Australia. ACM, New York, NY, USA, 15 pages. https://doi.org/10.1145/3651890.3672238

## What is included in the dataset?
This dataset contains the forwarding paths of 21,112 flow equivalence classes before and after a network change. It reflects the characteristics of forwarding paths in a complex production network, and show how a realistic network change affects these forwarding paths.

The layout of the dataset subdirectory:

1. `graph_change_anonymized`: each file in this directory contains the details of up to 1,000 flow equivalence classes (FEC), in JSON format. Each FEC contains an `ipTrafficKeys` field, a `graphBefore` field, and a `graphAfter` field. `ipTrafficKeys` indicate a set of packets that all traverse the same forwarding paths before the change *and* after the change. `graphBefore` and `graphAfter` each encodes a forwarding graph, where the vertices are routers and edges are the inbound interface of each network link.
2. `dg_mapping_anonymized.json`: contains the mapping from a router name to the router group that it belongs to. This file is used by Rela tool to construct router-group level forwarding paths on-the-fly.

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
