# Adapting Neural Turing Machines for linguistic assessments aggregation in neural-symbolic decision support systems

## Bibliographic record

- Authors: Alexander Demidovskij, Eduard Babkin
- Year: 2021
- Venue: Information and Control Systems
- DOI: 10.31799/1684-8853-2021-5-40-50
- arXiv: Not provided
- Source: openalex
- Cite key: demidovskij2021adapting
- URL: https://doi.org/10.31799/1684-8853-2021-5-40-50

## Verified abstract

Introduction: The construction of integrated neurosymbolic systems is an urgent and challenging task. Building neurosymbolic decision support systems requires new approaches to represent knowledge about a problem situation and to express symbolic reasoning at the subsymbolic level. Purpose: Development of neural network architectures and methods for effective distributed knowledge representation and subsymbolic reasoning in decision support systems in terms of algorithms for aggregation of fuzzy expert evaluations to select alternative solutions. Methods: Representation of fuzzy and uncertain estimators in a distributed form using tensor representations; construction of a trainable neural network architecture for subsymbolic aggregation of linguistic estimators. Results: The study proposes two new methods of representation of linguistic assessments in a distributed form. The first approach is based on the possibility of converting an arbitrary linguistic assessment into a numerical representation and consists in converting this numerical representation into a distributed one by converting the number itself into a bit string and further forming a matrix storing the distributed representation of the whole expression for aggregating the assessments. The second approach to translating linguistic assessments to a distributed representation is based on representing the linguistic assessment as a tree and coding this tree using the method of tensor representations, thus avoiding the step of translating the linguistic assessment into a numerical form and ensuring the transition between symbolic and subsymbolic representations of linguistic assessments without any loss of information. The structural elements of the linguistic assessment are treated as fillers with their respective positional roles. A new subsymbolic method of aggregation of linguistic assessments is proposed, which consists in creating a trainable neural network module in the form of a Neural Turing Machine. Practical relevance: The results of the study demonstrate how a symbolic algorithm for aggregation of linguistic evaluations can be implemented by connectionist (or subsymbolic) mechanisms, which is an essential requirement for building distributed neurosymbolic decision support systems.

## Evidence boundary

This card contains bibliographic metadata and the abstract returned by the
literature API. It does not infer datasets, metrics, numerical findings, or
limitations that are absent from that record. Verify those details against the
primary paper before using them in the proposal or experiments.
