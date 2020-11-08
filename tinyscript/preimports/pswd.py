# -*- coding: utf8 -*-
"""Module for enhancing getpass preimport. It adds a function that prompts for a password that must be compliant with a
 simple password policy.
"""

import getpass

from .log import bindLogger
from ..helpers.password import getpass as _getpass


@bindLogger
def __getcompliantpass(prompt="Password: ", stream=None, policy=None, once=False):
    """ This function allows to enter a password enforced through a password policy able to check for the password
         length, characters set and presence in the given wordlists.
    
    :param prompt: prompt text
    :param stream: a writable file object to display the prompt (defaults to the tty or to sys.stderr if not available)
    :param policy: password policy to be considered
    :param once:   ask for a password only once
    :return:       policy-compliant password
    """
    pwd = None
    while pwd is None:
        logger.debug("Special conjunction characters are stripped")
        try:
            pwd = _getpass(prompt, stream, policy).strip()
        except ValueError as exc:
            if hasattr(exc, "errors"):
                for e in exc.errors:
                    logger.error(e)
                pwd = None
            else:
                raise
        except KeyboardInterrupt:
            print("")
            break
        if once:
            break
    return pwd
getpass.getcompliantpass = __getcompliantpass

