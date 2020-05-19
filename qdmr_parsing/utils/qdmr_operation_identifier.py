import re

DELIMITER = ';'
REF = '#'


def extract_aggragate_from_qdmr_step(step):
    """Extract aggregate expression from QDMR step

    Returns
    -------
    str
        string of the aggregate: max/min/count/sum/avg.
    """
    for aggregate in ['max', 'highest', 'largest', 'most', 'longest',
                      'biggest', 'more', 'last', 'longer', 'higher', 'larger']:
        if aggregate in step:
            return "max"
    for aggregate in ['min', 'lowest', 'smallest', 'least', 'shortest',
                      'less', 'first', 'shorter', 'lower', 'fewer', 'smaller']:
        if aggregate in step:
            return "min"
    for aggregate in ['number of']:
        if aggregate in step:
            return "number of"
    for aggregate in ['sum', 'total']:
        if aggregate in step:
            return "sum"
    for aggregate in ['avg', 'average', 'mean ']:
        if aggregate in step:
            return "avg"
    for aggregate in ['closer']:
        if aggregate in step:
            return "closer"
    return None


def extract_references_from_qdmr_step(step):
    """Extracts a list of references to previous steps

        Returns
        -------
        str
            string of the aggregate: max/min/count/sum/avg.
        """
    # make sure decomposition does not contain a mere '# ' other than a reference.
    step = step.replace("# ", "hashtag ")
    references = []
    l = step.split(REF)
    for chunk in l[1:]:
        if len(chunk) > 1:
            ref = chunk.split()[0]
            ref = int(ref)
            references += [ref]
        if len(chunk) == 1:
            ref = int(chunk)
            references += [ref]
    return references


class QDMROperation(object):
    def __init__(self):
        self._sub_operator_name = None
        self._arguments = []

    @property
    def operator_name(self):
        raise NotImplementedError()

    @property
    def sub_operator_name(self):
        return self._sub_operator_name

    @property
    def full_operator_name(self):
        if self.sub_operator_name is not None:
            return f'{self.operator_name}_{self.sub_operator_name.replace(" ", "@")}'
        return self.operator_name

    @property
    def arguments(self):
        return self._arguments

    def __str__(self):
        return f"{self.full_operator_name.upper()}_{self.arguments}"

    def init_from_raw_qdmr_step(self, step):
        """Initializes the object from the given step.

        Parameters
        ----------
        self : QDMROperation
        step : str

        """
        self._init_from_raw_qdmr_step(step)
        self._arguments = [arg.strip() for arg in self._arguments]

    def _init_from_raw_qdmr_step(self, step):
        """Initializes the object from the given step.

        Parameters
        ----------
        self : QDMROperation
        step : str

        """
        raise NotImplementedError()

    def generate_step_text(self):
        """
        generate step text from the operation and the arguments
        """
        raise NotImplementedError()


class QDMROperationSelect(QDMROperation):
    """
    Example: "return countries"
    """
    @property
    def operator_name(self):
        return 'select'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if 0 < len(references):
            raise TypeError(f'{step} is not {self.operator_name}')
        self._sub_operator_name = None
        self._arguments = [step]

    def generate_step_text(self):
        return self.arguments[0]


class QDMROperationFilter(QDMROperation):
    """
    Example: "#2 that is wearing #3"
    Example: "#1 from Canada"
    """
    @property
    def operator_name(self):
        return 'filter'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (0 < len(references) <= 3 and step.startswith("#")):
            raise TypeError(f'{step} is not {self.operator_name}')
        to_filter = f"#{references[0]}"
        filter_condition = step.split(to_filter, 1)[1]
        # condition might be empty
        self._arguments = [to_filter, filter_condition]

    def generate_step_text(self):
        return f"{self.arguments[0]} {self.arguments[1]}"


