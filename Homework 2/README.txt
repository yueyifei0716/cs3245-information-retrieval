This is the README file for A0269477J-A0267871N's submission
Email(s): e1112349@u.nus.edu, e1100391@u.nus.edu

== Python Version ==

I'm (We're) using Python Version <3.10.9> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps
in your program, and discuss your experiments in general.  A few paragraphs
are usually sufficient.

In the index.py. The build_index function takes three parameters: in_dir, which
is the input directory containing the documents to be indexed, out_dict, which
is the output dictionary file, and out_postings, which is the output postings file.

The function starts by creating a directory called disk_dir if it doesn't already exist,
and deleting all files in that directory. It also creates empty dictionary and postings
files with the names specified by out_dict and out_postings.

Then we compute the block size and total number of blocks in the input directory, and the
chunk size, which is the maximum size of the output chunk that can fit in memory. It also
opens all the disk files in the disk directory for reading.

Next, we loop over all block IDs, reads a chunk of data from the disk file associated with
the current block ID, and appends it to the corresponding list in the chunks list.

We then enters a loop where it merges the smallest terms from each chunk in the chunks list.
It does this by iterating through each chunk and checking if it contains the lowest alphabetical
term. If a chunk contains the lowest term, the function pops the first posting list from that chunk
and appends it to a temporary list. The function then removes duplicates from the temporary list
and computes the document frequency of the merged term.

We then adds skip pointers to the merged postings list, and computes the memory used by the merged term
and postings list. If the memory used exceeds the memory threshold, the function writes the current chunk
to disk and creates a new empty chunk. If the memory used does not exceed the threshold, the function adds
the merged term and postings list to the current chunk.

We continue to run this loop until all terms have been merged. Finally, we write the last
chunk to disk and closes all the disk files.


In the search.py, the most important algorithm is shunting_yard, it can transform
a infix boolean equation to postfix boolean equation, It not onlt solve the bracket
problem, but also making later's evaluating boolean expression much easier. Also,
the three boolean operator function is also important, it include the algorithm of
skip pointers, we decide to use a list to store all values, integer for file name and
with ^ and square root size to make a string for skip pointer. By taking ^ out it can
point to the next index.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

dictionary.txt contains a list of unique terms (or words) extracted from the documents in the collection,
    along with the document frequency and pointers to the locations of the terms in postings.txt
postings.txt - contain the actual postings (i.e., occurrences) of each term in the documents of the collection
index.py - apply SPIMI algorithm to build index and return dictionary.txt, postings.txt and doc_ids for search.py
search.py - require a queries.txt and two txt mentioned above and the result store in result.txt

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0269477J-A0267871N, certify that I/we have followed the CS 3245 Information
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

Single-pass in-memory indexing: https://nlp.stanford.edu/IR-book/html/htmledition/single-pass-in-memory-indexing-1.html#:~:text=SPIMI%20uses%20terms%20instead%20of,is%20enough%20disk%20space%20available.&text=The%20SPIMI%20algorithm%20is%20shown%20in%20Figure%204.4%20.
Shunting yard algorithm: https://en.wikipedia.org/wiki/Shunting-yard_algorithm