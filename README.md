# AI Numbers to Words - An interpretable & incremental approach

## Model architecture proposal and application to a simple task
Machine Learning models often lack transparency on their model parameters and reuse learnings from previous tasks or data. We propose a simple rule-based model architecture that is both interpretable - the model knowledge is represented by a list of rules that can be easily understood - and incremental - the model leverages previous knowledge to learn new samples.
The model is then applied for the task of translating numbers (like “234”) to words (“two hundred and thirty-four”). We also apply the same model to translate roman numerals to words.


### The concept
Samples fed to the model are represented as pairs of input-outputs such as (“234”, “two hundred and thirty-four”), reusing a similar pattern for the samples of supervised machine learning models. These samples are two-dimensional vectors.

A rule is represented by a two-dimensional vector (v) and a validity set (vset), for example `{r=(“a”, “b”) vset={}}`. The vector stores the character-level difference between the new sample and one other existing rule in the model knowledge. The validity set stores links to rules that can be applied to the current one to generate valid vectors. For example, if the rule `{r=(“a”, “b”) vset={}}` exists in the model knowledge and there is a rule `{r=(“c<input>”, “d<output>”) vset={(“a”,”b”)}}`, then the model is able to generate the vector (“ca”, “db”), by applying the vset to the rule vector.

Each learnt rule can then be represented as an N-ary tree, similar to a dictionary, that is able to generate samples by performing a path from the root to a leaf node.

The model knowledge is simply a list of the learnt rules.

### Model learning
To illustrate how the model learns, we apply it to the task of translating numbers to words.

Initially, the model knowledge is empty. The first sample (“1”, “one”) cannot be matched to any knowledge rules and so is added as the first knowledge rule as an atom (since it cannot be decomposed in differences with other rules). The same happens for the samples corresponding to the numbers 2-13. Once the model reaches the sample 14, it will compare (“14”, “fourteen”) with all the available knowledge rules and identify a character-level match with (“4”, “four”), generating the first difference rule:

`{r=(“1<input>”, “<output>teen”) vset={(“4”, “four”)}`

The 2-dimensional vectors generated by the `diff` algorithm at character-level follow a similar structure to vector arithmetics:

`(“1<input>”, “<output>teen”) = (“14”, “fourteen”) - (“4”, “four”)`

At every new sample, the model will aim to learn and generate differences with already existing knowledge rules, thus minimizing the incremental learning. For example, for the numbers between 21 and 29, the model learns a single rule and keeps updating the validity set:

`{r=('2<v_input1>', 'twenty-<v_output>'), vset=[[('1', 'one'), ('2', 'two'), ('3', 'three'), ('4', 'four'), ('5', 'five'), ('6', 'six'), ('7', 'seven'), ('8', 'eight'), ('9', 'nine')]]}`

Conversely, this rule is able to generate all numbers from 21-29.

### Few examples of learnt rules
Below we provide some interesting examples extracted from the model knowledge by training with a dataset from the numbers 1-1500:

- Rule that learns numbers 60, 70 and 90: `Rule{r=('<v_input1>0', '<v_output>ty') vset=[[('6', 'six'), ('7', 'seven'), ('9', 'nine')]]}`

- Rule that learns numbers 61-69, 71-79, 91-99: `Rule{r=('<v_input1><v_input1>', '<v_output>ty-<v_output>') vset=[[('6', 'six'), ('7', 'seven'), ('9', 'nine')],[('1', 'one'), ('2', 'two'), ('3', 'three'), ('4', 'four'), ('5', 'five'), ('6', 'six'), ('7', 'seven'), ('8', 'eight'), ('9', 'nine')]]}`

- Rule that learns numbers x00 from 100 to 900: `Rule{r=('<v_input1>00', '<v_output> hundred') vset=[[('1', 'one'), ('2', 'two'), ('3', 'three'), ('4', 'four'), ('5', 'five'), ('6', 'six'), ('7', 'seven'), ('8', 'eight'), ('9', 'nine')]]}`

- Rule that learns any 3-digit numbers: `Rule{r=('<v_input1><v_input2>', '<v_output> hundred and <v_output>') vset=[[('1', 'one'), ('2', 'two'), ('3', 'three'), ('4', 'four'), ('5', 'five'), ('6', 'six'), ('7', 'seven'), ('8', 'eight'), ('9', 'nine')],[('10', 'ten'), ('11', 'eleven'), ('12', 'twelve'), ('13', 'thirteen'), ('1<v_input1>', '<v_output>teen'), ('15', 'fifteen'), ('1<v_input1>', '<v_output>een'), ('20', 'twenty'), ('2<v_input1>', 'twenty-<v_output>'), ('30', 'thirty'), ('3<v_input1>', 'thirty-<v_output>'), ('40', 'forty'), ('4<v_input1>', 'forty-<v_output>'), ('50', 'fifty'), ('5<v_input1>', 'fifty-<v_output>'), ('<v_input1>0', '<v_output>ty'), ('<v_input1><v_input1>', '<v_output>ty-<v_output>'), ('<v_input1>0', '<v_output>y'), ('<v_input1><v_input1>', '<v_output>y-<v_output>')]]}`

### Additional notes
This project is a prototype for an incremental and interpretable model architecture. The goal is to materialize a concept rather than to deliver a production-ready learning model. Future work would be required to optimize the code for datasets larger than 10k entries and to adapt to other language tasks.