class QDMROperationProject(QDMROperation):
    """
    Example: "first name of #2"
    Example: "who was #1 married to"
    """
    @property
    def operator_name(self):
        return 'project'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (len(references) == 1 and re.search(r"[\s]+[#]+[0-9\s]+", step)):
            raise TypeError(f'{step} is not {self.operator_name}')
        ref = f"#{references[0]}"
        projection = step.replace(ref, "#REF")
        self._arguments = [projection, ref]
        assert '' not in self._arguments

    def generate_step_text(self):
        assert "#REF" in self.arguments[0]
        return self.arguments[0].replace("#REF", self.arguments[1])


class QDMROperationAggregate(QDMROperation):
    """
    Example: "lowest of #2"
    Example: "the number of #1"
    """
    AGGREGATORS = ['number of', 'highest', 'largest', 'lowest', 'smallest', 'maximum', 'minimum',
                   'max', 'min', 'sum', 'total', 'average', 'avg', 'mean of', 'first', 'last',
                   'longest', 'shortest']

    @property
    def operator_name(self):
        return 'aggregate'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if len(references) != 1:
            raise TypeError(f'{step} is not {self.operator_name}')
        for aggr in self.AGGREGATORS:
            if f"{aggr} #" in step or f"{aggr} of #" in step:
                if aggr == 'number of' and not step.startswith(aggr) and not step.startswith(f"the {aggr}"):
                    before_number_of = step.split("number of")[0].strip()
                    if before_number_of not in ["total", "the combined", "count", "count the", "the total", "there", "average"]:
                        # it's not aggragate number of, here number of is a part of a Construct state
                        continue
                self._sub_operator_name = aggr
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')
        self._arguments = [f"#{references[0]}"]
        assert '' not in self._arguments

    def generate_step_text(self):
        full_aggregate = self.sub_operator_name
        if self.sub_operator_name in ['highest', 'largest', 'lowest', 'smallest', 'longest', 'shortest', 'first', 'last']:
            full_aggregate = f"the {self.sub_operator_name}"
        elif self.sub_operator_name in ['maximum', 'minimum', 'max', 'min', 'total', 'average', 'avg']:
            full_aggregate = f"the {self.sub_operator_name} of"
        return f"{full_aggregate} {self.arguments[0]}"


class QDMROperationGroup(QDMROperation):
    """
    Example: "number of #3 for each #2"
    Example: "average of #1 for each #2"
    """
    @property
    def operator_name(self):
        return 'group'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not ('for each' in step and len(references) > 0):
            raise TypeError(f'{step} is not {self.operator_name}')
        self._sub_operator_name = extract_aggragate_from_qdmr_step(step)
        value, key = step.split('for each', 1)
        val_refs = extract_references_from_qdmr_step(value)
        key_refs = extract_references_from_qdmr_step(key)
        arg_value = value.split()[-1] if len(val_refs) == 0 else "#%s" % val_refs[0]
        arg_key = key.split()[-1] if len(key_refs) == 0 else f"#{key_refs[0]}"
        self._arguments = [arg_value, arg_key]
        assert '' not in self._arguments

    def generate_step_text(self):
        return f"{self.sub_operator_name} {self.arguments[0]} for each {self.arguments[1]}"


class QDMROperationSuperlative(QDMROperation):
    """
    Example: "#1 where #2 is highest"
    Example: "#1 where #2 is smallest"
    """
    RAW_SUPERLATIVES = ['highest', 'largest', 'most', 'smallest', 'lowest', 'smallest', 'least',
                   'longest', 'shortest', 'biggest']
    SUPERLATIVES = [f"is {sup}" for sup in RAW_SUPERLATIVES] + [f"are {sup}" for sup in RAW_SUPERLATIVES]

    @property
    def operator_name(self):
        return 'superlative'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not ((step.startswith('#') or step.startswith('the #')) and len(references) == 2 and 'where' in step):
            raise TypeError(f'{step} is not {self.operator_name}')
        for s in self.SUPERLATIVES:
            if s in step:
                self._sub_operator_name = s
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')
        entity_ref, attribute_ref = references
        self._arguments = [f"#{entity_ref}", f"#{attribute_ref}"]
        assert '' not in self._arguments

    def generate_step_text(self):
        return f"{self.arguments[0]} where {self.arguments[1]} is {self.sub_operator_name}"


