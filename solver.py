#!/usr/bin/env python3

"""
Name: Wordle Solver
Author: Kinille
Date: 2022-01-07 Friday

Interactively helps you solve wordle

As of right now, this is garbage spaghetti code used to test different methods,
the solver itself works right now, but over the weekend I'm going to refactor a clean looking program that
should also work a lot faster and be better at guessing.

"""
import re

from collections import Counter
from string import ascii_lowercase
import numpy as np
import copy
from loguru import logger

logger.remove()
best_start_word = "adieu"


with open('resources/five_letters.txt', 'r') as fd:
    POSSIBLE_WORDS = fd.read().splitlines()
correct_response = re.compile(r'[xgy]{5}')
letters_by_frequency = ['e', 'a', 'r', 'i', 'o', 't', 'n', 's', 'l', 'c', 'u', 'd', 'p',
                        'm', 'h', 'g', 'b', 'f', 'y', 'w', 'k', 'v', 'x', 'z', 'j', 'q']

def new_letters_by_frequency():
    for letter in letters_by_frequency:
        yield letter

def unknown_letter_maximizing_guess(yellow_set, black_set, possible_words, unique=5):
    nono_set = yellow_set | black_set
    return_word = None
    looking = ""
    get_letter = new_letters_by_frequency()
    # Get four letters
    while len(looking) < 4:
        l = next(get_letter)
        if l not in nono_set:
            looking += l
    while True:
        while True:
            try:
                l = next(get_letter)
            except StopIteration:
                return None
            if l not in nono_set:
                looking += l
                break
        com = re.compile(f'[{looking}]{{5}}')
        for word in possible_words:
            c = Counter(word)
            if len(c) >= unique:
                return word

def entropy_maximizing_guess(possible_words, required_chars, black_set, yellow_set, green_set):
    scores = []
    possible_guesses = possible_words
    #if len(possible_words) < 150:
    if True:
        logger.debug('Entering mode for all possible guess words')
        alph = set(ascii_lowercase)
        looking = "".join(list(alph - black_set))
        is_possible = re.compile(f'[{looking}]{{5}}')
        possible_guesses = [word for word in POSSIBLE_WORDS if is_possible.search(word)]
    for possible_guess_word in possible_guesses:
        word_counts = []
        for prior, actual_word in enumerate(possible_words):
            faux_required_chars = copy.copy(required_chars)
            faux_black_set = copy.copy(black_set)
            faux_yellow_set = copy.copy(yellow_set)
            faux_green_set = copy.copy(green_set)
            response = ""
            for index, char in enumerate(possible_guess_word):
                if actual_word[index] == char:
                    response += 'g'
                    continue
                elif char in actual_word:
                    response += 'y'
                    continue
                else:
                    response += 'x'
            for index, (letter, code) in enumerate(zip(possible_guess_word, response)):
                if code == "g":
                    faux_required_chars.add(letter)
                    pair = (letter, index)
                    if pair not in faux_green_set:
                        faux_green_set.add(pair)
                elif code == "y":
                    faux_required_chars.add(letter)
                    pair = (letter, index)
                    if pair not in faux_yellow_set:
                        faux_yellow_set.add(pair)
                else:
                    assert code == "x"
                    faux_black_set.add(letter)
            # Get all new possible words
            new_possible_words = []
            for word in possible_words:
                if not black_check_possible(faux_black_set, word):
                    continue
                if not required_check_possible(faux_required_chars, word):
                    continue
                if not yellow_check_possible(faux_yellow_set, word):
                    continue
                if not green_check_possible(faux_green_set, word):
                    continue
                new_possible_words.append(word)
            word_counts.append(len(new_possible_words) - 1 * int(possible_guess_word in possible_words))
        score = sum(word_counts) / len(word_counts)
        scores.append((score, possible_guess_word))
    scores.sort(key=lambda x: x[0])
    #if len(scores) < 10:
    #    new_scores = []
    #    adder = 2
    #    ite = 0
    #    for score in scores:
    #        val, word = score
    #        val += adder * ite
    #        ite += 1
    #        new_scores.append((val, word))
    #    scores = new_scores
    best = min(scores, key=lambda x: x[0])
    if len(scores) < 20:
        logger.info(scores)
    else:
        logger.info(len(scores))
        logger.info(scores[:10])
    if scores[0] == 1.0:
        best_list = [pair for pair in scores if pair[0] == 1.0]
        for pair in best_list:
            if pair[1] in possible_words:
                best = pair
                break
    logger.info(f'The guess {best[1]} has a score of {best[0]}')
    return best[1]


