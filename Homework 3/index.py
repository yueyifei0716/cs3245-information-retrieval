#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle
import string
import math


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def process_text(text):
    """
    Preprocesses the text.
    """
    # Convert the input text to lowercase
    text = text.lower()

    # Initialize an empty dictionary to hold the frequency counts
    frequencies = {}

    # Tokenize the text into sentences and words, and stem each word
    for sentence in nltk.sent_tokenize(text):
        for token in nltk.word_tokenize(sentence):
            if token in string.punctuation:
                continue
            stemmed_token = nltk.stem.PorterStemmer().stem(token)

            # Update the frequency count of the stemmed token
            frequencies[stemmed_token] = frequencies.get(stemmed_token, 0) + 1

    # Return the dictionary of term frequencies
    return frequencies


def compute_doc_length(frequencies):
    """
    Computes the document length using log-frequency weighting scheme.
    """
    # Initialize the document length
    doc_length = 0

    # Iterate over the term frequencies in the dictionary
    for tf in frequencies.values():
        # Apply log-frequency weighting scheme to the current term frequency
        log_tf = 1 + math.log(tf, 10)

        # Compute the square of the log-frequency weighted term frequency
        log_tf_squared = log_tf ** 2

        # Add the square of the log-frequency weighted term frequency to the document length
        doc_length += log_tf_squared

    # Compute the square root of the document length
    doc_length_sqrt = math.sqrt(doc_length)

    # Return the document length computed using log-frequency weighting scheme
    return doc_length_sqrt


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    # Get list of filenames in input directory
    filenames = sorted(os.listdir(in_dir))
    N = len(filenames)

    # Initialize dictionary with doc_length key
    dictionary = {'doc_length': {}}

    # Process each document
    for filename in filenames:
        full_filename = os.path.join(in_dir, filename)
        text = open(full_filename, 'r', encoding='utf8').read()
        frequencies = process_text(text)

        # Compute document length and update doc_length entry
        doc_length = compute_doc_length(frequencies)
        dictionary['doc_length'][int(filename)] = doc_length

        # Update dictionary and postings for each term in current document
        for term, tf in frequencies.items():
            if term in dictionary:
                df, postings = dictionary[term]
                df += 1
                postings.append((int(filename), 1 + math.log(tf, 10)))
                dictionary[term] = (df, postings)
            else:
                dictionary[term] = (1, [(int(filename), 1 + math.log(tf, 10))])

    # Write dictionary and postings to output files
    with open(out_dict, 'wb') as f_dict, open(out_postings, 'wb') as f_post:
        for term, value in dictionary.items():
            if term == 'doc_length':
                continue

            df, posting = value
            pointer = f_post.tell()
            pickle.dump(posting, f_post)

            # Compute IDF
            idf = math.log((N / df), 10)
            dictionary[term] = (idf, pointer)

        # Write final dictionary to file
        pickle.dump(dictionary, f_dict)

    print('Done.')


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # input directory
        input_directory = a
    elif o == '-d':  # dictionary file
        output_file_dictionary = a
    elif o == '-p':  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