class QDMROperationComparative(QDMROperation):
    """
    Example: "#1 where #2 is at most three"
    Example: "#3 where #4 is higher than #2"
    """
    COMPARATIVES = ['same as', 'same as', 'higher than', 'larger than', 'smaller than', 'lower than', 'less than',
                    'more than', 'less than', 'at least', 'at most', 'equal', ' is ', 'are', 'was', 'contain',
                    'include', 'has', 'have', 'end with', 'start with', 'ends with',
                    'starts with', 'begin']

    @property
    def operator_name(self):
        return 'comparative'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (2 <= len(references) <= 3 and 'where' in step
                and (step.startswith('#') or step.startswith('the #'))):
            raise TypeError(f'{step} is not {self.operator_name}')
        if 'where at least one' in step:
            # special comarative structure here
            if ' is ' not in step:
                raise TypeError(f'{step} is not {self.operator_name} - weird at least one sentence')
            to_filter = f"#{references[0]}"
            comparative = step.split('where at least one', 1)[1]
            attribute_1, attribute_2 = comparative.split(' is ', 1)
            self._arguments = [to_filter, attribute_1, attribute_2]
            assert '' not in self._arguments
            return

        for comp in self.COMPARATIVES:
            if comp in step:
                self._sub_operator_name = comp.strip()
                if f'is the {comp}' in step:
                    expr = f'is the {comp}'
                elif f'is {comp}' in step:
                    expr = f'is {comp}'
                else:
                    expr = comp

                to_filter = f"#{references[0]}"
                comparative = step.split('where', 1)[1]
                attribute_1, attribute_2 = comparative.split(expr, 1)
                arguments = [to_filter, attribute_1, attribute_2]
                if '' in arguments:
                    continue

                self._arguments = arguments
                return

        else:
            raise TypeError(f'{step} is not {self.operator_name}')

    def generate_step_text(self):
        return f"{self.arguments[0]} where {self.arguments[1]} {self.sub_operator_name} {self.arguments[2]}"


class QDMROperationUnion(QDMROperation):
    """
    Example: "#1 or #2"
    Example: "#1, #2, #3, #4"
    Example: "#1 and #2"
    """
    @property
    def operator_name(self):
        return 'union'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (1 < len(references)):
            raise TypeError(f'{step} is not {self.operator_name}')
        substitute_step = step.replace('and', ',').replace('or', ',')
        if not re.search(r"^[#0-9,\s]+$", substitute_step):
            raise TypeError(f'{step} is not {self.operator_name}')
        self._arguments = []
        for ref in references:
            self._arguments.append(f"#{ref}")
        assert '' not in self._arguments

    def generate_step_text(self):
        return " ," .join(self.arguments)


class QDMROperationIntersect(QDMROperation):
    """
    Example: "countries in both #1 and #2"
    Example: "#3 of both #4 and #5"
    """
    @property
    def operator_name(self):
        return 'intersection'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (len(references) >= 2 and 'both' in step and ' and' in step):
            raise TypeError(f'{step} is not {self.operator_name}')
        for expr in ['of both', 'in both', 'by both', 'between both',
                     'for both', 'are both', 'both of', 'both']:
            if expr in step:
                intersection_expression = expr
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')

        self._sub_operator_name = intersection_expression
        projection, intersection = step.split(intersection_expression, 1)
        if projection:
            self._arguments = [projection]
        intersection_references = extract_references_from_qdmr_step(intersection)
        self._arguments += [f"#{ref}" for ref in intersection_references]
        assert '' not in self._arguments

    def generate_step_text(self):
        intersection = " and ".join(self.arguments[1:])
        return f"{self.arguments[0]} {self.sub_operator_name} {intersection}"


