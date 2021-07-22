from Rule import Rule
from constants import *
import re as regex
from helper import findAll, getInputArgTag

def getStringRules(string, search, tag):
  rules = []
  idxs = []
  i = string.find(search)
  while i != -1:
    new_string = string[0: i] + string[i:].replace(search, tag, 1)
    if new_string != tag and new_string.find(">>") == -1:
      rules.append(new_string)
      idxs.append(i)
    i = string.find(search, i+1)
  return rules, idxs


# Returns list of possible rules
# Calculates the character-level differences between 2 rules or 2 vectors
# print("diff", rule2, rule1)
# Diff between ("12<input>", "one hundred and twenty-<output>") and ("2<input>", "twenty-<input>")
# Returns rule ("1<input>", "one hundred and <output>")

def diff(rule2, rule1):
  if not isinstance(rule1, Rule):
    rule1 = Rule(rule1)
  if not isinstance(rule2, Rule):
    rule2 = Rule(rule2)

  vector1 = rule1.getTuple()
  vector2 = rule2.getTuple()

  (v1_input, v1_output) = vector1
  (v2_input, v2_output) = vector2

  diff_rules_list = []

  v2_input_tag_idxs = findAll(v2_input, INPUT_ARG_SEARCH_TAG) # [2]
  v2_output_tag_idxs = findAll(v2_output, OUTPUT_ARG_TAG) # [23]
  # print("v2_input_tag_idxs", v2_input_tag_idxs)
  #print("v2_output_tag_idxs", v2_output_tag_idxs)
  # TODO Currently only looking at inputs in inputs and outputs in outputs, could consider mixed
  diff_inputs, diff_input_idxs = getStringRules(v2_input, v1_input, getInputArgTag(rule1.size)) # [("1<input>", "one hundred and <input>")], [1]
  diff_outputs, diff_output_idxs = getStringRules(v2_output, v1_output, OUTPUT_ARG_TAG)
  # print("diff_inputs", diff_inputs)
  # print("diff_input_idxs", diff_input_idxs)
  #print("diff_output_idxs", diff_output_idxs)
  if len(diff_inputs) == 0 or len(diff_outputs) == 0:
    return diff_rules_list

  # Store idxs in the rule?? eg. to figure out inversions like (<in0><in1>, <out1><out0>)
  for ri, idx_i in zip(diff_inputs, diff_input_idxs):

    diff_indexed_vsets = []
    new_v1_vsets = []
    input_sizes = []
    for idx, i in enumerate(v2_input_tag_idxs):
      if i >= idx_i and i < idx_i + len(vector1[0]):
        #print('skipping v2_input_tag_idxs', i)
        new_v1_vsets.append(rule2.validity_list[idx])
        continue
      diff_indexed_vsets.append((i, rule2.validity_list[idx]))
      input_sizes.append(rule2.input_sizes[idx])
    # The new_v1_vsets are mostly made of rule2_vsets however we could also combine with rule1_vsets
    diff_indexed_vsets.append((idx_i, [Rule(rule1.rule, rule1.arg_count, new_v1_vsets)]))
    input_sizes.append((idx_i, rule1.size))
    #print("diff_indexed_vsets", diff_indexed_vsets)

    for ro, idx_o in zip(diff_outputs, diff_output_idxs):
      new_diff = Rule((ri, ro), rule1.arg_count + 1)
      new_diff.size = rule2.size
      new_diff.input_sizes = input_sizes
      #print("diff_indexed_vsets", diff_indexed_vsets)
      for idx, (idx_vset, vset) in enumerate(sorted(diff_indexed_vsets, key=lambda x: x[0])):
        #print("idx,vset", idx, vset)
        new_diff.addToValidityList(idx, vset)
      diff_rules_list.append(new_diff)

  #print("rules", diff_rules_list)
  for r in diff_rules_list:
    #print("r", r)
    if not r.checkIsValid():
      print("diff", rule2, rule1)
      print("resulting rule", r)
      raise Exception("Issue in diff")
  return diff_rules_list