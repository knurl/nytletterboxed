#!/usr/bin/env python

import os, sys, pdb, argparse, re, string, random
from functools import reduce

num_letters = 12

def process_word(letters, word):
    sides = [frozenset(letters[i:i+3]) for i in range(0, len(letters), 3)]
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

def solve_puzzle(word_list, letters):
    global num_letters
    assert len(letters) == num_letters

    # Read each dictionary word out, and filter out the ones that are valid for
    # the sides given
    word_list.seek(0)
    valid_words = []
    try:
        for word in word_list:
            t = process_word(letters, word.rstrip('\n'))
            if t:
                valid_words.append(t)
    except (BrokenPipeError, IOError) as e:
        print(e, file=sys.stderr)
        sys.stderr.close()
        sys.exit(0)

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
    return sorted(word_pairs, key=lambda s: len(s))

def printbox(letters):
    top = ' '.join(letters[:3])
    right = letters[3:6]
    bot = ' '.join(letters[6:9])
    left = letters[9:]

    toplen = len(top)

    # top row
    print('\n ' + top)

    # middle rows
    box = []
    box.append('+' + '-' * (toplen - 2) + '+')
    box.append('|' + ' ' * (toplen - 2) + '|')
    box.append(box[0])
    for i in range(0,3):
        print(left[i] + box[i] + right[i])

    print(' ' + bot + '\n')

def main():
    global num_letters
    rxp = f'^[a-zA-Z]{{{num_letters}}}$'

    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'

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
                   default=None,
                   help="The allowed letters, in clockwise order, e.g.: "
                   "tnlihawrudof. If you don't specify this option, a random"
                   "set of letters will be selected.")
    ns = p.parse_args()

    letters = ns.letters
    word_pairs = []

    if letters:
        if not re.search(rxp, ns.letters):
            sys.exit('Letters are not in correct format. See example.')
        letters = ns.letters.lower()
        print(f"Using user-provided letters '{letters}'")
        word_pairs = solve_puzzle(ns.word_list, letters)
        if not word_pairs:
            print(f'Could not find solution using those letters!')

    if not word_pairs:
        print('Attempting to generate a new puzzle', end='', flush=True)

    while not word_pairs:
        print('.', end='', flush=True)
        nvowels = random.randrange(2, 4)
        vowel_list = random.sample(vowels, nvowels)
        cons_list = random.sample(consonants, num_letters - nvowels)
        if 'q' in cons_list and 'u' not in vowel_list:
            vowel_list = ['u'] + vowel_list
        letter_list = (vowel_list + cons_list)[:12]
        random.shuffle(letter_list)
        letters = ''.join(letter_list)
        assert(len(letters) == num_letters)
        word_pairs = solve_puzzle(ns.word_list, letters)

    printbox(letters)
    if word_pairs:
        print("Solutions are:")
        print('\n'.join(word_pairs[:5]))
    else:
        print("No solutions found!")

if __name__ == '__main__':
    main()
