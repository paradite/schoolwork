This is the README file for A0093910H's submission
a0093910@u.nus.edu

== General Notes about this assignment ==

The program follows the skeleton provided, which uses a two-phase process of
building and testing the language model. The probability for each gram in a
particular language is stored in the language model during the building phase.
The probabilities that correspond to the grams in the test are then multiplied
to determine which language has the highest probability for a line.

In order to determine if a sentence is the "other language", a 2-step process is
added into the "testing phase". In step 1, for each sentence, if more than half
of the grams were not seen in the language model of a particular language, that
particular language will have a score (probability) of zero. In step 2, if all
known languages have a score (probability) of zero for a sentence, then the
sentence is determined to be from "other lanuge".

== Files included with this submission ==

build_test_LM.py - Build and test language model, all in one single file

== Statement of individual work ==

Please initial one of the following statements.

[X] I, A0093910H, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0093910H, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

Python 2 documentation: https://docs.python.org/2/index.html
