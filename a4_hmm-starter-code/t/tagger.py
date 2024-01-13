# The tagger.py starter code for CSC384 A4.
# Currently reads in the names of the training files, test file and output file,
# and calls the tagger (which you need to implement)
import os
import sys
import time

# Key for sum of entries
SUM = 0
# Minimum Probability for start, emission and transition
MINIMUM_PROB = 0.0001

# CPTs for start, emission and transition probabilities
start_table = {SUM : 0}
transition_table = {}
emission_table = {}


def normalize(arr):
    """ Normalize an array of probabilities to have a sum of 1 """

    arr_sum = sum(arr)
    for i in range(len(arr)):
        arr[i] /= arr_sum


def add_start_entry(start_tag):
    """ Given a starting tag, add this as an entry to the start table """

    if start_tag not in start_table:
        start_table[start_tag] = 0
    start_table[start_tag] += 1
    start_table[SUM] += 1


def add_transition_entry(prev_tag, tag):
    """ Given two consecutive tags, add this pair as an transition entry 
    to the transition_table """

    if prev_tag not in transition_table:
        transition_table[prev_tag] = {SUM : 0}
    if tag not in transition_table[prev_tag]:
        transition_table[prev_tag][tag] = 0

    transition_table[prev_tag][SUM] += 1
    transition_table[prev_tag][tag] += 1

    if tag not in transition_table:
        transition_table[tag] = {SUM : 0}


def add_emission_entry(word, tag):
    """ Given a word and its tag, add this pair as an emission entry 
    to the transition_table """

    if word not in emission_table:
        emission_table[word] = {SUM : 0}
    if tag not in emission_table[word]:
        emission_table[word][tag] = 0

    emission_table[word][SUM] += 1
    emission_table[word][tag] += 1


def train(training_list):
    """ Train a list of files, populate the start, transition and emission table """

    for train_file in training_list:
        f = open(train_file, "r")

        # Handle first line
        first_line = f.readline()
        word, tag = first_line.strip().split(" : ")

        # Add start and emission entry to the CPTs
        add_start_entry(tag)
        add_emission_entry(word, tag)
        prev_tag = tag

        # Hanlde the rest of the lines
        end_of_sentence = False
        for l in f:
            word, tag = l.strip().split(" : ")
            if end_of_sentence:
                add_start_entry(tag)
                end_of_sentence = False
                add_emission_entry(word, tag)
            else:
                add_emission_entry(word, tag)
                add_transition_entry(prev_tag, tag)
            if word == ".":
                end_of_sentence = True
            prev_tag = tag
        f.close()


def test(test_file, output_file):
    """With the start, transition and emission table from the training data,
    assigned a test of file of words with tags """

    test = open(test_file, "r")
    output = open(output_file, "w")

    words_index_dict = {}
    all_tags = list(transition_table.keys())
    all_words = list(emission_table.keys()) 

    num_lines = sum([1 for _ in test])
    num_tags = len(all_tags)
    num_words = len(all_words)

    # Probability for time t, only needs to record probability of the latest time
    prob_trellis = [ 0.0 for i in range(num_tags) ]
    # Path for all time t, each cell indicates the index of the prev tag selected
    path_trellis = [ [ -1 for i in range(num_tags) ] for j in range(num_lines)]

    transition_matrix = [ [ MINIMUM_PROB for i in range(num_tags) ] for j in range(num_tags) ]
    emission_matrix = [ [ MINIMUM_PROB for i in range(num_tags) ] for j in range(num_words) ]

    # Construct transition_matrix
    for i in range(num_tags):
        tag = all_tags[i]

        for j in range(num_tags):
            prev_tag = all_tags[j]
            
            if prev_tag in transition_table and tag in transition_table[prev_tag]:
                transition_matrix[i][j] = transition_table[prev_tag][tag] / transition_table[prev_tag][SUM]
    
    # Construct emission_matrix
    for i in range(num_words):
        word = all_words[i]
        words_index_dict[word] = i

        if word not in emission_table:
            continue

        for j in range(num_tags):
            tag = all_tags[j]

            if tag in emission_table[word]:
                emission_matrix[i][j] = emission_table[word][tag] / emission_table[word][SUM]

    # Represent time t
    t = 0

    # handle first word
    test.seek(0, 0)
    line = test.readline()
    word = line.strip()

    word_index = words_index_dict[word] if word in words_index_dict else -1

    # Loop over all tags and assign probabilities to each of them
    for i in range(num_tags):
        tag = all_tags[i]

        # Calculate start probability and emission probability,
        # i.e. given this tag, what is the probability of observing this word
        start_prob = MINIMUM_PROB
        if tag in start_table:
            start_prob = start_table[tag] / start_table[SUM]

        emission_prob = emission_matrix[word_index][i] if word_index >= 0 else MINIMUM_PROB

        prob_trellis[i] = start_prob * emission_prob
        
    normalize(prob_trellis)

    # Loop over the remaing words in the file
    for line in test:
        t += 1
        word = line.strip()
        word_index = words_index_dict[word] if word in words_index_dict else -1

        # This list records the probabilities of tages for the current timestamp
        curr_prob_trellis = [ 0.0 for j in range(num_tags) ]

        # Loop over all tags to compute their probabilities for the given word
        for i in range(num_tags):

            # Look up emission probablity 
            emission_prob = emission_matrix[word_index][i] if word_index >= 0 else MINIMUM_PROB
        
            max_prob = -1
            max_prob_index = None

            # j is index for prev tags
            for j in range(num_tags):

                # Compute transition probability from the previous tag to the current tag
                transition_prob = transition_matrix[i][j]
                # As well as the probability of the previous tag
                prev_prob = prob_trellis[j]

                total_prob = prev_prob * transition_prob

                if total_prob > max_prob:
                    max_prob_index = j
                    max_prob = total_prob

            # Assign the trellis table with the tag of highest probability
            curr_prob_trellis[i] = max_prob * emission_prob
            path_trellis[t][i] = max_prob_index
        
        # Reassign the probability for time t as the current list
        prob_trellis = curr_prob_trellis
        normalize(prob_trellis)

    # Find the position with the highest probability by the final timestamp 
    max_index = None
    max_prob = -1
    for i in range(num_tags):
        prob = prob_trellis[i]
        if prob > max_prob:
            max_index = i
            max_prob = prob

    best_path = []

    # Trace the best path frame by frame
    # Each time we append max_index to the path and use 
    # the max index to get the index of the previous tag
    while t != 0:
        best_path.append(max_index)
        max_index = path_trellis[t][max_index]
        t -= 1
    
    best_path.append(max_index)
    best_path.reverse()

    # Write to the output file with the best path, i.e. the sequence of tags 
    # that produce the overall highest probability
    test.seek(0, 0)
    for index in best_path:
        word = test.readline().strip()
        line = "{} : {}\n".format(word, all_tags[index])
        output.write(line)
    
    test.close()
    output.close()


def tag(training_list, test_file, output_file):
    # Tag the words from the untagged input file and write them into the output file.
    # Doesn't do much else beyond that yet.
    print("Tagging the file.")

    train(training_list)

    test(test_file, output_file)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training files> -t <test file> -o <output file>"
    parameters = sys.argv
    training_list = parameters[parameters.index("-d")+1:parameters.index("-t")]
    test_file = parameters[parameters.index("-t")+1]
    output_file = parameters[parameters.index("-o")+1]
    # print("Training files: " + str(training_list))
    # print("Test file: " + test_file)
    # print("Ouptut file: " + output_file)

    # Start the training and tagging operation.
    tag (training_list, test_file, output_file)
