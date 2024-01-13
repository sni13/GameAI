# The tagger.py starter code for CSC384 A4.
# Currently reads in the names of the training files, test file and output file,
# and calls the tagger (which you need to implement)
import os
import sys

SUM = "sum"

initial_entries = {SUM: 0}
transition_entries = {}
emission_entries = {}

def normalize(probs):
    """ Normalize an array of probabilities to have a sum of 1 """
    my_sum = sum(probs)
    for i in range(len(probs)):
        probs[i] /= my_sum


def add_initial_tag(initial_tag):
    """Add initial tags """
    if initial_tag not in initial_entries:
        initial_entries[initial_tag] = 0
    initial_entries[initial_tag] += 1
    initial_entries[SUM] += 1

def add_emission_pair(word, tag):
    """Add emission word-tag pairs """
    if word not in emission_entries:
        emission_entries[word] = {SUM: 0}
    if tag not in emission_entries[word]:
        emission_entries[word][tag] = 0
    emission_entries[word][SUM] += 1
    emission_entries[word][tag] += 1 
    
def add_transition_pair(prev_tag, curr_tag):
    """Add transition pairs for prev_tag-curr_tag"""
    if prev_tag not in transition_entries:
        transition_entries[prev_tag] = {SUM: 0}
    if curr_tag not in transition_entries[prev_tag]:
        transition_entries[prev_tag][curr_tag] = 0
    transition_entries[prev_tag][curr_tag] += 1
    transition_entries[prev_tag][SUM] += 1

def train(training_list):
    """Based on training files, extract transition, emission, and initial entries"""
    initial_entries[SUM] = 0
    for train_file in training_list:
        f = open(train_file, "r")
        # read initial line
        l = f.readline().strip()
        word, tag = l.split(" : ")
        add_initial_tag(tag)
        add_emission_pair(word, tag)
        prev = tag
        # read rest of the lines, add each emission and transition pairs
        end_of_sentence = False
        for l in f:
            word, tag = l.strip().split(" : ")
            if end_of_sentence:
                add_initial_tag(tag)
                end_of_sentence = False
                add_emission_pair(word, tag)
            else:
                add_emission_pair(word, tag)
                add_transition_pair(prev, tag)
            if word == '.':
                end_of_sentence = True
            prev = tag
        f.close()

def get_transition_matrix(tags):
    """Get transition matrix converted from transition_entries"""
    transition_matrix = []
    # init transition matrix
    for i in range(len(tags)):
        tmp = []
        for j in range(len(tags)):
            tmp.append(0.00001)
        transition_matrix.append(tmp)
    # calculate probabilities into matrix
    for i in range(len(tags)):
        curr = tags[i]
        for j in range(len(tags)):
            prev = tags[j]
            if prev in transition_entries and curr in transition_entries[prev]:
                times = transition_entries[prev][curr] + 1
                total = transition_entries[prev][SUM]
                transition_matrix[i][j] = times/total
    return transition_matrix

def get_emission_matrix(words, tags):
    """Get emission matrix from emission_entries"""
    emission_matrix = []
    # init emission matrix
    for i in range(len(words)):
        tmp = []
        for j in range(len(tags)):
            tmp.append(0.00001) 
        emission_matrix.append(tmp)
    # calculate probabilities into matrix
    for i in range(len(words)):
        word = words[i]
        if word not in emission_entries:
            continue
        for j in range(len(tags)):
            tag = tags[j]
            if tag in emission_entries[word]:
                emission_matrix[i][j] = (emission_entries[word][tag] + 1)/ emission_entries[word][SUM]
    return emission_matrix

def get_init_prob(init_tag):
    """Get initial probabilities from initial_entries"""
    if init_tag in initial_entries:
        return initial_entries[init_tag]/initial_entries[SUM]
    else:
        return 0.00001

def test(test_file, output_file):
    """test the test_file by running viterbi algo, write to output file"""
    # read files
    test_f = open(test_file, "r")
    output_f = open(output_file, "w")

    # init_tags, tags, and words
    tags = list(transition_entries.keys())
    words = list(emission_entries.keys())

    # probability matrices
    transition_matrix = get_transition_matrix(tags)
    emission_matrix = get_emission_matrix(words, tags)

    # store word to its index in emission matrix
    words_to_index = {}
    for i in range(len(words)):
        word = words[i]
        words_to_index[word] = i

    # sequence of observations
    emissions = test_f.readlines()

    # store probs of all tags for each emission in test, at time t
    prob_t = [0.00001 for _ in range(len(tags))]
    # store prev_tag of all tags for each emission in test 
    prev = [[-1 for _ in range(len(tags))] for _ in range(len(emissions))]

    # determine values for time step 0
    t = 0
    word = emissions[t].strip()
    word_idx = words_to_index[word] if word in words_to_index else -1
    for i in range(len(tags)):  #calculate prob of all possible hidden states
        tag = tags[i]
        emission_prob = emission_matrix[word_idx][i]
        prob_t[i] = get_init_prob(tag) * emission_prob
        prev[0][i] = None
    normalize(prob_t)
    
    # determine values for time 1 to length(emissions)-1
    for t in range(1, len(emissions)):
        word = emissions[t].strip()
        word_idx = words_to_index[word] if word in words_to_index else -1
        curr_prob_t = [ 0.00001 for j in range(len(tags)) ]
        # loop over all current tags 
        for i in range(len(tags)):
            emission_prob = emission_matrix[word_idx][i]
            # find the max prev x
            max_prob = -1
            max_prob_idx = None
            # loop over all prev tags
            for j in range(len(tags)):
                transition_prob = transition_matrix[i][j]
                prev_prob = prob_t[j]
                total_prob = prev_prob * transition_prob * emission_prob
                if total_prob > max_prob:
                    max_prob, max_prob_idx = total_prob, j
            curr_prob_t[i] = max_prob
            prev[t][i] = max_prob_idx
        prob_t = curr_prob_t
        normalize(prob_t)

    # after scanning all words and calculating prob values
    # determine final position  
    max_idx = None
    max_prob = -1
    for i in range(len(tags)):
        prob = prob_t[i]
        if prob > max_prob:
            max_idx = i
            max_prob = prob
    # track most likely path by tracing backward
    most_likely_path = []
    while t > 0:
        most_likely_path.append(max_idx)
        max_idx = prev[t][max_idx]
        t -= 1
    most_likely_path.append(max_idx)
    most_likely_path.reverse()

    # write to output file
    test_f.seek(0, 0)
    for max_idx in most_likely_path:
        word = test_f.readline().strip()
        line = "{} : {}\n".format(word, tags[max_idx])
        output_f.write(line)

    test_f.close()
    output_f.close()



def tag(training_list, test_file, output_file):
    # Tag the words from the untagged input file and write them into the output file.
    # Doesn't do much else beyond that yet.
    print("Tagging the file.")
    #
    # YOUR IMPLEMENTATION GOES HERE
    #
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
    # print("Output file: " + output_file)

    # Start the training and tagging operation.
    tag (training_list, test_file, output_file)

    # training_list = ['data/training1.txt']
    # train(training_list)
    # print(initial_entries)
    # print(transition_entries)
    # print(emission_entries)
