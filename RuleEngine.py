from Rule import Rule
from Diff import diff
from helper import getBatches

class RuleEngine:
  def __init__(self):
    self.knowledge = dict()
    self.characters = dict()
 
  def load(self, dataset):
    self.dataset = dataset
 
    for idx, batch in enumerate(getBatches(dataset, 1000)):
      print("Starting batch", idx)
      for d in batch:
        self.learn(d)
      # self.compress(10)
 
 
  def addRule(self, rule):
    self.knowledge[rule.getTuple()] = rule
    for i in rule.getIndices():
      if i not in self.characters:
        self.characters[i] = []
 
      self.characters[i].append(rule)
 
  def getRule(self, rule):
    return self.knowledge[rule.getTuple()]
 
  def removeRule(self, rule):
    if self.containsRule(rule):
      self.knowledge.pop(rule.getTuple())
 
  def containsRule(self, rule):
    return (rule.getTuple() in self.knowledge)
 
  
##########################################################################################################################################

  def getCandidateRules(self, d):
    candidates = []
    for k in self.knowledge.values():
      diff_rules = diff(d, k)
      for r in diff_rules:
          if self.containsRule(r):
            return [r]
      for r in diff_rules:
        candidates.extend(self.getCandidateRules(r))

    if len(candidates) == 0:
      candidates.append(d)

    return candidates
 
##########################################################################################################################################

  def learn(self, datapoint):
    d = Rule(datapoint)

    d.size = len(datapoint[0])
    # print("Learning rule for", d)
    candidates = self.getCandidateRules(d)

    # if len(candidates) == 0:
    #   print("- Adding atom", d)
    #   self.addRule(d)
    #   return
    # print("=======candidates========")
    # for c in candidates:
    #   print(c)
    # print("=====candidates (end)=====")

    exists_rule = False
    for c in candidates:
      if self.containsRule(c):
        exists_rule = True
        existing_rule = self.getRule(c)
        existing_rule.addAllToValidityList(c.validity_list)
        # print("- Existing rule", existing_rule)
    
    if exists_rule == False:
        # print("- Adding simple diff rule to knowledge", candidates[0])
        self.addRule(candidates[0])
  
##########################################################################################################################################

  def learnSequences(self):
    knowledge_seqs = dict() # mapping from initial rule, to sequence of rules
 
    for k1 in self.knowledge.values():
      exists_rule = False
      rules = []
      for k2 in self.knowledge.values():
        diffs = diff(k2, k1)
        #rules.extend({"rule": r, "k2": k2.rule, "k1": k1.rule, "validset2": k2.validity_list, "validset1": k1.validity_list} for r in diffs)        
        rules.extend(diffs)
        #if len(diffs) > 0:
        #  print("k2", k2)
        #  print("k1", k1)
        #  print("diffs", diffs, "\n")
 
      for rule in rules:
        #print("rule", rule)
        #print("gen vectors")
        #for v in rule.getGeneratedVectors():
          #print(v)
 
        if rule.getTuple() in knowledge_seqs:
          exists_rule = True
          existing_rule = knowledge_seqs[rule.getTuple()]
          #print("current", rule, "existing", existing_rule)
          existing_rule.addAllToValidityList(rule.validity_list)
          continue
 
        if not exists_rule:
          knowledge_seqs[rule.getTuple()] = rule
          exists_rule = True
 
    for k in knowledge_seqs.values():
      if self.containsRule(k):
        #print('contains rule', self.getRule(k))
        #print('current rule', k)
        existing_rule = self.getRule(k)
        #print("current2", rule, "existing2", existing_rule)
        existing_rule.addAllToValidityList(k.validity_list)
        #self.addRule(k) # replace current rule to avoid any loops - oversimplification
      else:
        #print('new rule', k)
        self.addRule(k)
      
      # print(k)
      # for v in k.validity_list:
      #   print('vset',v)
 
    return knowledge_seqs
  
##########################################################################################################################################

  def consolidate(self):
    # If a rule can only produce items already produced by other rules, then that rule can be removed
 
    # First need to pass again through the whole dataset as some rules were not exposed to all inputs (consolidate step)
    # Eg. ('7<v_input>', 'seventy-<v_output>') True [('2', 'two'), ('3', 'three'), ('4', 'four'), ('5', 'five'), ('6', 'six'), ('7', 'seven'), ('8', 'eight'), ('9', 'nine')]
    # Not exposed to 71
 
    # Consolidate learning
    for d in self.dataset:
      exists_rule = False
      rules = []
 
      # Build a list of all rules that can explain d from knowledge atoms k
      for k in self.knowledge.values():
        rules.extend(diff(Rule(d), k))
      
      for rule in rules:
        if rule.getTuple() in self.knowledge:
          exists_rule = True
          existing_rule = self.knowledge[rule.getTuple()]
          existing_rule.addToValidityList(rule.validity_list)
          continue
 
