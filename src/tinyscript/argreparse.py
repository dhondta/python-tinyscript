#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for extending argparse features, for simplifying parser.py.

"""
import operator as op
import random
import re
import shlex
import sys
from argparse import _ActionsContainer, _ArgumentGroup, _MutuallyExclusiveGroup, _AttributeHolder, _SubParsersAction, \
                     Action, ArgumentDefaultsHelpFormatter, ArgumentError, ArgumentTypeError, RawTextHelpFormatter, \
                     SUPPRESS, _UNRECOGNIZED_ARGS_ATTR, Namespace as BaseNamespace, ArgumentParser as BaseArgumentParser
from os import environ
from os.path import abspath, basename, dirname, sep, splitext
from stat import S_IXUSR
try:
    from configparser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError

from .features.loglib import logger
from .helpers.constants import PYTHON3
from .helpers.inputs import user_input
from .helpers.licenses import *
from .helpers.data.types import is_executable, is_in_path, is_long_opt, is_pos_int, is_short_opt
from .helpers.termsize import get_terminal_size
from .helpers.text import *
from .helpers.text import configure_docformat, txt_terminal_render
from .preimports.shutilp import which


__all__ = ["ArgumentParser", "DUNDERS", "SUPPRESS"]


BASE_DUNDERS = ['__author__', '__contributors__', '__copyright__', '__credits__', '__license__', '__reference__',
                '__source__', '__training__']
DUNDERS = BASE_DUNDERS + [
    '__date__', '__details__', '__description__', '__doc__', '__docformat__', '__email__', '__examples__',
    '__functions__', '__maximum_python_version__', '__minimum_python_version__', '__priority__', '__product__',
    '__script__', '__status__', '__version__',
]
if sys.version_info >= (3, 8):
    DUNDERS.append('__requires__')

DEFAULT_MAX_LEN     = 20
DEFAULT_LST_MAX_LEN = 10


stem = lambda p: splitext(basename(p))[0]


# ------------------------------- CUSTOM ACTIONS -------------------------------
class _ConfigAction(Action):
    """ Custom action for handling an INI configuration file. """
    def __init__(self, option_strings, dest=None, default=None, help=None):
        super(_ConfigAction, self).__init__(option_strings=option_strings, dest=SUPPRESS, default=default, nargs=1,
                                            help=gt(help), metavar="INI")
    
    def __call__(self, parser, namespace, values, option_string=None):
        conf = values[0]
        setattr(namespace, "read_config", conf)
        if conf not in parser._config.read(conf):
            logger.error(gt("Config file '{}' not found").format(conf))
            sys.exit(2)
        parser.config_args()


class _DemoAction(Action):
    """ Custom action for triggering the execution of an example. """
    def __init__(self, option_strings, dest=SUPPRESS, help=None):
        super(_DemoAction, self).__init__(option_strings=option_strings, dest=SUPPRESS, default=SUPPRESS, nargs=0,
                                          help=gt(help))
    
    def __call__(self, parser, namespace, values, option_string=None):
        parser.demo_args()


class _ExtendAction(Action):
    """ Custom action for extending a list of values. """
    def __call__(self, parser, namespace, values, option_string=None):
        l = getattr(namespace, self.dest) or []
        if not isinstance(l, list):
            if not getattr(namespace, "default_silent", False):
                logger.warning(gt("extend is used with {} while its value is not a list").format(self.dest))
            l = []
        if not isinstance(values, list):
            values = [values]
        l.extend(values)
        setattr(namespace, self.dest, l)


class _NewSubParsersAction(_SubParsersAction):
    """ Modified version of argparse._SubParsersAction for handling formatters of subparsers, inheriting from this of
         the main parser. """
    last = False
    
    def __init__(self, *args, **kwargs):
        kwargs.pop('required', True)
        super(_NewSubParsersAction, self).__init__(*args, **kwargs)
    
    def add_parser(self, name, **kwargs):
        category = kwargs.pop('category', "default")
        # set prog from the existing prefix
        if kwargs.get('prog') is None:
            kwargs['prog'] = "%s %s" % (self._prog_prefix, name)
        # create a pseudo-action to hold the choice help
        aliases = kwargs.pop('aliases', [])
        if 'help' in kwargs:
            help = kwargs.pop('help')
            # see [Python2] argparse.py:1029 and [Python3] argparse.py:1059
            args = (name, aliases, help) if PYTHON3 else (name, help)
            choice_action = self._ChoicesPseudoAction(*args)
            choice_action.category = category
            self._choices_actions.append(choice_action)
        # create the parser, but with another formatter and separating the help into an argument group
        parser = self._parser_class(ArgumentParser.globals_dict, add_help=False, **kwargs)
        parser.name = name
        # add default extra arguments group
        i = parser.add_argument_group("extra arguments")
        i.add_argument("-h", action="usage", prefix="show", help=gt("show usage message and exit"))
        i.add_argument("--help", action="help", prefix="show", help=gt("show this help message and exit"))
        # add it to the map
        self._name_parser_map[name] = parser
        # make parser available under aliases also (Python3 only ; see before)
        for alias in aliases:
            self._name_parser_map[alias] = parser
        return parser


class _UsageAction(Action):
    """ Custom action for displaying the usage message. """
    def __init__(self, option_strings, dest=SUPPRESS, help=None):
        super(_UsageAction, self).__init__(option_strings=option_strings, dest=SUPPRESS, default=SUPPRESS, nargs=0,
                                           help=gt(help))
    
    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_usage()
        parser.exit()


class _WizardAction(Action):
    """ Custom action for triggering the wizard, asking for argument values. """
    def __init__(self, option_strings, dest=SUPPRESS, help=None):
        super(_WizardAction, self).__init__(option_strings=option_strings, dest=SUPPRESS, default=SUPPRESS, nargs=0,
                                            help=gt(help))

    def __call__(self, parser, namespace, values, option_string=None):
        parser.input_args()


# ------------------------------ CUSTOM ENTITIES -------------------------------
class _NewActionsContainer(_ActionsContainer):
    """ Modified version of argparse._ActionsContainer for handling a new "note" keyword argument. """
    def __init__(self, *args, **kwargs):
        super(_NewActionsContainer, self).__init__(*args, **kwargs)
        self.register('action', 'parsers', _NewSubParsersAction)
        self.register('action', 'config', _ConfigAction)
        self.register('action', 'demo', _DemoAction)
        self.register('action', 'extend', _ExtendAction)
        self.register('action', 'usage', _UsageAction)
        self.register('action', 'wizard', _WizardAction)
    
    def add_argument(self, *args, **kwargs):
        new_kw = {k: v for k, v in kwargs.items()}
        # collect Tinyscript-added keyword-arguments
        cancel = new_kw.pop('cancel', False)
        orig = new_kw.pop('orig', None)
        note = new_kw.pop('note', None)
        last = new_kw.pop('last', False)
        prefix = new_kw.pop('prefix', None)
        suffix = new_kw.pop('suffix', None)
        try:
            # define the action based on argparse, with only argparse-known keyword-arguments
            action = super(_NewActionsContainer, self).add_argument(*args, **new_kw)
            # now set Tinyscript-added keyword-arguments
            action.note = None if note is None else gt(note)
            action.last = last
            action.orig = orig
            action.prefix = prefix
            action.suffix = suffix
            return args[-1]
        except ArgumentError:
            # drop the argument if conflict and cancel set to True
            if cancel:
                return
            # otherwise, retry after removing the short option string
            args = list(args)
            short_opt = list(filter(is_short_opt, args))
            if len(short_opt) > 0:
                args.remove(short_opt[0])
                if len(args) > 0:
                    return self.add_argument(*args, **kwargs)
            # otherwise, retry after modifying the long option string with the precedence to the prefix (if set) then
            #  the suffix (if set)
            long_opt = list(filter(is_long_opt, args))
            if len(long_opt) > 0:
                long_opt = args.pop(args.index(long_opt[0]))
                if kwargs.get('action') in [None, 'store', 'append', 'store_const', 'append_const']:
                    # set metavar only if no choices given ; otherwise, it takes the precedence on choices in the help
                    kwargs['metavar'] = kwargs.get('metavar') or \
                                        (long_opt.lstrip('-').upper() if not kwargs.get('choices') else None)
                curr_opt = long_opt.lstrip("-")
                kwargs['orig'] = curr_opt.replace("-", "_")
                if prefix:
                    long_opt = "--{}-{}".format(prefix, curr_opt)
                    args.append(long_opt)
                    return self.add_argument(*args, **kwargs)
                elif suffix:
                    long_opt = "{}-{}".format(long_opt, suffix)
                    args.append(long_opt)
                    return self.add_argument(*args, **kwargs)
    
    def add_argument_group(self, title, *args, **kwargs):
        # return the group if it already exists
        for group in self._action_groups:
            if group.title == title:
                return group
        # add the new group, after or before the specified one if relevant
        added, after, before = False, kwargs.pop('after', None), kwargs.pop('before', None)
        group = _NewArgumentGroup(self, title, *args, **kwargs)
        if after or before:
            for i, g in enumerate(self._action_groups):
                if g.title == after or g.title == before:
                    self._action_groups.insert(i + [0, 1][g.title == after], group)
                    added = True
                    break
        if not added:
            self._action_groups.append(group)
        return group
    
    def add_mutually_exclusive_group(self, **kwargs):
        group = _NewMutuallyExclusiveGroup(self, **kwargs)
        self._mutually_exclusive_groups.append(group)
        return group


class _NewArgumentGroup(_ArgumentGroup, _NewActionsContainer):
    """ Alternative argparse._ArgumentGroup for modifying argument groups handling in the modified ActionsContainer. """
    pass
        

class _NewMutuallyExclusiveGroup(_MutuallyExclusiveGroup, _NewArgumentGroup):
    """ Alternative argparse._MutuallyExclusiveGroup for modifying arguments mutually exclusive groups handling in the
         modified ActionsContainer. """
    pass


class ArgumentParser(_NewActionsContainer, BaseArgumentParser):
    """ Modified version of argparse.ArgumentParser, based on the modified ActionsContainer.
    
    :param globals_dict: globals() dictionary from the calling script/tool
                         NB: only for help formatting purpose ; therefore this is NOT propagated through subparsers
    :param args:         arguments applicable for argparse.ArgumentParser
    :param kwargs:       kwarguments applicable for argparse.ArgumentParser
                         NB: 'prog' set to preformatted program name
                             'add_help' set to False (customized)
                             'conflict_handler' set to "error" (cfr tuning of add_argument)
                             'formatter_class' set to custom HelpFormatter
                             'epilog' set to preformatted usage message
                             'description' set to preformatted help message
    """
    _config = ConfigParser()
    is_action = lambda s, a, *l: any(type(a) is s._registry_get('action', n) for n in l)
    name = "main"
    
    def __init__(self, globals_dict=None, *args, **kwargs):
        ArgumentParser.globals_dict = gd = globals_dict or {}
        if sys.version_info >= (3, 8):
            self._check_requirements(gd.get('__requires__'))
        configure_docformat(gd)
        self._config_parsed = False
        self._docfmt = gd.get('__docformat__')
        self._reparse_args = {'pos': [], 'opt': [], 'sub': []}
        self.examples = gd.get('__examples__', [])
        script = stem(sys.argv[0])
        self.banner = gd['__scriptname__'] = gd.get('__banner__', script)
        if kwargs.get('prog') is None:
            path = abspath(which(script) or script)
            ArgumentParser.prog = kwargs['prog'] = "python " + script if not is_executable(path) else \
                                                   "./" + script if not is_in_path(dirname(path)) else script
        kwargs['add_help'] = False
        kwargs['conflict_handler'] = "error"
        # when __docformat__ is set, fixing max_help_position to terminal's width forces argparse to format arguments
        #  with their help on the same line ; in other words, formatting is left to the renderer
        try:
            mhp = get_terminal_size()[0]
        except TypeError:
            mhp = 80
        kwargs['formatter_class'] = HelpFormatter if self._docfmt is None else \
                                    lambda prog: HelpFormatter(prog, max_help_position=mhp)
        # format the epilog message
        if self.examples:
            _ = ["{} {}".format(ArgumentParser.prog, e) for e in self.examples]
            _ = list(filter(lambda x: x.startswith(kwargs['prog']), _))
            if len(_) > 0:
                kwargs['epilog'] = txt2title(gt("Usage example{}".format(["", "s"][len(_) > 1])) + ":")
                e = '\n'.join(["\n", "  "][self._docfmt is None] + txt2paragraph(e) for e in _)
                kwargs['epilog'] += "\n" + e
        # format the description message
        d = gd.get('__description__', script)
        d += " " + str(gd.get('__version__') or "")
        d = txt2title(d, level=1)
        v = gd.get('__status__')
        if v:
            d += " (" + v + ")"
        try:
            l = max(list(map(lambda x: len(txt2italic(x.strip('_'))),
                             [bd for bd in BASE_DUNDERS if gd.get(bd) is not None])))
        except ValueError:
            l = 0
        for k in BASE_DUNDERS:
            m = gd.get(k)
            if m:
                if k == '__copyright__':
                    if not isinstance(m, tuple):
                        m = (m, )
                    m = copyright(*m)
                elif k == '__license__':
                    m = license(m, True) or m
                elif k == '__contributors__':
                    # data structure (per contributor):
                    # {
                    #   'author': ...,
                    #   'email':  ..., (optional)
                    #   'reason': ..., (optional)
                    # }
                    m = ""
                    for i, contributor in enumerate(gd[k]):
                        s = contributor.get('author') or ""
                        email = contributor.get('email')
                        if email:
                            s += txt2email(e) if s == "" else " ({})".format(txt2email(str(email)))
                        if s == "":  # do not display an 'reason' if no 'author' and 'email' is defined
                            continue
                        reason = contributor.get('reason')
                        if reason:
                            s += " - " + str(reason)
                        m += ["", (l + 2) * " "][i > 0] + s
                meta = ("{: <%d}: {}" % l).format(txt2italic(k.strip('_').capitalize()), m)
                if k == '__author__':
                    e = gd.get('__email__')
                    if e:
                        meta += " ({})".format(txt2email(e))
                d += ["\n\n", "\n"][self._docfmt is None] + txt2paragraph(meta)
        doc = txt2blockquote(gd.get('__doc__') or "")
        if doc:
            d += "\n\n" + doc
        kwargs['description'] = d
        self.details = gd.get('__details__', [])
        # now initialize argparse's ArgumentParser with the new arguments
        super(ArgumentParser, self).__init__(*args, **kwargs)
    
    def _check_requirements(self, requires):
        """ Check for package requirements before continuing.
        
        :param requires: dictionary of requirements
        """
        environ['SETUPTOOLS_USE_DISTUTILS'] = "stdlib"
        # importlib.metadata is available only from Python 3.8
        from importlib.metadata import version as get_version
        from setuptools.extern.packaging.version import Version
        errors = []
        requires = requires or {}
        if not isinstance(requires, dict):
            logger.warning(gt("'__requires__' does not contain a dictionary ({}) ; could not check requirements")
                              .format(str(requires)))
            requires = {}
        for m, v in requires.items():
            o, v = re.match(r"^([<>]|[<>=!]=|)(.*)$", v).groups()
            operator = {'': op.ge, '<': op.lt, '>': op.gt, '<=': op.le, '>=': op.ge, '==': op.eq, '!=': op.ne}[o]
            desired, actual = Version(v), Version(get_version(m))
            if not operator(actual, desired):
                errors.append((m, o or ">=", str(desired), str(actual)))
        if len(errors) > 0:
            if len(errors) == 1:
                msg = "Bad version for module '%s' ; should be %s%s while actual version is %s" % errors[0]
            else:
                msg = ""
                for error in errors:
                    msg += "\n- Bad version for module '%s' ; should be %s%s while actual version is %s" % error
            raise RequirementError(msg)
    
    def _filtered_actions(self, *a_types):
        """ Get actions filtered on a list of action types.
        
        :param a_type: argparse.Action instance name (e.g. count, append)
        """
        for a in filter(lambda _: self.is_action(_, *a_types), self._actions):
            yield a
    
    def _get_value(self, a, s):
        """ Get the value from an argument string given its related action.
        NB: This method is mostly the same as the original ; it customizes the "invalid ... value" message.
        
        :param a: argparse.Action instance
        :param s: argument string
        :return:  resulting valuefro mthe argument string given its action
        """
        type_func = self._registry_get('type', a.type, a.type)
        if not callable(type_func):
            raise ArgumentError(a, gt('%r is not callable') % type_func)
        try:
            result = type_func(s)
        except ArgumentTypeError:
            raise ArgumentError(a, str(sys.exc_info()[1]))
        except (TypeError, ValueError):
            # clean up the name (do not keep the function name, e.g. "_my_argument_action", but make it more
            #  user-friendly, e.g. "my argument action"
            name = getattr(a.type, '__name__', repr(a.type)).strip("_").replace("_", " ")
            raise ArgumentError(a, gt('invalid %s value: %r') % (name, s))
        return result
    
    def _input_arg(self, a):
        """ Ask the user for input of a single argument.
        
        :param a: argparse.Action instance
        :return:  the user input, asked according to the action
        """
        # if action of an argument that suppresses any other, just return
        if a.dest == SUPPRESS or a.default == SUPPRESS:
            return
        # prepare the prompt
        prompt = gt((a.help or a.dest).capitalize())
        r = {'newline': True, 'required': a.required}
        # now handle each different action
        try:
            if self.is_action(a, 'store', 'append'):
                return user_input(prompt, a.choices or self._registry_get('type', a.type, a.type), a.default, **r)
            elif self.is_action(a, 'store_const', 'append_const'):
                return user_input(prompt, (gt("(A)dd"), gt("(D)iscard")), "d", **r)
            elif self.is_action(a, 'store_true'):
                return user_input(prompt, (gt("(Y)es"), gt("(N)o")), "n", **r)
            elif self.is_action(a, 'store_false'):
                return user_input(prompt, (gt("(Y)es"), gt("(N)o")), "y", **r)
            elif self.is_action(a, 'count'):
                return user_input(prompt, is_pos_int, 0, gt("positive integer"), **r)
            elif self.is_action(a, 'parsers'):
                pmap = a._name_parser_map
                l = list(pmap.keys())
                return user_input(prompt, l, l[0], **r) if len(l) > 0 else None
        except (EOFError, SystemExit):
            sys.exit(0)
        raise NotImplementedError(gt("Unknown argparse action"))
    
    def _reset_args(self):
        args = [_ for _ in self._reparse_args['pos']] + [_ for _ in self._reparse_args['opt']]
        for sp in self._reparse_args['sub']:
            args += sp._reset_args()
        self._reparse_args = {'pos': [], 'opt': [], 'sub': []}
        return args
    
    def _set_arg(self, a, s="main", c=False):
        """ Set a single argument.
        
        :param a: argparse.Action instance
        :param s: config section title
        :param c: use class' ConfigParser instance to get parameters
        """
        # if action of an argument that suppresses any other, just return
        if a.dest is SUPPRESS or a.default is SUPPRESS:
            return
        # check if an option string is used for this action in sys.argv ; if so, return as it will be parsed normally
        if any(o in sys.argv[1:] for o in a.option_strings):
            return
        # in case of non-null config, get the value from the config object
        default = a.default if a.default is None else str(a.default)
        if c:
            try:
                value = ArgumentParser._config.get(s, a.dest)
            except (NoOptionError, NoSectionError) as e:
                item = "setting" if isinstance(e, NoOptionError) else "section"
                # if the argument is required, just ask for the value
                value = self._input_arg(a) if a.required else default
                logger.debug(gt("{} {} not present in config (set to {})").format(a.dest, item, value))
        # in case of null config, just ask for the value
        else:
            value = self._input_arg(a)
        # collect the option string before continuing
        try:
            ostr = a.option_strings[0]
        except IndexError:  # occurs when positional argument
            ostr = None
        # now handle arguments regarding the action
        if self.is_action(a, 'store', 'append'):
            if value:
                if ostr:
                    self._reparse_args['opt'].extend([ostr, value])
                else:
                    self._reparse_args['pos'].extend([value])
        elif self.is_action(a, 'store_const', 'append_const'):
            if value.lower() == "add" or value != default:
                self._reparse_args['opt'].append(ostr)
        elif self.is_action(a, 'store_true'):
            if value.lower() in ["y", "true"]:
                self._reparse_args['opt'].append(ostr)
        elif self.is_action(a, 'store_false'):
            if value.lower() in ["n", "false"]:
                self._reparse_args['opt'].append(ostr)
        elif self.is_action(a, 'count'):
            v = int(value or 0)
            if v > 0:
                if ostr.startswith("--"):
                    new_arg = [ostr for i in range(v)]
                else:
                    new_arg = ["-{}".format(v * ostr.strip('-'))]
                self._reparse_args['opt'].extend(new_arg)
        elif self.is_action(a, 'parsers'):
            if not value:
                value = self._input_arg(a)
            pmap = a._name_parser_map
            pmap[value].config_args(a.dest) if c else pmap[value].input_args()
            pmap[value]._reparse_args['pos'].insert(0, value)
            self._reparse_args['sub'].append(pmap[value])
        else:
            raise NotImplementedError("Unknown argparse action")
    
    def _sorted_actions(self):
        """ Generate the sorted list of actions based on the "last" attribute. """
        for a in filter(lambda _: not _.last and not self.is_action(_, 'parsers'), self._actions):
            yield a
        for a in filter(lambda _: _.last and not self.is_action(_, 'parsers'), self._actions):
            yield a
        for a in filter(lambda _: self.is_action(_, 'parsers'), self._actions):
            yield a
    
    def config_args(self, section="main"):
        """ Additional method for feeding input arguments from a config file.
        
        :param section: current config section name
        """
        if self._config_parsed:
            return
        for a in self._filtered_actions("config"):
            for o in a.option_strings:
                try:
                    i = sys.argv.index(o)
                    sys.argv.pop(i)  # remove the option string
                    sys.argv.pop(i)  # remove the value that follows
                except ValueError:
                    pass
        for a in self._sorted_actions():
            self._set_arg(a, section, True)
        self._config_parsed = True
    
    def demo_args(self):
        """ Additional method for replacing input arguments by demo ones. """
        argv = random.choice(self.examples).replace("--demo", "")
        self._reparse_args['pos'] = shlex.split(argv)
    
    def error(self, message):
        """ Prints a usage message incorporating the message to stderr and exits in the case when no new arguments to be
             reparsed, that is when no special action like _DemoAction (triggering parser.demo_args()) or _WizardAction
             (triggering input_args()) was called. Otherwise, it simply does not stop execution so that new arguments
             can be reparsed. """
        if all(len(x) == 0 for x in self._reparse_args.values()):
            # normal behavior with argparse
            self.print_usage(sys.stderr)
            self.exit(2, gt("%s: error: %s\n") % (self.prog, message))
    
    def format_help(self):
        text = ""
        # description
        formatter = self._get_formatter()
        formatter.add_text(self.description)
        text += formatter.format_help() + "\n"
        # usage
        text += self.format_usage().rstrip("\n") + "\n\n"
        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter = self._get_formatter()
            formatter.start_section(txt2title(gt(action_group.title) + ":"))
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
            actions = formatter.format_help()
            if actions == "":
                continue
            a = ""
            for i, line in enumerate(actions.splitlines()):
                s, dedent = line.lstrip(), 0
                if i == 0:
                    # action_group.title has ":" added after txt2title(...) causing an extra ":" to be appended
                    if self._docfmt == "html":
                        # for markup languages with tags, ":" appears behind the title tag
                        title = line.rstrip(":") + "\n"
                    else:
                        # for other markup languages without tags, ":" appears at the end in duplicate
                        title = line.rstrip(":") + ":\n"
                    continue
                if i == 1 and self._docfmt == "rst":
                    # action_group.title has ":" added after txt2title(...) causing an extra ":" to be appended behind
                    #  the underline, making rendering fail
                    title = title.rstrip("\n") + "\n" + line.rstrip(":") + "\n"
                    continue
                if self._docfmt and s[0] in "-*":
                    dedent = len(line) - len(s)
                _nl = ["\n", ""][self._docfmt is None]
                a += _nl + txt2paragraph(line.lstrip() if self._docfmt else line) + "\n"
            text += title + a + "\n"
        # epilog
        formatter = self._get_formatter()
        formatter.add_text(self.epilog)
        text += formatter.format_help()
        # determine help from format above
        return txt_terminal_render(text)
    
    def format_usage(self):
        formatter = self._get_formatter()
        formatter.add_usage(self.usage, self._actions, self._mutually_exclusive_groups)
        text = formatter.format_help()
        if self._docfmt:
            title, usage = text.rstrip("\n").split(": ", 1)
            usage = "\n".join(l[2:] if i > 0 else l for i, l in enumerate(usage.split("\n")))
            text = txt2title(title + ":") + "\n\n" + txt2paragraph(usage) + "\n"
        return text
    
    def input_args(self):
        """ Additional method for making the user input arguments manually. """
        for a in self._sorted_actions():
            self._set_arg(a)
    
    def parse_args(self, args=None, namespace=None):
        """ Reparses new arguments when _DemoAction (triggering parser.demo_args()) or _WizardAction (triggering
             input_args()) was called. """
        if not namespace:  # use the new Namespace class for handling _config
            namespace = Namespace(self)
        if len(sys.argv) == 2 and sys.argv[1] == "DISPLAY_USAGE":
            self.print_usage()
            self.exit()
        namespace = super(ArgumentParser, self).parse_args(args, namespace)
        if len(self._reparse_args['pos']) > 0 or len(self._reparse_args['opt']) > 0 or \
           len(self._reparse_args['sub']) > 0:
            args = self._reset_args()
            namespace = super(ArgumentParser, self).parse_args(args, namespace)
        # process "-hh..." here, after having parsed the arguments
        help_level = getattr(namespace, "help", 0)
        if help_level > 0:
            self.print_help()
            self.print_extended_help(help_level)
            self.exit()
        return namespace
    
    def print_extended_help(self, level=1, file=None):
        if not isinstance(self.details, (tuple, list, set)):
            self.details = [self.details]
        for _, message in zip((level - 1) * [None], self.details):
            message = "\n{}\n".format(message.strip())
            self._print_message(message, file or sys.stdout)
    
    def print_usage(self, file=None):
        self._print_message(txt_terminal_render(self.format_usage()), file or sys.stdout)
    
    @classmethod
    def add_to_config(cls, section, name, value):
        """ Add a parameter to the shared ConfigParser object.
        
        :param section: parameter's section
        :param name:    parameter's name
        :param value:   parameter's value
        """
        if value:
            if not cls._config.has_section(section):
                cls._config.add_section(section)
            cls._config.set(section, name, str(value))
    
    @classmethod
    def reset(cls):
        cls._config = ConfigParser()


class HelpFormatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    """ Help message formatter for appending a custom note (as input through the add_argument method of
         CustomArgumentParser) to argument help. It also allows to reduce long default values (e.g. a list of integers)
         to something readable. It also allows to add categories to subparser's choices. """
    def _expand_help(self, action):
        params = dict(vars(action), prog=self._prog)
        for name in list(params):
            if params[name] is SUPPRESS:
                del params[name]
        for name in list(params):
            if hasattr(params[name], '__name__'):
                params[name] = params[name].__name__
        if params.get('choices') is not None:
            choices_str = ', '.join([str(c) for c in params['choices']])
            params['choices'] = choices_str
        if params.get('default') is not None:
            s = repr(params['default']).strip("'")
            # if the default value string representation is too long, reduce it
            if len(s) > DEFAULT_MAX_LEN:
                p = s.split(',')
                if len(p) > DEFAULT_LST_MAX_LEN:
                    s = ','.join(p[:2] + ["..."] + p[-2:])
            params['default'] = s
        return self._get_help_string(action) % params
    
    def _format_action(self, action):
        # determine the required width and the entry label
        help_position = min(self._action_max_length + 2, self._max_help_position)
        help_width = max(self._width - help_position, 11)
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)
        # no help; start on same line and add a final newline
        if not action.help:
            action_header = '%*s%s\n' % (self._current_indent, '', action_header)
        # short action name; start on the same line and pad two spaces
        elif len(action_header) <= action_width:
            action_header = '%*s%-*s  ' % (self._current_indent, '', action_width, action_header)
            indent_first = 0
        # long action name; start on the next line
        else:
            action_header = '%*s%s\n' % (self._current_indent, '', action_header)
            indent_first = help_position
        # collect the pieces of the action help
        parts = [action_header]
        # if there was help for the action, add lines of help text
        if action.help:
            help_text = self._expand_help(action)
            help_lines = self._split_lines(help_text, help_width)
            parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
            for line in help_lines[1:]:
                parts.append('%*s%s\n' % (help_position, '', line))
        # or add a newline if the description doesn't end with one
        elif not action_header.endswith('\n'):
            parts.append('\n')
        # if there are any sub-actions, add their help as well, in categories if relevant
        categories = getattr(action, "categories", None)
        if categories is None:
            for subaction in self._iter_indented_subactions(action):
                parts.append(self._format_action(subaction))
        else:
            for category in sorted(list(categories.keys())):
                parts.append('%*s[%s]\n' % (self._current_indent, '', category))
                for subaction in self._iter_indented_subactions(action):
                    if subaction in categories[category]:
                        parts.append(self._format_action(subaction))
        # return a single string
        return self._join_parts(parts)
    
    def _get_help_string(self, action):
        help = super(HelpFormatter, self)._get_help_string(action)
        if '%(note)' not in help and hasattr(action, "note") and action.note is not None:
            help += '\n NB: %(note)s'
        return help
    
    def add_argument(self, action):
        if action.help is not SUPPRESS:
            categories = {}
            # find all invocations
            get_invocation = self._format_action_invocation
            invocations = [get_invocation(action)]
            for subaction in self._iter_indented_subactions(action):
                categories.setdefault(subaction.category, [])
                categories[subaction.category].append(subaction)
                invocations.append(get_invocation(subaction))
            # update the maximum item length
            invocation_length = max([len(s) for s in invocations])
            action_length = invocation_length + self._current_indent
            self._action_max_length = max(self._action_max_length, action_length + 2)
            # add the item to the list
            if len(categories) > 1 or len(categories) > 0 and list(categories.keys())[0] != "default":
                action.categories = categories
            self._add_item(self._format_action, [action])


