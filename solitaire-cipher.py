#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__reference__ = "https://www.schneier.com/academic/solitaire/"
__doc__ = """
This tool implements the Solitaire Encryption Algorithm of Bruce Schneier.
"""
__examples__ = ["encrypt \"AAAAA AAAAA\" -s",
                "decrypt \"AAAAA AAAAA\" -d deck.txt"]

# --------------------- IMPORTS SECTION ---------------------
from itertools import cycle
from string import uppercase
from tinyscript import *


class Deck(object):
    length = 54
    iscard = lambda s, x: isinstance(x, int) and 0 <= x < s.length

    def __init__(self, deck, A=52, B=53, shuffle=False):
        assert self.iscard(A) and self.iscard(B)
        self.A = A
        self.B = B
        self.cards = deck
        self.__load(shuffle)
        logger.debug("Start    : {}\n".format(str(self)))

    def __repr__(self):
        d = map(lambda i: i + 1, self.start)
        return ','.join(map(str, d)).replace(str(self.A + 1), 'A') \
                                    .replace(str(self.B + 1), 'B')

    def __str__(self):
        d = map(lambda i: i + 1, self.cards)
        return ','.join(map(str, d)).replace(str(self.A + 1), 'A') \
                                    .replace(str(self.B + 1), 'B')

    def __load(self, shuffle=False):
        """
        Load the input deck from a string as a comma- or space-separated list or
         from a file.

        :post: self.cards is a valid deck with indices from 0 to 53
        """
        d = []  # deck representation
        # try to parse the deck as a comma-/whitespace-separated list
        if len(re.split(r',?\s*', self.cards)) == 54:
            d = self.cards.replace('A', str(self.A)).replace('B', str(self.B))
            d = map(int, re.split(r',?\s*', d))
            if 0 not in d:
                d = map(lambda x: x - 1, d)
        # try to interpret the deck as encoded
        elif os.path.exists(self.cards):
            mapping = Deck.encoding_scheme(False)
            d = map(lambda x: x.strip(), open(self.cards).readlines())
            try:
                d = [mapping[k] for k in d]
            except:
                pass
        # then register the cards only if valid
        assert all(map(self.iscard, d)) and set(range(54)) == set(d), \
               "Invalid deck"
        self.cards = d[:]
        del d
        if shuffle:
            random.shuffle(self.cards)
        self.start = self.cards[:] # save the starting configuration of the deck

    def _count_cut(self):
        c, i, l = self.cards, self.cards[-1], len(self.cards)
        self.cards = (c[i+1:-1] + c[:i+1] + c[-1:])[:l]
        logger.debug("CountCut : {}".format(str(self)))

    def _move_down(self):
        l = len(self.cards)
        for n, j in [(1, self.A), (2, self.B)]:
            idx = self.cards.index(j)
            i = int(idx + n >= l)
            self.cards.pop(idx)
            self.cards.insert((idx + n) % l + i, j)
        logger.debug("MovDown  : {}".format(str(self)))

    def _output_card(self):
        return self.cards[min(self.cards[0]+1, len(self.cards) - 1)] + 1

    def _triple_cut(self):
        c = self.cards
        idxa, idxb = c.index(self.A), c.index(self.B)
        m, M = min(idxa, idxb), max(idxa, idxb)
        self.cards = c[M+1:] + c[m:M+1] + c[:m]
        logger.debug("TripleCut: {}".format(str(self)))

    def keystream(self):
        i, passed = 1, False
        while True:
            if not passed:
                logger.debug("DRAW #{}".format(i))
            passed = False
            self._move_down()
            self._triple_cut()
            self._count_cut()
            card = self._output_card()
            if card not in [self.A + 1, self.B + 1]:
                logger.debug("> Card: {}\n".format(card))
                yield card
                i += 1
            else:
                passed = True

    @property
    def encoded(self):
        mapping = Deck.encoding_scheme(True)
        return '\n'.join(map(lambda c: mapping[c], self.start))

    @staticmethod
    def encoding_scheme(encode=True):
        bridge_suit = []
        for c in ['c', 'd', 'h', 's']:
            for f in ['a'] + map(str, range(2, 11)) + ['j', 'q', 'k']:
                bridge_suit.append(c + f)
        bridge_suit.extend(['jr', 'jb'])
        return {i: k for i, k in enumerate(bridge_suit)} if encode else \
               {k: i for i, k in enumerate(bridge_suit)}


class Solitaire(object):
    chr2int = lambda s, c: uppercase.index(c) + 1
    int2chr = lambda s, i: uppercase[i-1]

    def __init__(self, deck, A=52, B=53):
        assert isinstance(deck, Deck)
        self.deck = deck

    def decrypt(self, ciphertext):
        ciphertext = ciphertext.replace(' ', '').upper()
        plaintext = ""
        for i, k in enumerate(self.deck.keystream()):
            if i >= len(ciphertext):
                break
            plaintext += self.int2chr((self.chr2int(ciphertext[i]) - k) % 26)
        return plaintext

    def encrypt(self, plaintext):
        plaintext = plaintext.replace(' ', '').upper()
        plaintext = filter(lambda x: x.isalnum(), plaintext)
        ciphertext = ""
        for i, k in enumerate(self.deck.keystream()):
            if i >= len(plaintext):
                break
            ciphertext += self.int2chr((self.chr2int(plaintext[i]) + k) % 26)
        return ' '.join(ciphertext[i:i+5] for i in range(0, len(ciphertext), 5))


# ---------------------- MAIN SECTION -----------------------
if __name__ == '__main__':
    #kw = {'formatter_class': argparse.RawTextHelpFormatter}
    subparsers = parser.add_subparsers(help="commands", dest="command")
    decrypt = subparsers.add_parser('decrypt', help="decrypt message")
    encrypt = subparsers.add_parser('encrypt', help="encrypt message")
    for subparser in [decrypt, encrypt]:
        subparser.add_argument("message", help="message to be handled")
        subparser.add_argument("-a", type=int, default=53, help="joker A")
        subparser.add_argument("-b", type=int, default=54, help="joker B")
        subparser.add_argument("-d", default=','.join(map(str, range(1, 55))),
                               dest="deck", help="deck file or list of integers")
        subparser.add_argument("-p", dest="passphrase", help="passphrase")
        subparser.add_argument("-v", dest="verbose", action="store_true",
                               help="verbose mode")
    encrypt.add_argument("-o", dest="output", default="deck.txt",
                         help="save the encoded deck to")
    encrypt.add_argument("-s", dest="shuffle", action="store_true",
                         help="shuffle the deck")
    initialize(globals(), noargs_action="demo")
    validate(globals(),
        ('a', "not 0 < ? <= 54", "A must be an integer from 1 to 54"),
        ('b', "not 0 < ? <= 54", "B must be an integer from 1 to 54"),
        ('deck', "not Deck( ? )"),
    )
    output = getattr(args, "output", None)
    shuffle = getattr(args, "shuffle", False)
    solitaire = Solitaire(Deck(args.deck, args.a - 1, args.b - 1, shuffle))
    logger.info(getattr(solitaire, args.command)(args.message))
    logger.info(repr(solitaire.deck))
    if output is not None:
        with open(output, 'w') as f:
            f.write(solitaire.deck.encoded)
        logger.info("Saved the encoded deck to '{}'".format(output))
