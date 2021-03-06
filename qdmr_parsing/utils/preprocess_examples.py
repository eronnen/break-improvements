import argparse
import csv
import json
import pandas as pd
import os
import re
import ast
import logging

from utils.qdmr_identifier import split_decomposition, parse_step, get_step_seq2seq_repr, mycopynet_qdmr_to_regular_qdmr
from utils.break_dataset import is_noisy_data, NoiseDataException, WRONG_TRAINING_OPERATION_LIST


def get_example_split_set_from_id(question_id):
    return question_id.split('_')[1]


def preprocess_input_file(input_file, lexicon_file=None, model=None, model_type='seq2seq'):
    if lexicon_file:
        lexicon = [
            json.loads(line)
            for line in open(lexicon_file, "r").readlines()
        ]
    else:
        lexicon = None

    examples = []
    process_target = process_target_mycopynet if model_type == 'mycopynet' else process_target_seq2seq
    with open(input_file, encoding='utf-8') as f:
        lines = csv.reader(f)
        header = next(lines, None)
        num_fields = len(header)
        assert num_fields == 5

        for i, line in enumerate(lines):
            assert len(line) == num_fields, "read {} fields, and not {}".format(len(line), num_fields)
            question_id, source, target, operations, split = line
            split = get_example_split_set_from_id(question_id)

            if target:
                operations = ast.literal_eval(operations)
                try:
                    target = process_target(target.lower(), operations, question_id)
                except NoiseDataException:
                    logging.warning(f"skipping noise data sentence: \"{target}\"")
                    continue
            example = {'annotation_id': '', 'question_id': question_id,
                       'source': source, 'target': target, 'split': split}
            if model:
                parsed = model(source)
                example['source_parsed'] = parsed
            if lexicon:
                assert example['source'] == lexicon[i]['source']
                example['allowed_tokens'] = lexicon[i]['allowed_tokens']

            examples.append(example)

    return examples


def fix_references(string):
    return re.sub(r'#([1-9][0-9]?)', '@@\g<1>@@', string)


def process_target_seq2seq(target, *args, **kwargs):
    # replace multiple whitespaces with a single whitespace.
    target_new = ' '.join(target.split())

    # replace semi-colons with @@SEP@@ token, remove 'return' statements.
    parts = target_new.split(';')
    new_parts = [re.sub(r'return', '', part.strip()) for part in parts]
    target_new = ' @@SEP@@ '.join([part.strip() for part in new_parts])

    # replacing references with special tokens, for example replacing #2 with @@2@@.
    target_new = fix_references(target_new)

    return target_new.strip()


def process_target_mycopynet(target, operations, question_id):
    """Returns the target that 'mycopynet' model needs to learn.

    Parameters
    ----------
    target : str
        the original target in the original QDMR format.

    Returns
    -------
    str
        The target in the format which 'mycopynet' needs to learn

    """
    if is_noisy_data(target, operations, question_id):
        raise NoiseDataException()

    target = ' '.join(target.split())
    step_texts = split_decomposition(target)

    # sometimes there is a useless 'return;' in the middle of the target (???)'
    operations = [operation for operation, step_text in zip(operations, step_texts) if step_text != '']
    step_texts = [step_text for step_text in step_texts if step_text != '']

    assert len(step_texts) == len(operations)
    steps = [parse_step(step) for step in step_texts]
    assert len(steps) == len(operations)
    if question_id not in WRONG_TRAINING_OPERATION_LIST:
        for step, expected_operation in zip(steps, operations):
            assert step.operator_name == expected_operation, f"wrong operation predicted \"{step.operator_name}\"" \
                                                             f" instead of \"{expected_operation}\""
    target_new = ''
    for i, step in enumerate(steps):
        if i > 0:
            target_new += " "
        step_text = get_step_seq2seq_repr(step)
        target_new += step_text

    return target_new


def write_output_files(base_path, examples, dynamic_vocab):
    # Output file is suitable for the allennlp seq2seq reader and predictor.
    with open(base_path + '.tsv', 'w', encoding='utf-8') as fd:
        for example in examples:
            if dynamic_vocab:
                output = example['source'] + '\t' + example['allowed_tokens'] + '\t' + example['target'] + '\n'
            else:
                output = example['source'] + '\t' + example['target'] + '\n'
            fd.write(output)

    with open(base_path + '.json', 'w', encoding='utf-8') as fd:
        for example in examples:
            output_dict = {'source': example['source']}
            if dynamic_vocab:
                output_dict['allowed_tokens'] = example['allowed_tokens']
            fd.write(json.dumps(output_dict) + '\n')

    print(base_path + '.tsv')
    print(base_path + '.json')


def sample_examples(examples, configuration):
    df = pd.DataFrame(examples)
    df["dataset"] = df.question_id.apply(lambda x: x.split('_')[0])

    print("dataset distribution before sampling:")
    print(df.groupby("dataset").agg("count"))
    for dataset in df.dataset.unique().tolist():
        if dataset in configuration:
            drop_frac = 1 - configuration[dataset]
            df = df.drop(df[df.dataset == dataset].sample(frac=drop_frac).index)

    print("dataset distribution after sampling:")
    print(df.groupby("dataset").agg("count"))

    return df.to_dict(orient="records")


def main(args):
    model_type = "mycopynet" if args.mycopynet else "seq2seq"
    examples = preprocess_input_file(args.input_file, lexicon_file=args.lexicon_file, model_type=model_type)
    print(f"processed {len(examples)} examples. out of {len(open(args.input_file, encoding='utf-8').readlines())}")
    if args.sample:
        examples = sample_examples(examples, args.sample)
        print(f"left with {len(examples)} examples after sampling.")

    dynamic_vocab = args.lexicon_file is not None
    write_output_files(os.path.join(args.output_dir, args.output_file_base), examples, dynamic_vocab)

    print("done!\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="example command: "
                    "python utils/preprocess_examples.py data/QDMR/train.csv data/ "
                    "--lexicon_file data/QDMR/train_lexicon_tokens.json --output_file_base train_dynamic"
    )
    parser.add_argument('input_file', type=str, help='path to input file')
    parser.add_argument('output_dir', type=str, help='path to output file, without file extension')
    parser.add_argument('--lexicon_file', type=str, default=None,
                        help='path to lexicon json file with allowed tokens per example')
    parser.add_argument('--output_file_base', type=str, default="", help='output file base name (without file extension)')
    parser.add_argument('--sample', type=json.loads, default="{}",
                        help='json-formatted string with dataset down-sampling configuration, '
                             'for example: {"ATIS": 0.5, "CLEVR": 0.2}')
    parser.add_argument('--mycopynet', action='store_true', help="\"mycopynet\" preprocessing")
    args = parser.parse_args()
    assert os.path.exists(args.input_file)
    assert os.path.exists(args.output_dir)
    if args.lexicon_file:
        assert os.path.exists(args.lexicon_file)

    main(args)