class QDMROperationDiscard(QDMROperation):
    """
    Example: "#2 besides #3"
    Exmple: "#1 besides cats"
    """
    @property
    def operator_name(self):
        return 'discard'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (1 <= len(references) <= 2
                and (re.search(r"^[#]+[0-9]+[\s]+", step) or re.search(r"[#]+[0-9]+$", step))
                and ('besides' in step or 'not in' in step)):
            raise TypeError(f'{step} is not {self.operator_name}')
        for expr in ['besides', 'not in']:
            if expr in step:
                discard_expr = expr
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')
        set_1, set_2 = step.split(discard_expr, 1)
        self._arguments = [set_1, set_2]
        assert '' not in self._arguments

    def generate_step_text(self):
        return f"{self.arguments[0]} besides {self.arguments[1]}"


class QDMROperationSort(QDMROperation):
    """
    Example: "#1 sorted by #2"
    Example: "#1 ordered by #2"
    """
    SORT_EXPRESSIONS = [' sorted by', ' order by', ' ordered by']

    @property
    def operator_name(self):
        return 'sort'

    def _init_from_raw_qdmr_step(self, step):
        for expr in self.SORT_EXPRESSIONS:
            if expr in step:
                sort_expr = expr
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')
        objects, order = [frag.strip() for frag in step.split(sort_expr, 1)]
        self._arguments = [objects, order]
        assert '' not in self._arguments

    def generate_step_text(self):
        return f"{self.arguments[0]} sorted by {self.arguments[1]}"


class QDMROperationBoolean(QDMROperation):  # TODO: sub operation here
    """
    Example: "if both #2 and #3 are true"
    Example: "is #2 more than #3"
    Example: "if #1 is american"
    """
    BOOLEAN_PREFIXES = ['if ', 'is ', 'are ', 'did ']

    @property
    def operator_name(self):
        return 'boolean'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        # BOOLEAN step - starts with either 'if', 'is' or 'are'
        if not (step.startswith('if ') or step.startswith('is ') or step.startswith('are ') or step.startswith('did ')):
            raise TypeError(f'{step} is not {self.operator_name}')
        for expr in self.BOOLEAN_PREFIXES:
            if step.startswith(expr):
                boolean_prefix = expr
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')

        logical_op = None
        if len(references) == 2 and "both" in step and "and" in step:
            logical_op = "logical_and"
        elif len(references) == 2 and "either" in step and "or" in step:
            logical_op = "logical_or"

        if logical_op is not None:
            bool_expr = "false" if "false" in step else "true"
            sub_expressions = [f"#{ref}" for ref in references]
            self._arguments = [bool_expr] + sub_expressions
            assert '' not in self._arguments
            self._sub_operator_name = f"{logical_op} {boolean_prefix}"
            return

        if step.split()[1].startswith("#"):
            # filter boolean, e.g., "if #1 is american"
            objects = f"#{references[0]}"
            condition = step.split(objects, 1)[1]
            self._arguments = [objects, condition]
            assert '' not in self._arguments
            self._sub_operator_name = f"condition {boolean_prefix}"
            return

        if len(references) == 1 and not step.split()[1].startswith("#"):
            # projection boolean "if dinner is served on #1"
            objects = f"#{references[0]}"
            condition = step.split(' ', 1)[1].replace(objects, "#REF")
            self._arguments = [objects, condition]
            assert '' not in self._arguments
            self._sub_operator_name = f"projection {boolean_prefix}"
            return

        if len(references) == 2:
            objects = f"#{references[0]}"
            prefix = step.split(objects, 1)[0].lower()
            if "any" in prefix or "is there" in prefix or "there is" in prefix or "there are" in prefix:
                # exists boolean "if any #2 are the same as #3"
                if "any" in prefix:
                    self._sub_operator_name = "if_exist any"
                else:
                    self._sub_operator_name = "if_exist there is"
                condition = step.split(objects, 1)[1]
                self._arguments = [objects, condition]
                assert '' not in self._arguments
                return

        self._arguments = [step.split(boolean_prefix, 1)[1]]
        self._sub_operator_name = boolean_prefix
        assert '' not in self._arguments

    def generate_step_text(self):
        if "logical_and" in self.sub_operator_name or "logical_or" in self.sub_operator_name:
            logical_op, prefix = self.sub_operator_name.split()
            logical_op_word = "either" if logical_op == "logical_or" else "both"
            bool_expr = self.arguments[0]
            condition = " and ".join(self.arguments[1:])
            return f"{prefix} {logical_op_word} {condition} are {bool_expr}"

        if "condition " in self.sub_operator_name:
            _, prefix = self.sub_operator_name.split()
            return f"{prefix} {self.arguments[0]} {self.arguments[1]}"

        if "projection " in self.sub_operator_name:
            _, prefix = self.sub_operator_name.split()
            condition = self.arguments[0].replace('#REF', self.arguments[1])
            return f"{prefix} {condition}"

        if "if_exist " in self.sub_operator_name:
            _, prefix = self.sub_operator_name.split(' ', 1)
            return f"if {prefix} {self.arguments[0]} {self.arguments[1]}"

        return f"{self.sub_operator_name} {self.arguments[0]}"


