import random

number = random.randint(1,100)
guess = int(input("Guess the number : "))
attempt = 1
while(True):
    if(guess>number):
        guess = int(input("Guess another number. This one  is too big: "))
        attempt += 1
    elif(guess<number):
        guess = int(input("Guess another number. This one is too small"))
        attempt += 1
    else:
        print(f" you have guessed it right. You have take { attempt } to guess it right")
        break 
