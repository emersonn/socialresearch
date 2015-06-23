from colorama import Fore

from ..database import db_session

import models

# TODO: Move this to a settings file and make it more editable in the models?
CLASSIFICATIONS = ['sentiment', 'personal', 'convo', 'know']

def classify(classification):
    # response = db_session.execute('SELECT * FROM tweet WHERE ' + classification + '_classify is NULL')
    current = classification + "_classify"
    # TODO: fix this so it paginates, easy fix
    response = db_session.query(models.Tweet).filter_by(**{current: None}).limit(100)

    for row in response:
        print(Fore.BLUE + "The tweet: " + Fore.RESET + row.text.decode('unicode-escape'))
        print("You are classifying the " + Fore.RED + classification + Fore.RESET + ".")
        user = raw_input("Classification? (pos = 1, neg = 2, no = 3) (exit to exit) ")

        if user == "exit":
            from sys import exit
            exit()

        if (user != "1" and user != "2" and user != "3"):
            print("Was not pos or negative, going to next...")
            continue

        if user == "1":
            user = "pos"
        elif user == "2":
            user = "neg"
        elif user == "3":
            user = "no"

        setattr(row, current, user)

        db_session.commit()

        print("Classified as " + Fore.RED + user + Fore.RESET + ".")



if __name__ == "__main__":
    classification = raw_input("What type are we classifying? (" + ", ".join(CLASSIFICATIONS) + ") ")

    classify(classification)
