from .qdmr_operation_identifier import DELIMITER, parse_step


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
        assert 'return' == tokens[0].lower(), "\"Return\" should be the first toekn of a qdmr"
        for tok in tokens[1:]:
            step += tok.strip() + " "
        step = step.strip()
        steps += [step]
    return steps


def parse_qdmr(qdmr_text):
    steps = split_decomposition(qdmr_text)
    return [parse_step(step) for step in steps]
