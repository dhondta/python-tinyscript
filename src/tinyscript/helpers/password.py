# -*- coding: utf8 -*-
""" Compliant password prompt function relying on a simple password policy.

Policy:
- Prevents from using a few conjunction characters (i.e. whitespace, tabulation,
   newline)
- Use passwords of 8 to 40 characters (lengths by default)
- Use at least one lowercase character
- Use at least one uppercase character
- Use at least one digit
- Use at least one special character
- Do not use a password known in a dictionary (e.g. this of John the Ripper)
"""
import getpass as _getpass

from .attack import expand_mask, parse_rule, MASKS
from .constants import *
from .data.utils import entropy_bits
from ..preimports import os, re, platform


__all__ = __features__ = ["getpass", "getrepass"]


BAD_PASSWORDS_LISTS = {
    'default': {
        'password.lst': ["./", "~/"],
        'rockyou.txt':  ["./", "~/"],
    },
    'linux': {
        'password.lst': ["./", "~/", "/opt/john/run", "/usr/local/share/john", "/usr/share/john", "/var/lib/john"],
        'rockyou.txt':  ["./", "~/"],
    },
}
DEFAULT_POLICY = {
    'allowed':   "?l?L?d?s",
    'length':    (8, 40),
    'rules':     "lut",  # .lower(), .upper(), .title()
    'entropy':   32,
    'wordlists': BAD_PASSWORDS_LISTS.get(platform.system().lower(), "default"),
}
MASK_DESCRIPTIONS = {
    'd': "digits",
    'h': "lowercase hexadecimal",
    'H': "uppercase hexadecimal",
    'l': "lowercase letters",
    'L': "uppercase letters",
    'p': "printable characters",
    's': "special characters",
}
MASK_MODIFIERS = {v: k for k, v in MASKS.items()}

__policies_registry = {}


def __validate(policy):
    policy = policy or {}
    if not isinstance(policy, dict):
        raise ValueError("Bad policy format ; should be a dictionary")
    if hash(str(policy)) in __policies_registry:
        return policy
    for k in DEFAULT_POLICY.keys():
        if k not in policy.keys():
            policy[k] = DEFAULT_POLICY[k]
    policy['allowed_expanded'] = expand_mask(policy['allowed'])
    policy['allowed'] = policy['allowed'].replace("?", "")
    policy['required'] = policy.get('required', policy['allowed']).replace("?", "")
    for k in ["allowed", "required"]:
        if any(c not in "dhHlLps" for c in policy[k]):
            raise ValueError("Bad %s character set mask ; should be only amongst 'dhHlLps'" % k)
    for m in policy['required']:
        if m not in policy['allowed']:
            raise ValueError("Bad allowed/required set mask ; '?%s' is not in the allowed set" % m)
    # compose charset string
    s = ""
    for m in policy['allowed']:
        s += MASK_DESCRIPTIONS[m] + ", "
    s = s.rstrip(", ")
    s = s.split(", ")
    s = ", ".join(s[:-1]) + " and " + s[-1]
    policy['charset_string'] = s
    minl, maxl = policy['length']
    if minl < 1:
        raise ValueError("Bad minimum length ; should be greater than 0")
    if maxl < 1:
        raise ValueError("Bad maximum length ; should be greater than 0")
    if maxl < minl:
        raise ValueError("Bad maximum length ; should be greater than the minimum length")
    if isinstance(policy['wordlists'], (list, tuple)):
        # filter out non-existing wordlists
        for p in policy['wordlists']:
            if not os.path.isfile(os.path.expanduser(p)):
                policy['wordlists'].remove(p)
    elif isinstance(policy['wordlists'], dict):
        # transform the dictionary of potential wordlist paths to a list of existing wordlists
        e = []
        for filename, paths in policy.pop('wordlists').items():
            for path in paths:
                p = os.path.join(os.path.expanduser(path), filename)
                if os.path.isfile(p):
                    e.append(p)
                    break
        policy['wordlists'] = tuple(e)
    elif policy.get('wordlists') is not None:
        raise ValueError("Bad policy passwords files exclusion list ; should be a list or a dictionary")
    __policies_registry[hash(str(policy))] = policy
    return policy


def getpass(prompt="Password: ", stream=None, policy=None):
    """ This function allows to enter a password enforced through a password policy able to check for the password
         length, characters set and presence in the given wordlists.
    
    :param prompt: prompt text
    :param stream: a writable file object to display the prompt (defaults to the tty or to sys.stderr if not available)
    :param policy: password policy to be considered
    :return:       policy-compliant password
    """
    policy = __validate(policy)
    pwd, error = None, False
    # get values from policy
    minl, maxl = policy['length']
    pwd = _getpass.getpass(prompt, stream).strip()
    # first, check the length
    errors = []
    if len(pwd) < minl:
        errors.append("Please enter a password of at least {} characters".format(minl))
    if len(pwd) > maxl:
        errors.append("Please enter a password of at most {} characters".format(maxl))
    # second, check the characters
    if any(c not in "".join(policy['allowed_expanded']) for c in pwd):
        errors.append("Please enter a password with only " + policy['charset_string'])
    # third, check the entropy
    e = entropy_bits(pwd)
    if e < policy['entropy']:
        errors.append("Too weak password ; should have %d bits of entropy (currently %d)" % (policy['entropy'], e))
    # now, check for minimal character requirements
    for m, group in zip(policy['allowed'], policy['allowed_expanded']):
        if not any(c in group for c in pwd) and m in policy['required']:
            errors.append("Please enter a password that contains at least one " + MASK_DESCRIPTIONS[m].rstrip("s"))
    # then, check for bad passwords
    found = False
    for fp in (policy.get('wordlists') or []):
        with open(fp) as f:
            for l in f:
                passwords = [l.strip()]
                for r in parse_rule(policy.get('rules', "")):
                    passwords.append(r(passwords[0]))
                for p in set(passwords):
                    if pwd == p:
                        found = True
                        break
                if found:
                    break
        if found:
            errors.append("Please enter a more complex password (found in %s)" % fp)
            break
    if len(errors) > 0:
        g = {'__name__': "__main__"}
        exec("class NonCompliantPasswordError(ValueError):\n    def __init__(self, msg, errors, **kwargs):\n        " \
             "super(NonCompliantPasswordError, self).__init__(msg, **kwargs)\n        self.errors = errors", g)
        raise g['NonCompliantPasswordError'](pwd, errors)
    return pwd


def getrepass(prompt="Password: ", stream=None, pattern=None):
    """ This function allows to enter a password enforced through pattern matching.
    
    :param prompt:  prompt text
    :param stream:  a writable file object to display the prompt (defaults to the tty or to sys.stderr if not available)
    :param pattern: pattern to be used
    :return:        pattern-compliant password
    """
    pwd = _getpass.getpass(prompt, stream).strip()
    if pattern and not re.search(pattern, pwd):
        g = {'__name__': "__main__"}
        exec("class NonCompliantPasswordError(ValueError): pass", g)
        raise g['NonCompliantPasswordError'](pwd)
    return pwd

