# Our Copynet

## Data pre-processing
Before training or evaluating this model, the data files should be processed with the script `utils/preprocess_examples.py`.
```bash
$ python utils/preprocess_examples.py -h

usage: preprocess_examples.py [-h]
                              --mycopynet
                              [--output_file_base OUTPUT_FILE_BASE]
                              [--sample SAMPLE]
                              input_file output_dir
```

## Model training

We use `train-seq2seq-mycopynet.json` for the training.

## Evaluation
Evaluation of any model with the metrics described in the paper (i.e. EM, SARI, GED, GED+) can be done with the script `model/run_model.py`, by specifying the model for evaluation and passing the flag `--evaluate`.
Use the flag `--model mycopynet`.
