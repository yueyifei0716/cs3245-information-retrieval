#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt
import math

dict_label = {"malaysian": 0, "indonesian": 0, "tamil": 0}

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print('building language models...')

    # Initialize a dictionary to store the language model
    dict_lm = {}

    # Open the input file for reading
    with open(in_file, 'r') as input_file:
        for line in input_file:
            # Split the line into label and text
            split_string = line.split(" ", 1)

            # Extract the label and the text from the split line
            # The first element is the label, the second is the text with punctuations removed
            label = split_string[0]
            text = re.sub(r'[^\w\s]', '', split_string[1])

            # Generate 4-gram phrase
            fourgrams = [text[i: i + 4] for i in range(len(text) - 4 + 1)]

            # Update the frequency of each 4-gram phrase in the language model
            for fourgram in fourgrams:
                if fourgram not in dict_lm:
                    dict_lm[fourgram] = {label: 0 for label in dict_label}
                dict_lm[fourgram][label] += 1

    # Close the input file
    input_file.close()

    # Calculate the total word count of each language
    for label_counts in dict_lm.values():
        for key_l in dict_label:
            dict_label[key_l] += label_counts[key_l]

    # Copy the language model dictionary to another dictionary LM for return
    LM = {key: value.copy() for key, value in dict_lm.items()}

    # Compute the probability of each 4-gram phrase for each language
    for string_dict in LM.values():
        for label in dict_label:
            string_dict[label] = (string_dict[label] + 1) / (len(dict_lm) + dict_label[label])

    # Return the language model
    return LM


def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")

    # Open the input file and output file
    with open(in_file, 'r') as input_file, open(out_file, 'w') as output_file:
        # Loop through each line in the input file
        for line in input_file:
            # Initialize the label probability dictionary
            label_probability = {'malaysian': 0, 'indonesian': 0, 'tamil': 0}

            # Remove the punctuations from the line
            line = re.sub(r'[^\w\s]', '', line)

            # Generate 4-gram phrases from the line
            fourgrams = [line[i: i + 4] for i in range(len(line) - 4 + 1)]
            # Initialize the missing count
            miss_count = 0
            # Calculate the probability
            for fourgram in fourgrams:
                # Check if the 4-gram phrase exists in the language model
                if fourgram in LM:
                    # Update the label probabilities
                    for key in dict_label:
                        label_probability[key] += math.log(LM[fourgram][key])
                else:
                    # Increase the missing count if the 4-gram phrase doesn't exist in the language model
                    miss_count += 1

            # Check if the missing count is less than or equal to 0.7 (threshold)
            if miss_count / len(fourgrams) <= 0.7:
                # Sort the label probabilities in descending order
                sorted_labels = sorted(label_probability.items(), key=lambda label_probability: label_probability[1], reverse=True)
                # Get the most probable label
                most_probable_label = sorted_labels[0]
                result = most_probable_label[0]
            else:
                result = "other language"

             # Write the result to the output file
            output_file.write(result + " " + line)

    # Close the output and input file
    output_file.close()
    input_file.close()


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
