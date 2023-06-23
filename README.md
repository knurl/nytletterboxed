# nytletterboxed
Solves the Letter Boxed puzzle from the New York Times.

usage: nytletterboxed.py [-h] [-l LETTERS] word_list

Find NYT LetterBoxed solutions. Valid solutions are two words, wherein the
second word begins with the last letter of the first.

positional arguments:
  word_list             Path to your English dictionary. Needs to be a
                        plaintext list of words, separated by newlines.
                        Doesn't have to be sorted.

options:
  -h, --help            show this help message and exit
  -l LETTERS, --letters LETTERS
                        The allowed letters, in clockwise order, e.g.:
                        tnlihawrudof. If you don't specify this option, a
                        randomset of letters will be selected.
