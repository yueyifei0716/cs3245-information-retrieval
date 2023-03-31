#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -i directory-of-documents -d dictionary-file -p postings-file"
    )


def write_block_to_disk(block, block_num):
    """
    This function writes a block of terms and postings to disk as a binary file using pickle.

    Args:
        block (dict): a dictionary containing terms as keys and postings as values.
        block_num (int): the number of the block to write.

    Returns:
        None
    """
    # Create a path to the block file
    path = os.path.join(os.path.dirname(__file__), "disk_dir", f"block_{block_num}")
    # Open the file in binary mode and write the terms and postings to it using pickle
    with open(path, "wb") as f:
        for term, postings in sorted(block.items()):
            pickle.dump([term, sorted(postings)], f)


def write_to_disk(chunk, out_dict, out_postings):
    """
    Writes a chunk of postings to disk, updating the dictionary and posting file.

    Args:
    chunk (list): A list of posting dictionaries, where each dictionary has the keys "term", "doc_freq",
                           and "posting_list".
    out_dict (str): The filename for the output dictionary file.
    out_postings (str): The filename for the output postings file.

    Returns:
    None
    """

    # Open the output dictionary and postings files in binary mode for reading and writing.
    with open(os.path.join(os.path.dirname(__file__), out_dict), "r+b") as f_dict, \
         open(os.path.join(os.path.dirname(__file__), out_postings), "r+b") as f_postings:

        # Load the existing dictionary if it exists, or create a new empty one.
        dictionary = {}
        if os.stat(os.path.join(os.path.dirname(__file__), out_dict)).st_size != 0:
            dictionary = pickle.load(f_dict)

        # Write each posting to the postings file and update the dictionary with its location.
        for term_postings in chunk:
            # Get the current position in the postings file, which will be the starting position for the next posting.
            pointer = f_postings.seek(0, 2)
            # Update the dictionary with the posting's term, document frequency, and pointer to its location in the file.
            dictionary[term_postings["term"]] = {"doc_freq": term_postings["doc_freq"], "pointer": pointer}
            # Write the posting's posting list to the end of the postings file.
            pickle.dump(term_postings["posting_list"], f_postings)

        # Reset the position of the dictionary file to the beginning and truncate it.
        # Then write the updated dictionary to the beginning of the dictionary file.
        f_dict.seek(0, 0)
        f_dict.truncate()
        pickle.dump(dictionary, f_dict)


def generate_blocks(in_dir, BLOCK_SIZE):
    """
    Generate intermediate block files from documents in a directory.

    Args:
        in_dir (str): Path to the directory containing input documents.
        BLOCK_SIZE (int): Maximum size of a block in bytes.

    Returns:
        int: The number of intermediate block files generated.

    """

    # Initialize variables
    size_used = 0             # running counter of memory usage
    block = {}                # dictionary of term to posting list for each block
    block_num = 1             # block number for intermediate block files

    # Initialize the Porter stemmer from NLTK
    ps = nltk.stem.PorterStemmer()

    # Create index for each documents
    doc_ids = sorted([int(doc_id) for doc_id in os.listdir(in_dir)])

    # Save document IDs to file
    with open(os.path.join(os.path.dirname(__file__), "doc_ids.txt"), "wb") as f_doc_ids:
        pickle.dump(doc_ids, f_doc_ids)

    # Process each document in the input directory
    for docID in doc_ids:
        f = open(os.path.join(in_dir, str(docID)), "r")
        text = f.read().lower()
        sentences = nltk.sent_tokenize(text)

        # Process each sentence in the document
        for sentence in sentences:
            terms_stemmed = [ps.stem(w) for w in nltk.word_tokenize(sentence)]
            for term in terms_stemmed:
                # Add new term to block if it is not already in the block
                if term not in block:
                    term_posting_size = sys.getsizeof(term) + sys.getsizeof(docID)
                    if term_posting_size + size_used > BLOCK_SIZE:
                        # Write block to disk if it has reached BLOCK_SIZE
                        write_block_to_disk(block, block_num)
                        block_num += 1
                        size_used = 0
                        block = {}

                    # Add the new term and its posting list to the block
                    block[term] = [docID]
                    size_used += term_posting_size
                # Update posting list if term is already in the block
                else:
                    if docID not in block[term]:
                        docID_size = sys.getsizeof(docID)
                        if docID_size + size_used > BLOCK_SIZE:
                            # Write block to disk if it has reached BLOCK_SIZE
                            write_block_to_disk(block, block_num)
                            block_num += 1
                            size_used = 0
                            block = {}
                            block[term] = [docID]
                            size_used += sys.getsizeof(term) + docID_size
                        else:
                            # Append the document ID to the posting list for the term
                            block[term].append(docID)
                            size_used += docID_size
        f.close()

    # Write out the last block in memory to disk and clear memory
    write_block_to_disk(block, block_num)
    size_used = 0
    block = {}

    return block_num


