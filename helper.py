import re as regex

def getBatches(dataset, batch_size, first_batch_size=200):
  batches = [dataset[0:first_batch_size]]
  for i in range(first_batch_size,len(dataset), batch_size):
    batches.append(dataset[i:i+batch_size])
  return batches

def getCharacters(input):
    return list(input)

def getUniqueCharacters(input):
    return set(getCharacters(input))

def findAll(string, search):
  idxs = []
  for m in regex.finditer(search, string):
    idxs.append(m.start())

  return idxs

def getInputArgTag(size):
    return "<v_input{0}>".format(size)

def getOutputArgTag(size):
    return "<v_output{0}>".format(size)
