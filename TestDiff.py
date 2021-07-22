from Diff import diff 
from Rule import Rule

def DiffTest(rule2_tuple, rule2_validity_list_tuple, rule1_tuple, rule1_validity_list_tuple):
  rule2 = Rule(rule2_tuple)
  rule2.addToValidityList(*rule2_validity_list_tuple)
  rule1 = Rule(rule1_tuple)
  rule1.addToValidityList(*rule1_validity_list_tuple)
  rules = diff(rule2, rule1)
  print(rules)
  for rule in rules:
    print(rule)
    print(rule.validity_list[0][0])
    print(rule.getGeneratedVectors())
#
# Diff logic (rule2, rule1)
# Rule1 needs to be found on rule 2 so #tags(rule2) >= #tags(rule1)
# (0 tags, 0 tags) -> rules with 1 tag
# (1 tag, 0 tags) -> rules with 2 tags
# (1 tag, 1 tag) -> rules with 1 tag
# (2 tags, 0 tags) -> rules with 3 tags
# (2 tags, 1 tag) -> rules with 2 tags
# (2 tags, 2 tags) -> rules with 1 tag
# #tags(output) = #tags(rule2) - #tags(rule1) + 1

#DiffTest(('<v_input>1', '<v_output>ty-one'), (0, [('6', 'six'), ('7', 'seven'), ('8', 'eight')]), ('1', 'one'), (0, None))
#DiffTest(('22', 'twenty-two'), (0, None), ('2', 'two'), (0, None))

#DiffTest(('12<v_input>', 'one hundred and twenty-<v_output>'), (0, [('6', 'six'), ('7', 'seven'), ('8', 'eight')]), ('2<v_input>', 'twenty-<v_output>'), (0, [('1', 'one'), ('2', 'two'), ('5', 'five')]))

def DiffTest_checkMultipleInputsHundred():
  rule2 = Rule(('1<v_input><v_input>', '<v_output> hundred and <v_output>een'))
  rule2.addToValidityList(0, [Rule(('1', 'one'))])
  rule2.addToValidityList(1, [Rule(('8', 'eight'))])
  rule2.size = 3
  rule2.input_sizes = [(0,1), (1,1)]
  print("rule2 vectors", rule2.getGeneratedVectors())

  rule1 = Rule(('<v_input><v_input>', '<v_output> hundred and <v_output>'))
  rule1.addToValidityList(0, [Rule(('1', 'one')), Rule(('11', 'eleven'))])
  rule1.addToValidityList(1, [Rule(('10', 'ten')), Rule(('1', 'one'))])
  rule1.size = 3
  rule1.input_sizes = [(0,1), (1,2)]
  print("rule1 vectors", rule1.getGeneratedVectors())

  rules = diff(rule2, rule1)
  print(rules)
  for rule in rules:
    print(rule)
    print(list(rule.validity_list[0].values())[0])
    print(rule.getGeneratedVectors())


def DiffTest_checkMultipleInputsThousand():
  rule2 = Rule(('<v_input><v_input><v_input>', '<v_output> thousand, <v_output> hundred and <v_output>'))
  rule2.addToValidityList(0, [Rule(('1', 'one')), Rule(('2', 'two'))])
  rule2.addToValidityList(1, [Rule(('1', 'one'))])
  rule2.addToValidityList(2, [Rule(('10', 'ten')), Rule(('11', 'eleven')), Rule(('12', 'twelve'))])
  rule2.size = 4
  rule2.input_sizes = [(0,1), (1,1), (2,2)]
  print("rule2 vectors", rule2.getGeneratedVectors())
  
  rule1 = Rule(('<v_input><v_input>', '<v_output> hundred and <v_output>'))
  rule1.addToValidityList(0, [Rule(('1', 'one')), Rule(('2', 'two')), Rule(('4', 'four'))])
  rule1.addToValidityList(1, [Rule(('10', 'ten')), Rule(('11', 'eleven')), Rule(('12', 'twelve'))])
  rule1.size = 3
  rule1.input_sizes = [(0,1), (1,2)]
  print("rule1 vectors", rule1.getGeneratedVectors())

  rules = diff(rule2, rule1)
  print(rules)
  for rule in rules:
    print(rule)
    print(list(rule.validity_list[1].values())[0])
    print(rule.getGeneratedVectors())

def DiffTest_checkSingleInput():
  rule2 = Rule(('11<v_input>', 'one hundred and <v_output>een'))
  rule2.addToValidityList(0, [Rule(('8', 'eight'))])
  rule2.size = 3
  rule2.input_sizes = [(0,1)]
  print("rule2 vectors", rule2.getGeneratedVectors())

  rule1 = Rule(('1<v_input>', '<v_output>een'))
  rule1.addToValidityList(0, [Rule(('8', 'eight'))])
  rule1.size = 2
  rule1.input_sizes = [(0,1)]
  print("rule1 vectors", rule1.getGeneratedVectors())
  
  rules = diff(rule2, rule1)
  print(rules)
  for rule in rules:
    print(rule)
    print(list(rule.validity_list[0].values()))
    print(rule.getGeneratedVectors())


DiffTest_checkSingleInput()
DiffTest_checkMultipleInputsHundred()
DiffTest_checkMultipleInputsThousand()
