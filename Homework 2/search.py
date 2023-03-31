#!/usr/bin/python3
import pickle
import re
import nltk
import sys
import getopt
import math
from nltk.stem import WordNetLemmatizer


# define operator precedence
precedence = {'NOT': 3, 'AND': 2, 'OR': 1}


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def shunting_yard(expression):
    # initialize stacks for operators and output
    operator_stack = []
    output = []

    # iterate over each token in the expression
    for token in expression:
        # if token is an operator, move higher-precedence operators from stack to output,
        # then add operator to stack
        if token in precedence:
            prec = precedence[token]
            while operator_stack and operator_stack[-1] != '(' and prec <= precedence[operator_stack[-1]]:
                output.append(operator_stack.pop())
            operator_stack.append(token)
        # if token is left parenthesis, add to stack
        elif token == '(':
            operator_stack.append(token)
        # if token is right parenthesis, move operators from stack to output until matching
        # left parenthesis is found, then discard both parentheses
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()
        # if token is in lower case, add to output
        elif token not in precedence:
            output.append(token)

        else:
            print("Operand Error, some operand in query may have Uppercase letter, please check the queries.txt")
            exit(0)

    # move remaining operators from stack to output
    while operator_stack:
        output.append(operator_stack.pop())

    return output


# Search the target from dict_file, then return the corresponding list in Posting_file and return as dictionary
def get_all_posting(target, dictionary_path, posting_path):
    with open(dictionary_path, 'rb') as f:
        dictionary = pickle.load(f)
    postings = open(posting_path, 'rb')

    # Create a dictionary that will store all sub_dictionary
    dict = {}

    for word in target:
        # Create a sub_dictionary that will store frequency and list of pointer
        sub_dict = {}
        if word in dictionary:
            frequency = dictionary[word]["doc_freq"]
            sub_dict.update({"doc_freq": frequency})
            # get pointer value
            pointer = dictionary[word]["pointer"]
            # Get the list from posting by seeking corresponding pointer
            postings.seek(pointer, 0)
            postings_list = pickle.load(postings)
            sub_dict.update({"doc_list": postings_list})
            dict.update({word : sub_dict})
        else:
            sub_dict.update({"doc_freq": 0})
            sub_dict.update({"doc_list": []})
            dict.update({word: sub_dict})

    f.close()
    postings.close()
    # Return both dictionary and total_list
    return dict


def get_skip_pointer(value):
    return int(value[1:]) if isinstance(value, str) else None


def Boolean_NOT(operand_list1, operand_list2):
    result = []

    # Initialize both pointer
    curr_index_lst1 = curr_index_lst2 = 0
    skip_pointer_lst1 = skip_pointer_lst2 = 0

    while True:
        if curr_index_lst2 >= len(operand_list2):
            return result

        elif curr_index_lst1 >= len(operand_list1):
            result.extend(value for value in operand_list2[curr_index_lst2:] if get_skip_pointer(value) == None)
            return result

        curr_value_lst1 = operand_list1[curr_index_lst1]
        curr_value_lst2 = operand_list2[curr_index_lst2]

        # check if current index position is a skip pointer
        skip_pointer_lst1 = get_skip_pointer(curr_value_lst1)
        skip_pointer_lst2 = get_skip_pointer(curr_value_lst2)

        # Add 1 or 0 to move the current pointer to real value
        curr_index_lst1 += 1 if skip_pointer_lst1 else 0
        curr_index_lst2 += 1 if skip_pointer_lst2 else 0
        curr_value_lst1 = operand_list1[curr_index_lst1]
        curr_value_lst2 = operand_list2[curr_index_lst2]

        if curr_value_lst1 == curr_value_lst2:
            # If it exists in both list, then move to next index
            curr_index_lst1 += 1
            curr_index_lst2 += 1

        elif curr_value_lst1 > curr_value_lst2:
            result.append(curr_value_lst2)
            if skip_pointer_lst2 and operand_list2[skip_pointer_lst2] <= curr_value_lst1:
                result += operand_list2[curr_index_lst2 + 1: skip_pointer_lst2]
                curr_index_lst2 = skip_pointer_lst2 + 1
                skip_pointer_lst2 = get_skip_pointer(operand_list2[skip_pointer_lst2])
            else:
                curr_index_lst2 += 1

        elif curr_value_lst1 < curr_value_lst2 and skip_pointer_lst1 is not None:
            # Check if we can use skip pointer to jump ahead
            if skip_pointer_lst1 < len(operand_list1) - 1 and operand_list1[skip_pointer_lst1 + 1] <= curr_value_lst2:
                curr_index_lst1 = skip_pointer_lst1 + 1
                skip_pointer_lst1 = get_skip_pointer(operand_list1[skip_pointer_lst1])
            else:
                curr_index_lst1 += 1
        else:
            curr_index_lst1 += 1

    return result