class Namespace(BaseNamespace):
    """ Modified Namespace class for handling ArgumentParser._config. """
    # private __dict__, so that vars() can still be used with no "junk" variable used for Tinyscript-related processing
    #  (e.g. _current_parser)
    __privdict__ = {}
    # exclude list for saving options in a ConfigParser object
    excludes = ["_current_parser", "_debug_level", "_collisions", "_subparsers", "read_config", "write_config"]
    
    def __init__(self, parser):
        self._current_parser = parser.name
        self._collisions = {a.orig: a.dest for a in parser._actions if getattr(a, "orig", None)}
        self._subparsers = [a.dest for a in parser._filtered_actions("parsers")]
    
    def __getattr__(self, name):
        # handle __privdict__ entry first
        if (name.startswith("_") or name in self.excludes) and name in self.__privdict__:
            return self.__privdict__[name]
        # then get the attribute the normal way
        return self.__getattribute__(name)
    
    def __setattr__(self, name, value):
        # handle __privdict__ entry first
        if (name.startswith("_") or name in self.excludes) and name != "_debug_level":
            self.__privdict__[name] = value
        else:
            super(Namespace, self).__setattr__(name, value)
        # then save the entry to the ConfigParser object if not excluded
        if name not in self.excludes:
            ArgumentParser.add_to_config(self._current_parser, name, value)
        # finally switch the current parser value if the option name is part of a subparser's list of options ; this new
        #  name will allow to save new options in a new section of the ConfigParser object
        if hasattr(self, "_subparsers") and name in self._subparsers and value:
            self._current_parser = name
    
    def get(self, name):
        try:
            return self.__getattr__(name)
        except AttributeError:
            return

