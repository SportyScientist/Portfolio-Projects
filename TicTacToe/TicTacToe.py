# Author: Marlene Ganslmeier
# Date: 01.01.2022
#Tic Tac Toe 
#first implementation is two players against each other


import random
import time

#Games are much easier with a visual. We can represent the game board with some ASCII art.
#use the labelling to count moves!
board = ''' 1 | 2 | 3 \n --------- \n 4 | 5 | 6 \n --------- \n 7 | 8 | 9'''

#in code we will use a list of lists to represent a matrix

matrix = ["1", "2","3", "4", "5", "6", "7", "8", "9"]

class Player:
    def __init__(self, name):
        self.name = name
        self.sign = "O"

print("Thank you for playing Tic Tac Toe! \n")
name_a = input("What is the name of player 1? ")
name_b = input("\nWhat is the name of player 2? ")
time.sleep(0.5)

player_a = Player(name_a)
player_b = Player(name_b)


players_sorted = [player_a, player_b]

start = random.choice([0, 1])

player_random = []
player_random.append(players_sorted[start])
players_sorted.remove(players_sorted[start])
player_random.append(players_sorted[0])

player_one = player_random[0]
player_one.sign = "X"

player_two = player_random[1]

print("\n{name} starts!".format(name = player_one.name))
time.sleep(0.5)
print("\nThis is what your board looks like! \n\n" + 
        board + "\n\nTo reference a specific field, just type in the number!\n")
time.sleep(0.5)


winner_combinations = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

def check_win():
    win = False
       
    while win == False:
        for comb in winner_combinations:
            slice = [matrix[i] for i in comb]
            try:
                sumup = sum(slice)
                if sumup == 3 or sumup == 30:
                  win = True
                
            except:
                continue
        
        return win

def get_winner():
    for comb in winner_combinations:
        slice = [matrix[i] for i in comb]
        
        try:
            sumup = sum(slice)
            
        except:
            continue
        
        return sumup



winner = False

while not winner: 

    
    for move in range(1,10):

        field = ""
        winner = check_win()
        
        if winner == True:
            win_sum = get_winner()

            if win_sum == 3:
                winner_name = player_one.name
            else:
                winner_name = player_two.name
                           

            print("We have a winner! Congratulations {name}, you won this game!".format(name = winner_name))
            break
    
        if move % 2 != 0:

            while field not in matrix:
                field = input(player_one.name + " it's your turn. Where do you want to place your move? ")
                index = int(field) - 1            
                    
                if field not in matrix: 
                    print("This field has already been played. Try again!")

            matrix[index] = 1
            board = board.replace(str(field), player_one.sign)
        else:

            while field not in matrix:
                field = input(player_two.name + " it's your turn. Where do you want to place your move? ")
                index = int(field) - 1 
                
                if field not in matrix: 
                    print("This field has already been played. Try again!")


            matrix[index] = 10
            board = board.replace(str(field), player_two.sign)
        
      
                            
        print("\n" + board + "\n")  

     







