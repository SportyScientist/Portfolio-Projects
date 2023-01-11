# screening test resolve bioscience

#Author: Marlene Ganslmeier

import random #technically a library but I feel it's too much to ask to write your own randomness algorithm
#it also comes with the standard installation so I think it count's as acceptable 
import csv #same applies
import numpy
#function to create a random string comprised of the 4 bases 
def create_seq():
    bases = ["A", "T", "G", "C"]
    seq = []
    seq = [random.choice(bases) for x in range(6)]
    seq = "".join(seq)
    return seq

def hamming_distance(str1, str2):
    distance = 0
    for i in range(len(str1)):
        if str1[i] != str2[i]:
            distance += 1
    return distance

def check(list_size):
    words = []
    tested = []
    count = 0
    repeats = 0

    while len(words) < list_size:
        seq = create_seq()
        
        
        if seq in tested:
            repeats += 1
        
        else:
            tested.append(seq)
            count += 1
            dist = []
            
            if len(words) == 0:
                words.append(seq)
            else:
                for word in words:
                    x = hamming_distance(seq, word)
                    print(word, x)
                    if x <3:
                        #print("abort loop")
                        break
                    dist.append(x)
                #print(dist)

                if len(dist) == len(words): #add this to other for loop later
                    words.append(seq)
        
         
    
    # print("tested ", tested)
    # print("lenghts", len(tested))
    # print("unique", numpy.unique(tested))
    # print("unique length", len(numpy.unique(tested)))
    # print("count ", count)
    # print("repeats", repeats)
    return words
            
test = check(50)
test_words = ["".join(x) for x in test]
print(test_words)
print("lenghts", len(test_words))

out = csv.writer(open("words.txt","w"), delimiter='\n')
out.writerow(test_words)