class QDMROperationArithmetic(QDMROperation):
    """
    Example: "difference of #3 and #5"
    """
    ARITHMETICS = ['sum of', 'difference between', 'difference of', 'multiplication of', 'division of',
                   'sum', 'difference', 'multiplication', 'division']

    @property
    def operator_name(self):
        return 'arithmetic'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if len(references) < 1:
            raise TypeError(f'{step} is not {self.operator_name}')
        for a in self.ARITHMETICS:
            if step.startswith(a) or step.startswith(f'the {a}'):
                expression = a
                self._sub_operator_name = expression.split()[0]
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')

        if len(references) == 1:
            if 'and' not in step:
                raise TypeError(f'no \"and\" in {step}')
            prefix, suffix = step.split('and', 1)
            first_arg = prefix.split(expression, 1)[1]
            self._arguments = [first_arg, suffix]
            assert '' not in self._arguments
            return
        else:
            refs = [f'#{ref}' for ref in references]
            self._arguments = refs
            assert '' not in self._arguments

    def generate_step_text(self):
        arguments = " and ".join(self.arguments)
        return f"the {self.sub_operator_name} of {arguments}"


class QDMROperationComparison(QDMROperation):  # TODO: sub operation
    """
    Example: "which is highest of #1, #2"
    """

    @property
    def operator_name(self):
        return 'comparison'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (step.lower().startswith('which') and len(references) > 1):
            raise TypeError(f'{step} is not {self.operator_name}')

        comp = extract_aggragate_from_qdmr_step(step)
        if comp is None:
            # check if boolean comparison "which is true of #1, #2"
            if "true" in step or "false" in step:
                comp = "true" if "true" in step else "false"
            elif "bigger" in step:
                comp = "max"
            elif "smaller" in step:
                comp = "min"
            elif "earlier" in step:
                comp = "min"
            else:
                raise TypeError(f'{step} is not {self.operator_name}')
        self._sub_operator_name = comp
        refs = [f'#{ref}' for ref in references]
        self._arguments = refs
        assert '' not in self._arguments

    def generate_step_text(self):
        arguments = ', '.join(self.arguments)
        return f'which is {self.sub_operator_name} of {arguments}'


