#!/usr/bin/python3
import pickle
import re
import nltk
import sys
import getopt
import math
import string
from nltk.stem import WordNetLemmatizer


# define operator precedence
precedence = {'NOT': 3, 'AND': 2, 'OR': 1}


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def get_term_frequency(query_lst):
    # Create dictionary for term frequency
    tf_dict = {}
    for token in query_lst:

        # If term already in dictionary, add 1
        if token in tf_dict:
            tf_dict[token] += 1

        # If term is not in dictionary, add it with val = 1
        else:
            tf_dict[token] = 1

    return tf_dict


def compute_tf_idf_weight(tf_dict, dictionary):
    # Create dictionary for tf-idf weight
    weight_dict = {}
    for term, tf in tf_dict.items():
        if term in dictionary:

            # Get idf from dictionary
            idf = dictionary[term][0]

            # Calculate the weight and store in tf-idf weight dictionary
            weight_dict[term] = (1 + math.log(tf, 10)) * idf

    return weight_dict


def create_term_doc_dictionary(query, dictionary, postings_file):
    term_doc_dictionary = {}
    unique_docID = set()

    for term in query:
        if term in dictionary:
            address = dictionary[term][1]
            postings_file.seek(address)
            posting = pickle.load(postings_file)

            for docID, log_tf in posting:
                document_length = dictionary.get("doc_length", {}).get(docID)
                if document_length is not None:

                    # Length normalization
                    term_doc_dictionary.setdefault(term, {})[docID] = log_tf / document_length

                    # Add to unique_docID
                    unique_docID.add(docID)

    return term_doc_dictionary, unique_docID


def keyword_search(query_term_vector, term_doc_dictionary, docID, top_n):
    results = []

    # Iterate over each element in docID
    for doc in docID:
        score = 0

        # For each term and its weight in the query term vector
        for term, weight in query_term_vector.items():
            # If the term appears in the document
            if doc in term_doc_dictionary[term]:
                # Add weighted score to the document's total score
                term_score = term_doc_dictionary[term][doc]
                score += weight * term_score

        # Add the document ID and its score to the results list
        results.append((score, int(doc)))

    # Sort the results by score in decreasing order and by document ID in ascending order
    sorted_results = sorted(results, key=lambda x: (-x[0], x[1]))

    # Return the top n document IDs as a list of strings
    top_n_docIDs = [str(docID) for score, docID in sorted_results[:top_n]]
    return top_n_docIDs


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement yogur code in below

    # Open dictionary file
    f_dict = open(dict_file, 'rb')
    # Load dict_file file to memory
    dictionary = pickle.load(f_dict)
    f_dict.close()

    # Open postings file
    f_posting = open(postings_file, 'rb')

    # Open queries file
    f_queries = open(queries_file, 'r', encoding="utf8")
    query = f_queries.read()
    queries = query.splitlines()
    f_queries.close()

    # Open the result_file, the results_file will automatically close
    with open(results_file, 'w+') as f:
        for query in queries:
            # Tokenize, stemming and case folding for query
            stemmer = nltk.stem.PorterStemmer()
            tokens = query.split()

            # If the query is not empty
            if tokens:
                # Remove period at end of query
                tokens[-1] = tokens[-1].rstrip('.')
            stemmed_tokens = [stemmer.stem(token.lower()) for token in tokens if token not in string.punctuation]

            # Get the term frequency of the query
            tf_dict = get_term_frequency(stemmed_tokens)

            # Compute the tf_idf_weight
            query_vectors = compute_tf_idf_weight(tf_dict, dictionary)

            # Get the term doc dictionary and unique docID
            term_doc_dict, docID = create_term_doc_dictionary(stemmed_tokens, dictionary, f_posting)

            # Keyword search and get top n element, currently set to 10
            result = keyword_search(query_vectors, term_doc_dict, docID, 10)
            # print(result)

            # Join it with space and write to output
            f.write(' '.join(result) + '\n')

    # Close posting file
    f_posting.close()


# run_search("dictionary.txt", "postings.txt", "query.txt", "output.txt")


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)


run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
