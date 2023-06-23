#!/usr/bin/env python

import os, sys, pdb, argparse, re, string
from random import sample
from functools import reduce

def process_word(sides, word):
    all_letters = sides[0]|sides[1]|sides[2]|sides[3]
    wl = len(word)
    next_sides_graph = {None: [sides[0], sides[1], sides[2], sides[3]],
                        sides[0]: [sides[1], sides[2], sides[3]],
                        sides[1]: [sides[0], sides[2], sides[3]],
                        sides[2]: [sides[0], sides[1], sides[3]],
                        sides[3]: [sides[0], sides[1], sides[2]]}

    current = None
    word_ok = True
    word_letters = set()
    for letter in word:
        next_sides = next_sides_graph[current]
        letter_found = None
        for side in next_sides:
            if letter in side:
                letter_found = letter
                current = side
                break
        if not letter_found:
            word_ok = False
            break
        word_letters.add(letter)
    if word_ok:
        efficiency = (100.0 * (float(len(word_letters)) / float(len(word)))
                      * (float(len(word_letters)) / float(len(all_letters))))
        return (efficiency, word, word_letters)
    else:
        return None

def printbox(sides):
    top = ' '.join(sides[0])
    toplen = len(top)
    left = list(sides[1])
    right = list(sides[2])
    print('\n ' + top)
    box = []
    box.append('+' + '-' * (toplen - 2) + '+')
    box.append('|' + ' ' * (toplen - 2) + '|')
    box.append(box[0])
    for i in range(0,3):
        print(left[i] + box[i] + right[i])
    print(' ' + ' '.join(sides[3]) + '\n')

def main():
    num_letters = 12
    rxp = f'^[a-zA-Z]{{{num_letters}}}$'
    #
    # Process command-line arguments
    #
    p = argparse.ArgumentParser(description=
                                'Find NYT LetterBoxed solutions. Valid '
                                'solutions are two words, wherein the second '
                                'word begins with the last letter of the '
                                'first.')
    # Required arguments
    p.add_argument('word_list', type=argparse.FileType('r'),
                   help="Path to your English dictionary. Needs to be a "
                   "plaintext list of words, separated by newlines. Doesn't "
                   "have to be sorted.")
    p.add_argument('-l', '--letters', type=str, action='store',
                   help="The allowed letters, in clockwise order, e.g.: "
                   "tnlihawrudof. If you don't specify this option, a random"
                   "set of letters will be selected.")
    ns = p.parse_args()

    letters = ''
    if ns.letters:
        if not re.search(rxp, ns.letters):
            sys.exit('Letters are not in correct format. See example.')
        letters = ns.letters.lower()
        print(f"Using user-provided letters '{letters}'")
    else:
        alphabet = string.ascii_lowercase[:26]
        letters = sample(alphabet, num_letters) # no replacement
        letterstr = ''.join(letters)
        print(f"Using randomly-generated letters '{letterstr}'")

    sides = [frozenset(letters[i:i+3]) for i in range(0, len(letters), 3)]
    printbox(sides)

    # Read each dictionary word out, and filter out the ones that are valid for
    # the sides given
    valid_words = []
    try:
        for word in ns.word_list:
            t = process_word(sides, word.rstrip('\n'))
            if t:
                valid_words.append(t)
    except (BrokenPipeError, IOError) as e:
        print(e, file=sys.stderr)
        sys.stderr.close()

    vwlen = len(valid_words)
    print(f'{vwlen} valid words found.', file=sys.stderr)
    if vwlen < 1:
        sys.exit(-1)

    # Build up a list of words indexed by first letter
    words_by_eff = sorted(valid_words, key=lambda tup: tup[0], reverse=True)
    words_by_letter = {}
    for t in words_by_eff:
        _, word, word_letters = t
        wswl = words_by_letter.get(word[0])
        if wswl:
            wswl.append((word, word_letters))
        else:
            words_by_letter[word[0]] = [(word, word_letters)]

    # Look for two-word combinations.
    word_pairs = []
    for t1 in words_by_eff:
        _, word1, letters1 = t1
        for t2 in words_by_letter[word1[-1]]:
            word2, letters2 = t2
            if len(letters1|letters2) >= num_letters:
                score = len(word1)+len(word2)
                word_pairs.append(f'{word1} {word2}')
    sorted_word_pairs = sorted(word_pairs, key=lambda s: len(s))
    swplen = len(sorted_word_pairs)
    print(f'{swplen} valid two-word pairs found.', file=sys.stderr)
    if swplen < 1:
        print("Try again!\nThis random combination of letters wouldn't "
              "Appear in a NYT Letter Boxed puzzle")
        sys.exit(-1)
    for pair in sorted_word_pairs:
        print(pair)

if __name__ == '__main__':
    main()