QDMR_OPERATION = {
    'select': QDMROperationSelect,
    'filter': QDMROperationFilter,
    'group': QDMROperationGroup,
    'aggregate': QDMROperationAggregate,
    'arithmetic': QDMROperationArithmetic,
    'boolean': QDMROperationBoolean,
    'comparative': QDMROperationComparative,
    'discard': QDMROperationDiscard,
    'intersection': QDMROperationIntersect,
    'project': QDMROperationProject,
    'sort': QDMROperationSort,
    'superlative': QDMROperationSuperlative,
    'union': QDMROperationUnion,
    'comparison': QDMROperationComparison,
}


def parse_step(step_text):
    potential_operators = []
    for operation_type in QDMR_OPERATION:
        try:
            step = QDMR_OPERATION[operation_type]()
            step.init_from_raw_qdmr_step(step_text)
            potential_operators.append(step)
        except TypeError as e:
            # not dis type
            continue

    if len(potential_operators) == 0:
        raise RuntimeError(f"no QDMR operation found for \"{step_text}\"")

    if len(potential_operators) == 1:
        return potential_operators.pop()

    # avoid project duplicity with aggregate
    if any(op.operator_name == "project" for op in potential_operators):
        potential_operators = [op for op in potential_operators if "project" is not op.operator_name]

    # avoid filter duplicity with comparative, superlative, sort, discard, union
    if any(op.operator_name == "filter" for op in potential_operators):
        potential_operators = [op for op in potential_operators if "filter" is not op.operator_name]

    # return boolean (instead of intersect)
    if any(op.operator_name == "boolean" for op in potential_operators):
        return next(op for op in potential_operators if op.operator_name == "boolean")

    # return intersect (instead of filter)
    if any(op.operator_name == "intersect" for op in potential_operators):
        return next(op for op in potential_operators if op.operator_name == "intersect")

    # return superlative (instead of comparative)
    if any(op.operator_name == "superlative" for op in potential_operators):
        return next(op for op in potential_operators if op.operator_name == "superlative")

    # return group (instead of arithmetic)
    if any(op.operator_name == "group" for op in potential_operators):
        return next(op for op in potential_operators if op.operator_name == "group")

    # return comparative (instead of discard)
    if any(op.operator_name == "comparative" for op in potential_operators):
        return next(op for op in potential_operators if op.operator_name == "comparative")

    # return intersection (instead of intersection)
    if any(op.operator_name == "intersection" for op in potential_operators):
        return next(op for op in potential_operators if op.operator_name == "intersection")

    # avoid aggregate duplicity with arithmetic
    if any(op.operator_name == "aggregate" for op in potential_operators) and any(
            op.operator_name == "arithmetic" for op in potential_operators) and 'and' in step_text:
        potential_operators = [op for op in potential_operators if "aggregate" is not op.operator_name]

    if len(potential_operators) > 1:
        raise RuntimeError(f"Too many possibilities for \"{step_text}\"")

    if len(potential_operators) == 0:
        raise RuntimeError(f"0 possibilities for \"{step_text}\" after filtering!!")

    return potential_operators[0]


def get_step_seq2seq_repr(step):
    res = f"@@SEP_{step.full_operator_name}@@"
    for j, arg in enumerate(step.arguments):
        if j > 0:
            res += " ,"
        if arg.startswith('#'):
            arg = re.sub(r'#([1-9][0-9]?)', r'@@\g<1>@@', arg)
            arg = arg.replace('#REF', '@@REF@@')
        res += f" {arg}"
    return res


def parse_step_from_mycopynet(step_text):
    seperator = step_text.split(' ')[0]
    operation, sub_operation = re.match(r'@@SEP_([a-z]+)_?([a-z@]+)?@@', seperator)
    if sub_operation:
        sub_operation = sub_operation.replace('@', ' ')
    step = QDMR_OPERATION[operation]()
    step._sub_operator_name = sub_operation
    arguments_text = re.sub('@@([^@]*)@@', '#\g<1>', step_text.split(seperator)[1])
    step._arguments = arguments_text.split(seperator)[1].split(' , ')
