# -*- coding: UTF-8 -*-
from markdown2 import markdown

from ._utils import *


def markdown_encode(mdtext, errors="strict"):
    return markdown(mdtext), len(mdtext)


# note: the group is NOT captured so that the pattern is only used to match the
#        name of the codec and not to dynamically bind to a parametrizable
#        encode function
codecs.add_codec("markdown", markdown_encode,
                 pattern=r"^(?:markdown|Markdown|md)$")
