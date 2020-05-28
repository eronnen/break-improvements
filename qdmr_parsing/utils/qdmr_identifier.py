import re
from .qdmr_operation_identifier import DELIMITER, parse_step, parse_step_from_mycopynet, get_step_seq2seq_repr


def split_decomposition(qdmr):
    """Splits the decomposition into an ordered list of steps

    Parameters
    ----------
    qdmr : str
        String representation of the QDMR

    Returns
    -------
    list
        returns ordered list of qdmr steps
    """
    # parse commas as separate tokens
    qdmr = qdmr.replace(",", " , ")
    crude_steps = qdmr.split(DELIMITER)
    steps = []
    for i in range(len(crude_steps)):
        step = crude_steps[i]
        tokens = step.split()
        step = ""
        # remove 'return' prefix
        if len(tokens) > 0 and 'return' == tokens[0].lower():
            tokens = tokens[1:]
        for tok in tokens:
            step += tok.strip() + " "
        step = step.strip()
        steps += [step]
    return [step.strip() for step in steps]


def parse_mycopynet_qdmr(qdmr_text):
    steps = re.compile(r"(@@SEP@@|@@SEP_\S+@@)").split(qdmr_text)
    steps = [s.strip() for s in steps if s.strip()]
    if not len(steps) % 2 == 0:
        steps = steps[:-1]
    steps = [f"{steps[i*2]} {steps[i*2+1]}" for i in range(int(len(steps) / 2))]
    return [parse_step_from_mycopynet(step) for step in steps]


def parse_qdmr(qdmr_text):
    steps = split_decomposition(qdmr_text)
    return [parse_step(step) for step in steps]


def mycopynet_qdmr_to_regular_qdmr(mycopynet_qdmr):
    qdmr = parse_mycopynet_qdmr(mycopynet_qdmr)
    return ' @@SEP@@ '.join([s.generate_step_text_nicely() for s in qdmr])