def read_chunk(block_ID, disk_files, chunk_size, chunks):
    chunk_size_read = 0
    chunk_read = []
    while chunk_size_read < chunk_size:
        try:
            # Load a serialized object from the disk file associated with the given block ID
            data_object = pickle.load(disk_files[block_ID])
            # Add the deserialized object to the list of objects read so far
            chunk_read.append(data_object)
            # Update the total size of the objects read so far
            chunk_size_read += sys.getsizeof(data_object)
        except:
            # If there are no more objects to read, break out of the loop
            break
    # Add the list of objects read to the dictionary of chunks
    chunks[block_ID] = chunk_read
    # Return True if any objects were read, False otherwise
    return len(chunk_read) > 0


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("indexing...")
    # Create a path to the disk directory
    dir_path = os.path.join(os.path.dirname(__file__), "disk_dir")
    # Create the directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)
    # Loop through all files in the directory and delete them
    for file_name in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file_name))
    # Create empty files for the dictionary and postings
    with open(out_dict, "w"), open(out_postings, "w"):
        pass

    # Define the block size for processing
    BLOCK_SIZE = 1000000
    # Compute the total number of blocks in the input directory
    total_blocks = generate_blocks(in_dir, BLOCK_SIZE)
    # Compute the chunk size, which is the maximum size of the output chunk that can fit in memory
    chunk_size = BLOCK_SIZE // (total_blocks + 1)
    # Get a list of all the disk files in the disk directory
    disk_file_names = os.listdir(os.path.join(os.path.dirname(__file__), "disk_dir"))
    # Open all the disk files for reading
    disk_files = [open(os.path.join(os.path.dirname(__file__), "disk_dir", disk_file), "rb") for disk_file in disk_file_names]
    # Create an empty list of chunks, with one chunk for each disk file
    chunks = [[] for _ in range(len(disk_file_names))]

    print(chunks)

    # Loop over all block IDs in the range [0, len(disk_file_names))
    for block_ID in range(len(disk_file_names)):
        # Read a chunk of data from the disk file associated with the current block ID
        print(block_ID)
        read_chunk(block_ID, disk_files, chunk_size, chunks)

    # Initialize an empty list to hold the current chunk of merged data
    current_chunk = []
    # Initialize a variable to keep track of the total memory used by the current chunk
    current_chunk_memory_used = 0

    # Initialize variables to keep track of the current term being merged, the temporary chunk of postings lists,
    # and the document frequency of the current term
    term_to_merge = ""
    temp_chunk = []
    temp_posting_list = []
    doc_freq = 0

    while True:
        # Iterate through each chunk and check if it contains the lowest alphabetical term
        for chunkID, chunk in enumerate(chunks):
            if not chunk:
                if not read_chunk(block_ID, disk_files, chunk_size, chunks):
                    continue
            else:
                # If the chunk is not empty, check if its first term matches the current term to merge
                if not term_to_merge:
                    term_to_merge = chunk[0][0]
                    temp_chunk.append(chunkID)
                else:
                    if chunk[0][0] == term_to_merge:
                        temp_chunk.append(chunkID)
                    if chunk[0][0] < term_to_merge:
                        term_to_merge = chunk[0][0]
                        temp_chunk = [chunkID]
                    else:
                        pass

         # If the term being merged is empty, break the loop
        if term_to_merge == "":
            break

        # Iterate over the list of chunk ids to merge
        for chunkID in temp_chunk:
            # Pop the first posting list from the corresponding chunk and append it to the `temp_posting_list`
            temp_posting_list += chunks[chunkID].pop(0)[1]

        # Remove duplicates from `temp_posting_list` by converting it to a set, then sort it
        temp_posting_list = list(set(temp_posting_list))
        temp_posting_list.sort()

        # Set the length of the resulting list as the document frequency (`doc_freq`) of the merged term
        doc_freq = len(temp_posting_list)

        # Add skip pointers to the merged postings list
        n = int(len(temp_posting_list) ** 0.5)
        interval = len(temp_posting_list) // n
        for i in range(n):
            target = 1 + i * interval
            if target >= len(temp_posting_list):
                target = len(temp_posting_list)
            temp_posting_list.insert(i*interval, f'^{target}')

        # Compute the memory used by the merged term and postings list, and check if it exceeds the memory threshold
        merged_term_memory = sys.getsizeof(len(temp_posting_list)) + sys.getsizeof(term_to_merge) + sys.getsizeof(temp_posting_list[0]) * len(temp_posting_list)
        chunk_memory_threshold = chunk_size - current_chunk_memory_used
        if merged_term_memory > chunk_memory_threshold:
            # print(current_chunk)
            write_to_disk(current_chunk, out_dict, out_postings)
            current_chunk = []
            current_chunk_memory_used = 0

        # Add the merged term and postings list to the current chunk
        current_chunk.append({"term": term_to_merge, "doc_freq": doc_freq, "posting_list": temp_posting_list})
        current_chunk_memory_used += merged_term_memory
        write_to_disk(current_chunk, out_dict, out_postings)
        # print(current_chunk)

        # Reset variables for the next iteration
        term_to_merge = ""
        temp_chunk = []
        temp_posting_list = []
        doc_freq = 0

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], "i:d:p:")
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-i":  # input directory
        input_directory = a
    elif o == "-d":  # dictionary file
        output_file_dictionary = a
    elif o == "-p":  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if (
    input_directory == None
    or output_file_postings == None
    or output_file_dictionary == None
):
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
