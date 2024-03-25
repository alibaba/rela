import argparse
import sys
import os
import logging
import json
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

this_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(this_dir)
sys.path.append(project_dir)

from rela.main import generate_counterexamples
from specs.dict import defined_specs
from rela.language import *
from rela.counterexample.counterexample import CounterExampleGenerationResult, CounterExample

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
        "-i",
        "--input",
        type=str,
        required=False,
        help="Path to the input file of failed case",
    )
    parser.add_argument(
        "-I",
        "--index",
        type=int,
        required=False,
        help="Index of the failed case for the file to be checked",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        help="Path to the output file of counter examples",
    )
    parser.add_argument(
        "-s",
        "--summary-file",
        type=str,
        required=False,
        help="Path to the summary file of counter examples",
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
        "-k",
        "--top-k",
        type=int,
        required=False,
        default=3,
        help="Number of top reasons to print",
    )
    parser.add_argument(
        "-S",
        "--spec",
        type=str,
        required=False,
        choices=defined_specs.keys(),
        help="Spec used for verification",
    )
    parser.add_argument(
        "--filter",
        nargs='+',
        type=str,
        required=False,
        choices=defined_specs.keys(),
        help="Select only counterexamples that match the given spec name",
    )
    return parser.parse_args()

def to_key(counterexample: CounterExample) -> tuple:
    return (frozenset(counterexample.before_paths), frozenset(counterexample.after_paths), frozenset(counterexample.left_paths), frozenset(counterexample.right_paths), counterexample.spec)

def main():
    args = parse()
    if args.precision == 'devicegroup' and args.mapping_file is None:
        raise ValueError('Mapping file is required for devicegroup level forwarding graph')

    if args.spec is not None:
        spec = defined_specs[args.spec]
    else:
        raise ValueError('Spec is not specified')

    # read failed cases
    if args.input is None and args.index is None:
        raise Exception('Either input file or index should be provided')
    elif args.input is not None and args.index is not None:
        raise Exception('Only one of input file and index should be provided')
    elif args.input is not None:
        with open(args.input, 'r') as f:
            verification_result = json.load(f)
        failed_cases = verification_result['failed_cases']
    elif args.index is not None:
        failed_cases = [(args.data, args.index)]

    # check if args.data is a directory
    if os.path.isdir(args.data):
        # group failed cases by data
        failed_cases_by_file = {}
        for file, index in failed_cases:
            if file not in failed_cases_by_file:
                failed_cases_by_file[file] = []
            failed_cases_by_file[file].append(index)

        logging.getLogger().setLevel(logging.ERROR)

        if args.output is not None:
            # create output directory
            if not os.path.exists(args.output):
                os.makedirs(args.output)
            else:
                raise Exception(f'Output directory {args.output} already exists')
        
        res = CounterExampleGenerationResult(
            n_cases=0,
            error_cases=[],
            counter_examples=[]
        )
        with ProcessPoolExecutor(max_workers=args.n_cpus, initializer=tqdm.set_lock, initargs=(tqdm.get_lock(),)) as executor:
            futures = {}
            for file, indices in failed_cases_by_file.items():
                in_file = os.path.join(args.data, file)
                out_file = os.path.join(args.output, file) if args.output is not None else None
                future = executor.submit(generate_counterexamples, spec, in_file, args.format, args.precision, indices, out_file, args.mapping_file)
                futures[future] = file
            
            for f in tqdm(as_completed(futures.keys()), total=len(failed_cases_by_file), position=0, leave=True):
                try:
                    chunk_res = f.result()
                    res.n_cases += chunk_res.n_cases
                    res.error_cases.extend(chunk_res.error_cases)
                    res.counter_examples.extend(chunk_res.counter_examples)
                except Exception as e:
                    print(f'Exception raised when generating counterexamples for {futures[f]}: {e}')
                    continue

        logging.getLogger().setLevel(logging.INFO)
    else:
        #failed_cases = [case[1] for case in failed_cases]
        out_file = args.output if args.output is not None else None
        res = generate_counterexamples(spec, args.data, args.format, args.precision, failed_cases, out_file, args.mapping_file)

    print(f'Generated {len(res.counter_examples)} counterexamples for {res.n_cases} failed cases')
    if len(res.error_cases) > 0:
        print(f'Failed to generate counterexamples for {len(res.error_cases)} failed cases:')
        for case in res.error_cases:
            print(case)

    # summarize counterexamples
    unique_counter_examples = {}
    filtered_counter_examples = res.counter_examples
    if args.filter is not None:
        accepted_specs = set([str(defined_specs[spec]) for spec in args.filter])
        filtered_counter_examples = [ce for ce in filtered_counter_examples if ce.spec in accepted_specs]
        print(f'Filtered to {len(filtered_counter_examples)} counterexamples that match the given spec name(s)')
    for counter_example in filtered_counter_examples:
        key = to_key(counter_example)
        if key not in unique_counter_examples:
            unique_counter_examples[key] = 1
        else:
            unique_counter_examples[key] += 1

    # sort counterexamples by number of failed cases
    sorted_counterexamples = sorted(unique_counter_examples.items(), key=lambda x: x[1], reverse=True)
    # convert to output format
    sorted_counterexamples = [{'before_paths': list(ce[0][0]), 'after_paths': list(ce[0][1]), 'left_paths': list(ce[0][2]), 'right_paths': list(ce[0][3]), 'n_failed_cases': ce[1], 'spec': ce[0][4]} for ce in sorted_counterexamples]

    # print summary
    n_print = min(args.top_k, len(sorted_counterexamples))
    print(f'Summarized into {len(sorted_counterexamples)} reasons. Top {n_print} reasons:')
    for i in range(n_print):
        ce = sorted_counterexamples[i]
        print(f'  {i+1}. Responsible for {ce["n_failed_cases"]}/{res.n_cases} failed cases.')
        print(f'     Before paths (preState):')
        for path in ce['before_paths']:
            print(f'       {path}')
        print(f'     After paths (postState):')
        for path in ce['after_paths']:
            print(f'       {path}')
        print(f'     Left paths:')
        for path in ce['left_paths']:
            print(f'       {path}')
        print(f'     Right paths:')
        for path in ce['right_paths']:
            print(f'       {path}')

    if args.summary_file is not None:
        with open(args.summary_file, 'w', encoding='utf8') as f:
            json.dump(sorted_counterexamples, f, indent=2, ensure_ascii=False)
        print (f'Summary written to {args.summary_file}')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()