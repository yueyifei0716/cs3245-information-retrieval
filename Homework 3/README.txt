This is the README file for A0269377J-A0267871N's submission
Email(s): e1112349@u.nus.edu, e1100391@u.nus.edu

== Python Version ==

I'm (We're) using Python Version <3.8.10> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

The index.py consists of three main functions: "process_text", "compute_doc_length", and "build_index". 

The "process_text" function:
preprocesses the text by converting it to lowercase, tokenizing it into words and sentences, and stemming the words. It then calculates the frequency of each word in the text.

The "compute_doc_length" function: 
computes the document length using a log-frequency weighting scheme. It applies log-frequency weighting to each term frequency, computes the square of the log-frequency weighted term frequency, and sums the squares. It then takes the square root of the sum to get the document length.

The "build_index" function: 
constructs the index from the processed documents. It first reads the documents from the input directory and calls the "process_text" function to preprocess them. It then calls the "compute_doc_length" function to compute the document length for each document. It updates the index by iterating over the terms in each document and adding the document frequency (df) and the posting list to the ] index. Finally, it writes the index to two output files: a dictionary file and a postings file. The dictionary file contains the IDF and the pointer to the postings list for each term in the index. The postings file contains the posting lists for each term in the index.

The search.py consists of three main functions: "get_term_frequency", "compute_tf_idf_weight", "create_term_doc_dictionary" and "keyword_search". 

The "get_term_frequency" function: 
Takes a query list as input and returns a dictionary containing the frequency of each term in the document. 

The "compute_tf_idf_weight" function: 
Computes the tf-idf weight for each term in a document. It will takes the idf value from dictionary, and calculate it with 1 + base 10 log and then multiply by idf.

The "create_term_doc_dictionary" function: 
Creates a dictionary of terms and the documents in which they appear. it will find the address and load it from specific place by pickle load, then applying lenth normalization and add to the unique docID.

The "keyword_search" function: 
Takes a query string and a term-document dictionary as input and returns a list of documents that contain the query terms. It will add the weighted score to the total score and append with document ID to results, then sort it and return top n value, currently set to 10.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

dictionary.txt: a file that contains the inverted index dictionary with IDF and pointers to the postings list for each term in the index.

postings.txt: a file that contains the posting lists for each term in the index.

index.py: a file that implement the index construction.

search.py: a file that implement the search by VSM.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0269377J-A0267871N, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
