# Wordle Solver

Currently this project is very much a work in progress. As a weekend project I started messing around with a few different strategies to try to solve wordle in as few guesses as possible

The wordlist in resources/five_letters.txt was retrieved by first getting the 1/3 million most common words frequency list located [here.](https://norvig.com/ngrams/count_1w.txt)
Then I grepped that down to only five letter words. Finally, I ran each word through a /usr/bin/dict using the english dictionary (-d english) and if the word wasn't there, it was removed. Mostly, that took away a lot of plural words  e.g. trees, words, plays, etc.

I currently plan to refactor the code to clean it up and provide a nice curses environment over the weekend (2021-01-07)