def Boolean_AND(operand_list1, operand_list2):
    result = []

    # Initialize both pointer
    curr_index_lst1 = curr_index_lst2 = 0
    skip_pointer_lst1 = skip_pointer_lst2 = 0

    while True:
        if curr_index_lst1 >= len(operand_list1) or curr_index_lst2 >= len(operand_list2):
            return result

        curr_value_lst1 = operand_list1[curr_index_lst1]
        curr_value_lst2 = operand_list2[curr_index_lst2]

        # check if current index position is a skip pointer
        skip_pointer_lst1 = get_skip_pointer(curr_value_lst1)
        skip_pointer_lst2 = get_skip_pointer(curr_value_lst2)

        # Add 1 or 0 to move the current pointer to real value
        curr_index_lst1 += 1 if skip_pointer_lst1 else 0
        curr_index_lst2 += 1 if skip_pointer_lst2 else 0
        curr_value_lst1 = operand_list1[curr_index_lst1]
        curr_value_lst2 = operand_list2[curr_index_lst2]

        if curr_value_lst1 == curr_value_lst2:
            # If it's in both list, then add to result and move to next index
            result.append(curr_value_lst1)
            curr_index_lst1 += 1
            curr_index_lst2 += 1

        elif curr_value_lst1 > curr_value_lst2:
            if skip_pointer_lst2:
                skip_value_2 = operand_list2[skip_pointer_lst2] if skip_pointer_lst2 == len(operand_list2) - 1 else operand_list2[skip_pointer_lst2 + 1]
                if skip_value_2 <= curr_value_lst1:
                    curr_index_lst2, skip_pointer_lst2 = skip_pointer_lst2 + 1, get_skip_pointer(operand_list2[skip_pointer_lst2])
                else:
                    curr_index_lst2 += 1
            else:
                curr_index_lst2 += 1

        elif curr_value_lst1 < curr_value_lst2:
            if skip_pointer_lst1:
                skip_value_1 = operand_list1[skip_pointer_lst1] if skip_pointer_lst1 == len(operand_list1) - 1 else operand_list1[skip_pointer_lst1 + 1]
                if skip_value_1 <= curr_value_lst2:
                    curr_index_lst1, skip_pointer_lst1 = skip_pointer_lst1 + 1, get_skip_pointer(operand_list1[skip_pointer_lst1])
                else:
                    curr_index_lst1 += 1
            else:
                curr_index_lst1 += 1

    return result


