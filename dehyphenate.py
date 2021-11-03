#!/usr/bin/env python3

import sys
import re

from string import punctuation
from itertools import tee, zip_longest
from argparse import ArgumentParser


def argparser():
    ap = ArgumentParser()
    ap.add_argument('text', nargs='+')
    return ap


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip_longest(a, b)


def split_keep_space(text):
    return re.split(r'(\s+)', text)


def ends_with_hyphenated(line):
    return re.search(r'\S-$', line)


def starts_with_word(line):
    return re.match(r'^\S', line) is not None


def starts_with_space(line):
    return line.lstrip() != line


def split_last_token(string):
    m = re.match(r'^(.*?)(\S+)$', string)
    return m.groups()


def split_first_token(string):
    m = re.match(r'^(\S+)(.*)', string)
    return m.groups()


def split_hyphen(string):
    assert string[-1] == '-'
    return string[:-1], string[-1]


def is_same_vowel(char1, char2):
    return char1.lower() == char2.lower() and char2.lower() in 'aeiouyäöå'


def is_number(string):
    return all(c in '0123456789-.' for c in string)


def is_regular_word(string):
    """Return True iff string is a "regular" word that can be part
    of a non-hyphenated compound."""
    if len(string) < 2:
        return False
    elif is_number(string):
        return False
    elif string.isupper():
        return False
    else:
        return True


def is_proper_noun(string):
    """Return True iff string appears to be a proper noun."""
    if string[-1] in punctuation:
        string = string[:-1]    # approximate separating punctuation
    return string.isalpha() and string[0].isupper() and string[1:].islower()


def rejoin(hyphenated, line):
    """Add hyphenated word part to line start, dehyphenating when required."""
    first_part, hyphen = split_hyphen(hyphenated)
    second_part, rest = split_first_token(line)

    if is_same_vowel(first_part[-1], second_part[0]):
        # same vowel before and after hyphen
        keep_hyphen = True
    elif not (first_part[-1].isalpha() and second_part[0].isalpha()):
        # only join alphabetic with alphabetic char
        keep_hyphen = True
    elif not (is_regular_word(first_part) and
              is_regular_word(second_part)):
        # one or both are not "regular" words
        keep_hyphen = True
    elif is_proper_noun(second_part):
        # Keep hyphen for proper noun compounds. Don't check first
        # part as start-of-sentence capitalization may confound the
        # capitalization pattern.
        keep_hyphen = True
    else:
        keep_hyphen = False

    if keep_hyphen:
        rejoined = first_part + hyphen + second_part
    else:
        rejoined = first_part + second_part

    return rejoined + rest


def dehyphenate(stream):
    """Dehyphenate text from stream, writing to stdout."""
    hyphenated = None
    for line, next_line in pairwise(stream):
        line = line.rstrip()

        if hyphenated:
            line = rejoin(hyphenated, line)
        hyphenated = None
        
        if not line or line.isspace():
            line_end = '\n'    # keep blank lines
        elif not next_line or next_line.isspace():
            line_end = '\n'    # keep linebreak before blanks
        elif ends_with_hyphenated(line) and starts_with_word(next_line):
            # join hyphenated word
            line, hyphenated = split_last_token(line)
            line_end = ''
        else:
            # space between all other words
            line_end = ' '

        print(line, end=line_end)


def main(argv):
    args = argparser().parse_args(argv[1:])

    for fn in args.text:
        with open(fn, errors='replace') as f:
            dehyphenate(f)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
