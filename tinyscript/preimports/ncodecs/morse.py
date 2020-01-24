# -*- coding: UTF-8 -*-
from ._utils import *


TRANS = {
    # letters
    'a': ".-", 'b': "-...", 'c': "-.-.", 'd': "-..", 'e': ".", 'f': "..-.",
    'g': "--.", 'h': "....",  'i': "..", 'j': ".---", 'k': "-.-", 'l': ".-..",
    'm': "--", 'n': "-.", 'o': "---", 'p': ".--.", 'q': "--.-", 'r': ".-.",
    's': "...", 't': "-", 'u': "..-", 'v': "...-", 'w': ".--", 'x': "-..-",
    'y': "-.--", 'z': "--..",
    # digits
    '1': ".----", '2': "..---", '3': "...--", '4': "....-", '5': ".....",
    '6': "-....", '7': "--...", '8': "---..", '9': "----.", '0': "-----",
    # punctuation
    ',': "--..--", '.': ".-.-.-", ':' : "---...", '?': "..--..", '/': "-..-.",
    '-': "-....-", '=' : "-...-", '(': "-.--.", ')': "-.--.-", '@' : ".--.-.",
    '\'': ".----.", '_': "..--.-", '!': "-.-.--", '&': ".-...", '"': ".-..-.",
    ';': "-.-.-.", '$': "...-..-",
    # word separator
    ' ' : "/",
}
BTRANS = {v: k for k, v in TRANS.items()}
REPLACE_CHAR = "#"


class MorseError(ValueError):
    pass


class MorseDecodeError(MorseError):
    pass
codecs.MorseDecodeError = MorseDecodeError


class MorseEncodeError(MorseError):
    pass
codecs.MorseEncodeError = MorseEncodeError


def morse_encode(text, errors="strict"):
    r = ""
    for i, c in enumerate(ensure_str(text)):
        try:
            r += TRANS[c] + " "
        except KeyError:
            if errors == "strict":
                raise codecs.MorseEncodeError("'morse' codec can't encode "
                                              "character '{}' in position {}"
                                              .format(c, i))
            elif errors == "replace":
                r += REPLACE_CHAR + " "
            elif errors == "ignore":
                continue
            else:
                raise ValueError("Unsupported error handling {}".format(errors))
    return r[:-1], len(text)


def morse_decode(text, errors="strict"):
    r = ""
    for i, c in enumerate(ensure_str(text).split()):
        try:
            r += BTRANS[c]
        except KeyError:
            if errors == "strict":
                raise codecs.MorseDecodeError("'morse' codec can't decode "
                                              "character '{}' in position {}"
                                              .format(c, i))
            elif errors == "replace":
                r += REPLACE_CHAR
            elif errors == "ignore":
                continue
            else:
                raise ValueError("Unsupported error handling {}".format(errors))
    return r, len(text)


codecs.add_codec("morse", morse_encode, morse_decode)