def black_check_possible(black_set, word):
    for char in word:
        if char in black_set:
            return False
    return True

def required_check_possible(required_set, word):
    for char in required_set:
        if char not in word:
            return False
    return True

def yellow_check_possible(yellow_set, word):
    for pair in yellow_set:
        char, index = pair
        if char == word[index]:
            return False
    return True

def green_check_possible(green_set, word):
    for pair in green_set:
        char, index = pair
        if char != word[index]:
            return False
    return True

def main():
    print("Welcome to Wordle solver 1.0!")
    print("Guess the given word and input the response as:")
    print("G - for Green")
    print("Y - for Yellow")
    print("X - for blacked out/ grey")
    print("example: ggyxx")
    print()
    possible_words = copy.deepcopy(POSSIBLE_WORDS)
    guess = best_start_word
    green_set = set() # Filled with tuples of format ('char', index_position) ie ('t', 2) for 'petal'
    yellow_set = set() ## Filled with tuples of format ('char', index_position) ie ('l', 2) for a guess of small on 'petal'
    required_chars = set()
    black_set = set()
    guess = best_start_word
    tries = 0
    while True:
        tries += 1
        print(f"Please try the word:  '{guess}'")
        try:
            response = str(input("What is the response?: ")).lower()
            assert correct_response.search(response)
            assert len(response) == 5
        except AssertionError as err:
            print("Response must be 5 characters containing only the characters 'GgYyXx'")
        if response == "ggggg":
            print(f"Congratulations! We got there in {tries} rounds!")
            break
        for index, (letter, code) in enumerate(zip(guess, response)):
            if code == "g":
                required_chars.add(letter)
                pair = (letter, index)
                if pair not in green_set:
                    green_set.add(pair)
            elif code == "y":
                required_chars.add(letter)
                pair = (letter, index)
                if pair not in yellow_set:
                    yellow_set.add(pair)
            else:
                assert code == "x"
                black_set.add(letter)
        # Get all new possible words
        new_possible_words = []
        for word in possible_words:
            debug = False
            if word == "smock":
                debug = True
            if not black_check_possible(black_set, word):
                continue
            if not required_check_possible(required_chars, word):
                continue
            if not yellow_check_possible(yellow_set, word):
                continue
            if not green_check_possible(green_set, word):
                continue
            new_possible_words.append(word)
        possible_words = new_possible_words
        logger.debug(f'{green_set=}')
        logger.debug(f'{yellow_set=}')
        logger.debug(f'{black_set=}')
        logger.debug(f'{possible_words=}')
        print()
        print(f'There are now {len(possible_words)} possible words left')
        print(f'The most likely is: {possible_words[0]}')
        print(f'Loading, please wait...')
        if len(possible_words) > 500:
            s = unknown_letter_maximizing_guess(yellow_set, black_set, possible_words)
            guess = s
            if guess == None:
                guess = possible_words[0]
        elif len(possible_words) == 1:
            print(f"The word must be: '{possible_words[0]}'")
            guess = possible_words[0]
        else:
            guess = entropy_maximizing_guess(possible_words, required_chars, black_set, yellow_set, green_set)
            if guess == "None":
                exit()



if __name__ == "__main__":
    main()