def Boolean_OR(operand_list1, operand_list2):
    result = []

    # Initialize both pointer
    curr_index_lst1 = curr_index_lst2 = 0
    skip_pointer_lst1 = skip_pointer_lst2 = 0
    while True:

        if curr_index_lst1 >= len(operand_list1):
            result.extend(value for value in operand_list2[curr_index_lst2:] if get_skip_pointer(value) == None)
            return result

        elif curr_index_lst2 >= len(operand_list2):
            result.extend(value for value in operand_list1[curr_index_lst1:] if get_skip_pointer(value) == None)
            return result

        curr_value_lst1 = operand_list1[curr_index_lst1]
        curr_value_lst2 = operand_list2[curr_index_lst2]

        # check if current index position is a skip pointer
        skip_pointer_lst1 = get_skip_pointer(curr_value_lst1)
        skip_pointer_lst2 = get_skip_pointer(curr_value_lst2)

        # Add 1 or 0 to move the current pointer to real value
        curr_index_lst1 += 1 if skip_pointer_lst1 else 0
        curr_index_lst2 += 1 if skip_pointer_lst2 else 0
        curr_value_lst1 = operand_list1[curr_index_lst1]
        curr_value_lst2 = operand_list2[curr_index_lst2]

        if curr_value_lst1 == curr_value_lst2:
            # If it's in both list, then add to result and move to next index
            result.append(curr_value_lst1)
            curr_index_lst1 += 1
            curr_index_lst2 += 1

        elif curr_value_lst1 > curr_value_lst2:
            result.append(curr_value_lst2)
            if skip_pointer_lst2:
                skip_value_2 = operand_list2[skip_pointer_lst2] if skip_pointer_lst2 == len(operand_list2) - 1 else operand_list2[skip_pointer_lst2 + 1]
                if skip_value_2 <= curr_value_lst1:
                    result += operand_list2[curr_index_lst2 + 1: skip_pointer_lst2]
                    curr_index_lst2, skip_pointer_lst2 = skip_pointer_lst2 + 1, get_skip_pointer(operand_list2[skip_pointer_lst2])
            curr_index_lst2 += 1

        elif curr_value_lst1 < curr_value_lst2:
            result.append(curr_value_lst1)

            # update curr_index_lst1, checking for skip pointer first
            curr_index_lst1 += 1
            if skip_pointer_lst1 is not None and operand_list1[skip_pointer_lst1] <= curr_value_lst2:
                result += operand_list1[curr_index_lst1:skip_pointer_lst1]
                curr_index_lst1 = skip_pointer_lst1 + 1
                skip_pointer_lst1 = get_skip_pointer(operand_list1[skip_pointer_lst1])

    return result


def eval_queries(queries, dictionary, total_list):
    operand_stack = []
    list = []
    for token in queries:

        # If token is an operand
        if token not in precedence:
            # Append the operand to stack
            operand_stack.append(token)
        # If token is an operator
        else:
            # Check for unary operator first
            if token == "NOT":
                operand1 = operand_stack.pop()

                if not isinstance(operand1, type(list)):
                    operand1 = dictionary[operand1]["doc_list"]

                operand_stack.append(Boolean_NOT(operand1, total_list))

            # Rest is binary operator
            else:
                operand1 = operand_stack.pop()
                operand2 = operand_stack.pop()

                if not isinstance(operand1, type(list)):
                    operand1 = dictionary[operand1]["doc_list"]

                if not isinstance(operand2, type(list)):
                    operand2 = dictionary[operand2]["doc_list"]

                if token == "AND":
                    operand_stack.append(Boolean_AND(operand1, operand2))
                elif token == "OR":
                    operand_stack.append(Boolean_OR(operand1, operand2))

    if len(operand_stack) > 1:
        print("Query is not correct, Please check queries.txt")
    else:
        operand1 = operand_stack.pop()

        if not isinstance(operand1, type(list)):
            operand1 = dictionary[operand1]["doc_list"]

        for value in operand1:
            if isinstance(value, int):
                operand_stack.append(value)

        return operand_stack


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement yogur code in below

    # Open the queries_file
    queries_file = open(queries_file, "rb")
    queries = [query.decode() for query in queries_file.read().splitlines()]
    queries_str = ''.join(queries)
    print("Processing query:", queries_str)

    # Open the doc_id file
    doc_ids = open("doc_ids.txt", "rb")
    total_list = pickle.load(doc_ids)

    # tokenize the input string using nltk
    tokens = nltk.word_tokenize(queries_str)

    # apply the Shunting Yard algorithm to convert to postfix notation
    postfix_queries = shunting_yard(tokens)

    operant = [x for x in postfix_queries if x not in precedence]

    used_dict = get_all_posting(operant, dict_file, postings_file)

    # Get result from boolean queries
    result = eval_queries(postfix_queries, used_dict, total_list)

    # Translate result to string and write
    result_string = ' '.join(str(i) for i in result)

    result_file = open(results_file, "w")
    result_file.write(result_string)
    # print("Result:", result_string)

    # Close all files
    queries_file.close()
    doc_ids.close()
    result_file.close()

# run_search("dictionary.txt", "postings.txt", "queries.txt", "output.txt")


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
