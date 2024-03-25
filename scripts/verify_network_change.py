import argparse
import sys
import os
from dataclasses import asdict
import logging
import json
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

this_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(this_dir)
sys.path.append(project_dir)

from rela.main import verify_network_change
from specs.dict import defined_specs
from rela.language import *
from rela.verification import VerificationResult

def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--data",
        type=str,
        required=True,
        help="Path to the file to be checked",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        help="Path to the output file of verification result",
    )
    parser.add_argument(
        "-a",
        "--alg",
        type=str,
        required=False,
        choices=["default", "alt"],
        default="default",
        help="Verification algorithm, default or alt",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        required=True,
        choices=["path", "graph"],
        help="Format of the file to be checked, path or graph",
    )
    parser.add_argument(
        "-P",
        "--precision",
        type=str,
        required=True,
        choices=["interface", "device", "devicegroup"],
        help="Precision of the file to be checked, interface or device or devicegroup",
    )
    parser.add_argument(
        "-m",
        "--mapping-file",
        type=str,
        required=False,
        help="Path to the mapping file for devicegroup level forwarding graph",
    )
    parser.add_argument(
        "-n",
        "--n-cpus",
        type=int,
        required=False,
        default=None,
        help="Number of CPUs to use",
    )
    parser.add_argument(
        "-S",
        "--spec",
        type=str,
        required=False,
        choices=defined_specs.keys(),
        help="Spec to be verified",
    )
    parser.add_argument(
        "--previous-result",
        type=str,
        required=False,
        help="Use previous verification result to skip passed cases",
    )
    return parser.parse_args()

def main():
    args = parse()
    if args.precision == 'devicegroup' and args.mapping_file is None:
        raise ValueError('Mapping file is required for devicegroup level forwarding graph')

    if args.spec is not None:
        spec = defined_specs[args.spec]
    else:
        raise ValueError('Spec is not specified')


    if args.previous_result:
        with open(args.previous_result, 'r') as f:
            prev_res = json.load(f)
        prev_failed_cases = prev_res['failed_cases']
        if args.data != prev_res['data']:
            raise ValueError('Previous result does not match the current verification task')
        if os.path.isdir(args.data):
            mapping = {}
            for file, index in prev_failed_cases:
                file = os.path.basename(file)
                if file not in mapping:
                    mapping[file] = []
                mapping[file].append(index)
            prev_failed_cases = mapping
    else:
        prev_failed_cases = None

    # check if args.data is a directory
    if os.path.isdir(args.data):
        logging.getLogger().setLevel(logging.ERROR)
        files = os.listdir(args.data)
        res = VerificationResult(
            data=args.data,
            spec=str(spec),
            n_total=0,
            n_passed=0,
            n_failed=0,
            n_skipped=0,
            passed_cases=[],
            failed_cases=[],
            skipped_cases=[]
        )

        with ProcessPoolExecutor(max_workers=args.n_cpus, initializer=tqdm.set_lock, initargs=(tqdm.get_lock(),)) as executor:
            futures = {}
            for file in files:
                if prev_failed_cases is not None and file not in prev_failed_cases:
                    continue
                indices = prev_failed_cases[file] if prev_failed_cases is not None else None
                future = executor.submit(verify_network_change, spec, os.path.join(args.data, file), args.format, args.precision, args.alg, args.mapping_file, indices)
                futures[future] = file
            
            for f in tqdm(as_completed(futures.keys()), total=len(files), position=0, leave=True):
                try:
                    chunk_res = f.result()
                except Exception as e:
                    print(f'Exception raised when verifying {futures[f]}: {e}')
                    continue

                chunk_res = f.result()
                res.n_total += chunk_res.n_total
                res.n_passed += chunk_res.n_passed
                res.n_failed += chunk_res.n_failed
                res.n_skipped += chunk_res.n_skipped
                res.passed_cases += [(chunk_res.data, case) for case in chunk_res.passed_cases]
                res.failed_cases += [(chunk_res.data, case) for case in chunk_res.failed_cases]
                res.skipped_cases += [(chunk_res.data, case) for case in chunk_res.skipped_cases]

        logging.getLogger().setLevel(logging.INFO)
    else:
        res = verify_network_change(spec, args.data, args.format, args.precision, args.alg, args.mapping_file, prev_failed_cases)


    print(f'Verification result: {res}')


    if args.output:
        with open(args.output, 'w', encoding='utf8') as f:
            json.dump(asdict(res), f, indent=2, ensure_ascii=False)
        print(f'Verification result saved to {args.output}')



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()