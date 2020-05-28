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
            return "average"
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
            return f'{self.operator_name}_{self.sub_operator_name.strip().replace(" ", "@")}'
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
        assert '' not in self._arguments

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

    def generate_step_text_nicely(self):
        try:
            return self.generate_step_text()
        except (AssertionError, IndexError, AttributeError) as e:
            return self._generate_step_text_nicely()

    def _generate_step_text_nicely(self):
        """
        generate step text from the operation and the arguments without raising excpetion if the arguments/sub operations
        are bad because MyCopynet is not perfect
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
        self._arguments = [to_filter]
        if filter_condition:
            self._arguments.append(filter_condition)

    def generate_step_text(self):
        if 1 < len(self.arguments):
            return f"{self.arguments[0]} {self.arguments[1]}"
        return self.arguments[0]


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

    def generate_step_text(self):
        assert "#REF" in self.arguments[0]
        return self.arguments[0].replace("#REF", self.arguments[1])

    def _generate_step_text_nicely(self):
        if 0 == len(self.arguments):
            return ""
        elif 1 == len(self.arguments):
            words = self.arguments[0].split()
            if "#REF" in words:
                words.remove("#REF")
            return " ".join(words)
        if "#REF" not in self.arguments[0]:
            return f"{self.arguments[0]} of {self.arguments[1]}"


class QDMROperationAggregate(QDMROperation):
    """
    Example: "lowest of #2"
    Example: "the number of #1"
    """
    AGGREGATORS = ['number of', 'maximum', 'minimum',
                   'max', 'min', 'sum', 'total', 'average', 'avg', 'mean of', 'first', 'last']
    ORDER_AGGREGATORS = ['highest', 'largest', 'lowest', 'smallest', 'longest', 'shortest']
    ORDER_PREFIXES = ['two', 'second', 'three', 'third', 'four', 'fourth', 'five', 'fifth', 'six', 'sixth', '2nd',
                      '3rd', 'seventh', 'eighth', 'ninth', 'tenth', 'eleventh']

    @property
    def operator_name(self):
        return 'aggregate'

    @staticmethod
    def _is_aggr_valid_in_step(step, aggr):
        if step.startswith('the '):
            step = step.split('the ')[1].strip()

        if step.startswith(aggr) or step.startswith(f"{aggr} of"):
            return True

        before = step.split(aggr)[0].strip()
        non_meaningful_words = ["total", "combined", "count", "count the", "there", "next", "average", "which are",
                                "which is", "who had", "who has", "top", "find the"]
        if before in non_meaningful_words:
            return True
        for non_meaningful_word in non_meaningful_words:
            if before.startswith(f"{non_meaningful_word} "):
                before = before.split(f"{non_meaningful_word} ")[1].strip()

        if before.isdigit():
            return True

        # it's not aggregate, the aggregate is a part of a Construct state
        return False

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if len(references) != 1:
            raise TypeError(f'{step} is not {self.operator_name}')
        for aggr in self.AGGREGATORS + self.ORDER_AGGREGATORS:
            if f"{aggr} #" in step or f"{aggr} of #" in step:
                aggr_forms = [aggr]
                if aggr in self.ORDER_AGGREGATORS:
                    aggr_forms += [f'{prefix} {aggr}' for prefix in self.ORDER_PREFIXES]

                if not any(self._is_aggr_valid_in_step(step, aggr_form) for aggr_form in aggr_forms):
                    continue

                self._sub_operator_name = aggr
                self._arguments = []
                if aggr in self.ORDER_AGGREGATORS:
                    for prefix in self.ORDER_PREFIXES:
                        if prefix in step.split(aggr, 1)[0]:
                            if prefix == '2nd':
                                prefix = 'second'
                            elif prefix == '3rd':
                                prefix = 'third'
                            self._arguments = [prefix]
                            break
                    else:
                        before_word = step.split(aggr, 1)[0].strip().split(' ')[-1]
                        if before_word.isdigit():
                            self._arguments = [before_word]
                        else:
                            self._arguments = ['@@none@@']
                break
        else:
            raise TypeError(f'{step} is not {self.operator_name}')
        self._arguments += [f"#{references[0]}"]

    def generate_step_text(self):
        arg_index = 0
        full_aggregate = self.sub_operator_name
        if self.sub_operator_name in ['first', 'last']:
            full_aggregate = f"the {self.sub_operator_name}"
        elif self.sub_operator_name in ['maximum', 'minimum', 'max', 'min', 'total', 'average', 'avg']:
            full_aggregate = f"the {self.sub_operator_name} of"
        elif self.sub_operator_name in self.ORDER_AGGREGATORS:
            if len(self.arguments) > 1:
                arg_index += 1
            if len(self.arguments) > 1 and '@@none@@' not in self.arguments[0]:
                full_aggregate = f"the {self.arguments[0]} {self.sub_operator_name}"
            else:
                full_aggregate = f"the {self.sub_operator_name}"
        return f"{full_aggregate} {self.arguments[arg_index]}"

    def _generate_step_text_nicely(self):
        raise NotImplementedError()


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

    def generate_step_text(self):
        operator_name = self.sub_operator_name or ""
        if operator_name == "max":
            operator_name = "maximum of"
        elif operator_name == "min":
            operator_name = "minimum of"
        elif operator_name == "sum":
            operator_name = "sum of"
        elif operator_name == "average":
            operator_name = "average of"
        return f"{operator_name} {self.arguments[0]} for each {self.arguments[1]}".strip()


class QDMROperationSuperlative(QDMROperation):
    """
    Example: "#1 where #2 is highest"
    Example: "#1 where #2 is smallest"
    """
    RAW_SUPERLATIVES = ['highest', 'largest', 'most', 'smallest', 'lowest', 'smallest',
                        'least', 'longest', 'shortest', 'biggest']
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

    def generate_step_text(self):
        return f"{self.arguments[0]} where {self.arguments[1]} is {self.sub_operator_name}"


class QDMROperationComparative(QDMROperation):
    """
    Example: "#1 where #2 is at most three"
    Example: "#3 where #4 is higher than #2"
    """
    COMPARATIVES = ['same as', 'same as', 'higher than', 'larger than', 'smaller than', 'lower than', 'less than',
                    'more than', 'less than', 'at least', 'at most', 'equal', ' is ', 'are', 'was', 'contain',
                    'include', 'includes', 'has', 'have', 'end with', 'start with', 'ends with',
                    'starts with', 'begin']

    @property
    def operator_name(self):
        return 'comparative'

    def _init_from_raw_qdmr_step(self, step):
        references = extract_references_from_qdmr_step(step)
        if not (2 <= len(references) <= 3 and 'where' in step
                and (step.startswith('#') or step.startswith('the #'))):
            raise TypeError(f'{step} is not {self.operator_name}')
        if 'where at least one' in step or 'where at least some of' in step:
            # special comarative structure here
            if ' is ' not in step:
                raise TypeError(f'{step} is not {self.operator_name} - weird at least one sentence')
            to_filter = f"#{references[0]}"
            split_phrase = 'where at least some of' if 'where at least some of' in step else 'where at least one'
            comparative = step.split(split_phrase, 1)[1]
            attribute_1, attribute_2 = comparative.split(' is ', 1)
            attribute_1 = "one " + attribute_1
            self._arguments = [to_filter, attribute_1, attribute_2]
            self._sub_operator_name = "at_least"
            return
        elif 'where at least #' in step:
            # special comarative structure here
            if ' are ' not in step:
                raise TypeError(f'{step} is not {self.operator_name} - weird at least one sentence')
            to_filter = f"#{references[0]}"
            comparative = step.split('where at least', 1)[1]
            attribute_1, attribute_2 = comparative.split(' are ', 1)
            self._arguments = [to_filter, attribute_1, attribute_2]
            self._sub_operator_name = "at_least"
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
        if self.sub_operator_name == "at_least":
            return f"{self.arguments[0]} where at least {self.arguments[1]} is {self.arguments[2]}"
        return f"{self.arguments[0]} where {self.arguments[1]} is {self.sub_operator_name} {self.arguments[2]}"

    def generate_step_text_nicely(self):
        if 2 == len(self.arguments):
            self._arguments.append(self.arguments[0])
        return self.generate_step_text()


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
                boolean_prefix = expr.strip()
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
            self._sub_operator_name = f"{logical_op} {boolean_prefix}"
            return

        if step.split()[1].startswith("#"):
            # filter boolean, e.g., "if #1 is american"
            objects = f"#{references[0]}"
            condition = step.split(objects, 1)[1]
            self._arguments = [objects, condition]
            self._sub_operator_name = f"condition {boolean_prefix}"
            return

        if len(references) == 1 and not step.split()[1].startswith("#"):
            # projection boolean "if dinner is served on #1"
            objects = f"#{references[0]}"
            condition = step.split(' ', 1)[1].replace(objects, "#REF")
            self._arguments = [condition, objects]
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
                return

        self._arguments = [step.split(boolean_prefix, 1)[1]]
        self._sub_operator_name = boolean_prefix

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
            return
        else:
            refs = [f'#{ref}' for ref in references]
            self._arguments = refs

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

    def generate_step_text(self):
        arguments = ' , '.join(self.arguments)
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

    def arg_to_seq2seq(arg):
        arg = re.sub(r'#([1-9][0-9]?)', r'@@\g<1>@@', arg)
        arg = arg.replace('#REF', '@@REF@@')
        return arg

    args = [arg_to_seq2seq(arg) for arg in step.arguments]
    res += " " + (" @@,@@ ".join(args))
    return res


def parse_step_from_mycopynet(step_text):
    seperator = step_text.split(' ')[0]
    operation, sub_operation = re.match(r'@@SEP_([a-z]+)_?([a-z@_]+)?@@', seperator).groups()
    if sub_operation:
        sub_operation = sub_operation.replace('@', ' ')
    step = QDMR_OPERATION[operation]()
    step._sub_operator_name = sub_operation
    arguments_text = re.sub('@@([0-9|REF]*)@@', r'#\g<1>', step_text.split(seperator)[1]).strip()
    step._arguments = arguments_text.split(' @@,@@ ')
    step._arguments = [arg.strip() for arg in step.arguments]
    return step
