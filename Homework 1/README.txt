This is the README file for A0269377J's submission
Email: e1112349@u.nus.edu

== Python Version ==

I'm using Python Version <3.10.9> for
this assignment.

== General Notes about this assignment ==

The program is an implementation of a simple 4-gram based language
model to identify the language of a given text. It supports three
languages, "malaysian", "indonesian", and "tamil". The program has
two main functions: build_LM and test_LM.

The build_LM function takes an input file as an argument, reads the
file line by line, removes punctuations from the text, generates 4-gram
phrases from the text, and updates the frequency of each 4-gram phrase
for each language. The frequency of each 4-gram phrase is used to calculate
the probability of each 4-gram phrase for each language, which is stored
in a dictionary called the language model. The language model is returned
by the function.

The test_LM function takes three arguments: an input file, an output file and
the language model generated by the build_LM function. The function reads the
input file line by line, removes the punctuations from the text, generates 4-gram
phrases from the text, and calculates the probability of each language for the text.
If the missing count of 4-gram phrases, which are not present in the language model,
is less than or equal to 0.7 (A threshold that performs well based on my multiple
tests), the function calculates the most probable language. If the missing count
is greater than 0.7 , the function classifies the text as "other language".
The result is written to an output file and will be used for the following evaluations.

== Files included with this submission ==

build_test_LM.py    # source code
README.txt          # overview of HW #1 program

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0269377J, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I, A0269377J, did not follow the class rules regarding homework
assignment, because of the following reason:

I suggest that I should be graded as follows:

== References ==