########################################################################################################################################## 

  # Prune useless rules (compression)
  def prune(self, verbose=0):
    d_count, delete_rules = self.generateDeleteSet()
    
    if verbose == 1:
      print("Count of rules prunning", len(delete_rules))
      for k in delete_rules:
        print(k)
 
    for k in delete_rules:
      self.knowledge.pop(k.getTuple())
 
    return delete_rules
 
##########################################################################################################################################
 
  def generateDeleteSet(self):
    # How many rules produce d
    d_count = dict()
 
    for k in self.knowledge.values():
      for d in k.getGeneratedVectors():
        if d.getTuple() not in d_count:
          d_count[d.getTuple()] = 0
        d_count[d.getTuple()] += 1
 
    #print("dcount initial", d_count)
    delete_rules = set()
 
    # This code is not 100% perfect, it is possible that 2 rules are non-essential as they can both
    # produce the same number, but then one of them would become essential by removing the other -- which one is the most important?
    # This code removes one of those rules
    for k in self.knowledge.values():
      essential_rule = False
      for d in k.getGeneratedVectors():
        if d_count[d.getTuple()] == 1:
          essential_rule = True
      
      # Awesome, now let's add the rule to the delete set
      if not essential_rule: #  and len(k.validity_list) == 1
        delete_rules.add(k)
    
    def getValidityListLength(rule):
      return len(rule.validity_list)

    def getGeneratedVectorsLength(rule):
      return len(rule.getGeneratedVectors())
    # delete_rules contains candidates for deletion, though deleting all of them might actually delete essential rules
    # sort the delete_rules by the size of the validity_list
    delete_list = sorted(delete_rules, key=getGeneratedVectorsLength, reverse=False)
    #print("delete_list", delete_list)
      # Rule is not essential, go through all numbers that can be generated by this rule and decrement count
    for k in delete_list:
      # Confirm that the rule remains non-essential
      essential_rule = False
      for d in k.getGeneratedVectors():
        if d_count[d.getTuple()] == 1:
          essential_rule = True
          break
 
      # Rule is now essential (because another non-essential was marked for removal; don't delete this one)
      if essential_rule: 
        delete_rules.remove(k)
      else:
        # Rule is still essential, decrease counters
        for d in k.getGeneratedVectors():
          d_count[d.getTuple()] -= 1
 
    return d_count, delete_rules
 
##########################################################################################################################################

  def compress(self, max_cycles=100):
    pruned_rules = self.prune()
    seqs = self.learnSequences()
    cycles = 1
 
    while len(pruned_rules) > 0 and len(pruned_rules) != len(seqs):
      pruned_rules = self.prune()
      seqs = self.learnSequences()
      cycles += 1
 
      if cycles == max_cycles:
        print("Max cycles=", max_cycles, " reached")
        break
        #raise Exception("Max cycles=", max_cycles, " reached")
 
    print("seqs", len(seqs), "pruned rules", len(pruned_rules))
    return cycles
 
 
##########################################################################################################################################
 
  def verifyRulesOnDataset(self):
    d_count = dict()
 
    for k in self.knowledge.values():
      for v in k.getGeneratedVectors():
        if v.getTuple() not in d_count:
          d_count[v.getTuple()] = 0
        d_count[v.getTuple()] += 1
 
    def toInt(elem):
      return int(elem[0])
 
    generated_dataset = sorted(d_count.keys(), key=toInt)
 
    if generated_dataset == self.dataset:
      return
 
    gen_set = set(generated_dataset)
    orig_set = set(self.dataset)
    incorrectly_generated = gen_set.difference(orig_set)
    not_generated = orig_set.difference(gen_set)
 
    print("Incorrectly generated by learnt rules")
    for k in sorted(incorrectly_generated, key=toInt):
      print(k)
 
    print("\nNot generated by learnt rules")
    for k in sorted(not_generated, key=toInt):
      print(k)
 
    raise Exception("Inconsistency identified between vectors generated from rules and original dataset")
 
##########################################################################################################################################

  def generateKnowledgeComponents(self):
    self._knowledge_atoms = dict()
    self._knowledge_diffs = dict()
    self._knowledge_seqs = dict()
 
    for k in self.knowledge.values():
      # Atoms correspond to arg_count = 0
      if k.arg_count == 0:
        self._knowledge_atoms[k.getTuple()] = k
      # Diffs correspond to arg_count = 1
      elif k.arg_count == 1:
        self._knowledge_diffs[k.getTuple()] = k
        # Seqs correspond to arg_count >= 2
      else:
        self._knowledge_seqs[k.getTuple()] = k
 
 
##########################################################################################################################################
 
  def printKnowledge(self):
    self.generateKnowledgeComponents()
    print('\nAtoms')
    print("Count atoms", len(self._knowledge_atoms), "\n")
    for k in self._knowledge_atoms.values():
      print(k)
 
    print('\nDiffs')
    print("Count diffs", len(self._knowledge_diffs), "\n")
    for k in self._knowledge_diffs.values():
      print(k)
 
    print('\nSeqs')
    print("Count seqs", len(self._knowledge_seqs), "\n")
    for k in self._knowledge_seqs.values():
      print(k)