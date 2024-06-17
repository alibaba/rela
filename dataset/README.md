## What is included in the dataset?
This dataset contains the forwarding paths of 21,112 flow equivalence classes before and after a network change. It reflects the characteristics of forwarding paths in a complex production network, and show how a realistic network change affects these forwarding paths. The router names, interface names, and IP addresses in the dataset have been anonymized for confidentiality. 

The layout of the dataset:

1. `graph_change_anonymized`: each file in this directory contains the details of up to 1,000 flow equivalence classes (FEC), in JSON format. Each FEC contains an `ipTrafficKeys` field, a `graphBefore` field, and a `graphAfter` field. `ipTrafficKeys` indicate a set of packets that all traverse the same forwarding paths before the change *and* after the change. `graphBefore` and `graphAfter` each encodes a forwarding graph, where the vertices are routers and edges are the inbound interface of each network link.
2. `dg_mapping_anonymized.json`: contains the mapping from a router name to the router group that it belongs to. This file is used by Rela tool to construct router-group level forwarding paths on-the-fly.

## What is the scale of the dataset?
This dataset contains 21,112 unique FECs (the evaluation of our paper uses a richer set of FECs, in the order of 1,000,000). This sampled set of FECs traversed a total of 2,460 unique devices and 92501 unique interfaces.

## How can you use this dataset?
The Rela tool defines this graph format in its data model. One can load a json file containing a list of FECs using the following function provided by Rela: 
```python
from rela.networkmodel.relagraphformat import RelaGraphNC
data = RelaGraphNC.from_json(file, precision, mapping_file)
```

## Citation
Xieyang Xu, Yifei Yuan, Zachary Kincaid, Arvind Krishnamurthy, Ratul
Mahajan and David Walker. 2024. Relational Network Verification. In ACM
SIGCOMM 2024 Conference (ACM SIGCOMM ’24), August 4–8, 2024, Sydney,
NSW, Australia. ACM, New York, NY, USA, 15 pages. https://doi.org/10.1145/3651890.3672238
```
@inproceedings{rela-sigcomm24,
  title={Relational Network Verification},
  author={Xu, Xieyang and Yuan, Yifei and Kincaid, Zachary and Krishnamurthy, Arvind and Mahajan, Ratul and Walker, David and Zhai, Ennan},
  booktitle={Proceedings of SIGCOMM '24},
  publisher = {ACM},
  year={2024}
}
```


