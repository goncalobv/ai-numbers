from num2words import num2words
import roman

from constants import *
from RuleEngine import RuleEngine

def generateDataset(upper=100):
  return [(str(i), num2words(i)) for i in range(upper)]

def generateRomanDataset(upper=100):
  return [(str(i), roman.toRoman(i)) for i in range(upper)]


dataset = generateDataset(1500)
# dataset = generateRomanDataset(1500)

# for i in dataset:
#   print(i)

re = RuleEngine()
re.load(dataset)
re.printKnowledge()
