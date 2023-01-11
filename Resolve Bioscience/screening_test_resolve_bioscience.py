# screening test resolve bioscience

#Author: Marlene Ganslmeier

import random #technically a library but I feel it's too much to ask to write your own randomness algorithm
#it also comes with the standard installation so I think it count's as acceptable 
import csv #same applies

#the hamming distance defines in how many positions strings of the same length differ
def hamming_distance(str1, str2):
    distance = 0
    for i in range(len(str1)):
        if str1[i] != str2[i]:
            distance += 1
    return distance


#get all possible combinations with 4 letters in 6 positions (4**4)
def get_combinations():
    combinations = []
    bases = ["A", "T", "G", "C"]
    for i in bases:
        for j in bases:
            for k in bases:
                for l in bases:
                    for m in bases:
                        for n in bases:
                            combinations.append(i + j + k + l + m + n)
    return combinations


def check(list_size):
    words = []
    count = 0
    combinations = get_combinations()

    while len(words) < list_size:
        
        i = random.randrange(len(combinations)) # get random index
        #we need to get a random index because just iterating through the list in order results in a subset of 64 members 

        combinations[i], combinations[-1] = combinations[-1], combinations[i]    # swap with the last element
        seq = combinations.pop() #pop last element to remove the tested value  --> this is the most time efficient way to remove this value from the list      
           
        count += 1
        dist = []
        
        if len(words) == 0: #if list is empty add first entry
            words.append(seq)
            
        else:
            for word in words:
                x = hamming_distance(seq, word)
                
                if x <3: #if we found one match that has a score of less than 3 (which means at lest 4 positions are the same) we can abort iterating through the entire list 
                    
                    break
                dist.append(x)
            
            if len(dist) == len(words):#if the list of distances is the same length as words, the for loop didn't abort so no member has a hamming distance of less than 3
                words.append(seq)
    
    return words

while True:
    try:
        test = check(96)
        out = csv.writer(open("words.txt","w"), delimiter='\n')
        out.writerow(test)
        print("Your list has been safed as words.txt")
    except ValueError:
        continue
    else:
        break




