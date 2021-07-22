from constants import *
import re as regex
from helper import getUniqueCharacters

class Rule:
    # arg_count how many rules in the sequence 0 for atom, 1 for single rule, 2 for rule that calls other rules
    # valid_input input or list of inputs that are valid for the current rule
    def __init__(self, rule, arg_count=0, valid_input=None):
        self.rule = rule
        self.regex_rule = (rule[0].replace(INPUT_ARG_TAG, "(.+)"),
                           rule[1].replace(OUTPUT_ARG_TAG, "(.+)"))
        (self.rule_input, self.rule_output) = rule
        self.input_lengths = None
        self.size = None
        self.input_sizes = []
        self.arg_count = arg_count
        self.validity_list = []
        if valid_input is not None:
            self.validity_list = valid_input
        #self.addToValidityList(0, valid_input)

    def setInputLengths(self, input_lengths):
        self.input_lengths = input_lengths

    def buildRegex(self):
        if self.input_lengths is not None:
            self.regex_rule = self.rule
            i = 0
            while (self.regex_rule[0].count(INPUT_ARG_TAG) > 0):
                self.regex_rule = (self.regex_rule[0].replace(
                    INPUT_ARG_TAG, "(.{{{0}}})".format(self.input_lengths[i]),
                    1), self.regex_rule[1].replace(OUTPUT_ARG_TAG, "(.+)"))
                i += 1
        else:
            self.regex_rule = (self.rule[0].replace(INPUT_ARG_TAG, "(.+)"),
                               self.rule[1].replace(OUTPUT_ARG_TAG, "(.+)"))

    def addToValidityList(self, idx, valid_input):
        while idx >= len(self.validity_list):
            self.validity_list.append(dict())

        if valid_input is None:
            return
        if isinstance(valid_input, list):
            for v in valid_input:
                self.validity_list[idx][v.getTuple()] = v
        elif isinstance(valid_input, dict):
            self.validity_list[idx].update(valid_input)
        #if isinstance(valid_input, dict):
        #  self.validity_list[idx].update(valid_input)
        else:
            raise Exception('Something is wrong with validity list')
            self.validity_list[idx][valid_input] = valid_input

    def addAllToValidityList(self, validity_list):
        #print("addAllToValidityList", self.validity_list, validity_list)
        if len(self.validity_list) != len(validity_list):
            #print("current rule", self)
            #print("validity list to add", validity_list)
            raise Exception('Validity lists dont have the same length')

        for idx, l in enumerate(validity_list):
            self.validity_list[idx].update(l)

    def getTuple(self):
        return self.rule

    def getRegex(self):
        self.buildRegex()
        return self.regex_rule

    def apply(self, vector):
        if isinstance(vector, Rule):
            v = vector.rule
        else:
            v = vector

        (v_input, v_output) = v

        rule = (self.rule_input.replace(INPUT_ARG_TAG, v_input, 1)
                if self.rule_input else None,
                self.rule_output.replace(OUTPUT_ARG_TAG, v_output, 1)
                if self.rule_output else None)

        arg_count = vector.arg_count if isinstance(vector, Rule) else None
        vset = vector.validity_list if isinstance(vector, Rule) else None

        return Rule(rule, arg_count=arg_count, valid_input=vset)

    def applyValidVectors(self):
        res = []
        for l in self.validity_list:
            for v in l.values():
                res.append(self.apply(v))
        return res
        #return [self.apply(v) for v in self.validity_list]

    def getGeneratedVectors(self, validity_list=None, idx=0):
        validity_list = validity_list or self.validity_list

        if len(validity_list) == 0:
            return [self]

        if idx == len(validity_list):
            return [self]

        vectors = set()
        for v in validity_list[idx].values():
            vectors.update(self.apply(v).getGeneratedVectors())
            vectors.update(
                self.apply(v).getGeneratedVectors(validity_list, idx + 1))

        return vectors

    def getIndices(self):
        simplified_rule_input = self.rule_input.replace(INPUT_ARG_TAG, "")
        return getUniqueCharacters(simplified_rule_input)

    def checkIsValid(self):
        count_input_tag = len(regex.findall(INPUT_ARG_SEARCH_TAG, self.rule[0]))
        # count_input_tag = self.rule[0].count(INPUT_ARG_SEARCH_TAG)
        count_output_tag = self.rule[1].count(OUTPUT_ARG_TAG)

        if count_input_tag != count_output_tag:
            print("Count input tag does not match count output tag", self)
            return False

        if len(self.validity_list) != count_input_tag:
            print("Validity list does not have same length of count input tag",
                  self)
            return False
        return True

    def __repr__(self):
        return str(self.rule)

    def __str__(self):
        str_validity_list = ",".join(
            [str(list(l.values())) for l in self.validity_list])
        str_input_sizes = ",".join(
            [str(i_sizes) for i_sizes in self.input_sizes])
        #str_validity_list = ",".join(map(str, list(self.validity_list.values())))
        return "Rule{r=" + str(self.rule) + ", c=" + str(
            self.arg_count
        ) + ", size=" + str(
            self.size
        ) + ", input_sizes=[" + str_input_sizes + "], vset=[" + str_validity_list + "]}"

    def __eq__(self, other):
        return self.rule == other.rule

    def __hash__(self):
        return hash(self.rule)
