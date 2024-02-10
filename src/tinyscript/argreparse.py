# -*- coding: UTF-8 -*-
"""Module for extending argparse features, for simplifying parser.py.

"""
import argparse as ap
import operator as op
import random
import re
import shlex
import sys
from argparse import *
from argparse import _ActionsContainer, _ArgumentGroup, _MutuallyExclusiveGroup, _AttributeHolder, _SubParsersAction, \
                     Action, _UNRECOGNIZED_ARGS_ATTR, Namespace as BaseNamespace, ArgumentParser as BaseArgumentParser
from inspect import currentframe
from os import environ
from os.path import abspath, basename, dirname, sep, splitext
from shutil import which
from stat import S_IXUSR
try:
    from configparser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError

from .features.loglib import logger
from .helpers.inputs import user_input
from .helpers.licenses import *
from .helpers.data.types import is_executable, is_in_path, is_long_opt, is_pos_int, is_short_opt
from .helpers.termsize import get_terminal_size
from .helpers.text import *
from .helpers.text import configure_docformat, txt_terminal_render


__all__ = ["get_tool_globals", "parser_calls", "ArgumentParser", "Namespace", "ProxyArgumentParser",
           "DUNDERS", "SUPPRESS"]


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

parser_calls = []  # will be populated by calls to ProxyArgumentParser


def get_tool_globals():
    # get caller's frame
    frame = currentframe().f_back
    while not isinstance(frame.f_globals.get('parser'), ProxyArgumentParser) or \
          frame.f_globals.get('__name__') in ["tinyscript.argreparse", "tinyscript.parser"]:
        frame = frame.f_back
        if frame is None:
            return {}
    # walk the stack until a frame containing a known object is found
    glob = frame.f_globals
    # search for dunders
    for d in DUNDERS:
        f = frame
        while f and (d not in f.f_globals.keys() or f.f_globals[d] is None):
            f = f.f_back
        try:
            glob[d] = f.f_globals[d]
        except (AttributeError, KeyError):
            pass
    return glob


class ProxyArgumentParser(object):
    """ Proxy class for collecting added arguments before initialization. """
    def __getattr__(self, name):
        """ Each time a method is called, return __collect to make it capture the input arguments and keyword-arguments
             if it exists in the original parser class. """
        self.__call = name
        return self.__collect

    def __collect(self, *args, **kwargs):
        """ Capture the input arguments and keyword-arguments of the currently called method, appending a proxy
             subparser in case it should be used for mutually exclusive groups or subparsers. """
        subparser = ProxyArgumentParser()
        parser_calls.append((self, self.__call, args, kwargs, subparser))
        del self.__call
        return subparser
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass
    
    @staticmethod
    def reset():
        global parser_calls
        parser_calls = []
        ArgumentParser.reset()


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
            choice_action = self._ChoicesPseudoAction(name, aliases, help)
            choice_action.category = category
            self._choices_actions.append(choice_action)
        # create the parser, but with another formatter and separating the help into an argument group
        parser = self._parser_class(add_help=False, **kwargs)
        parser.name = name
        # add default extra arguments group
        i = parser.add_argument_group("extra arguments")
        i.add_argument("-h", action="usage", prefix="show", help=gt("show usage message and exit"))
        i.add_argument("--help", action="help", prefix="show", help=gt("show this help message and exit"))
        # add it to the map
        self._name_parser_map[name] = parser
        # make parser available under aliases also
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
        super(_NewActionsContainer, self).__init__(*[kwargs.get(k) for k in \
                                               ['description', 'prefix_chars', 'argument_default', 'conflict_handler']])
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
            return action
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
    def add_argument(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], Action):
            self._group_actions.append(args[0])
            return args[0]
        return super(_NewMutuallyExclusiveGroup, self).add_argument(*args, **kwargs)


class ArgumentParser(BaseArgumentParser, _NewActionsContainer):
    """ Modified version of argparse.ArgumentParser, based on the modified ActionsContainer.
    
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
    
    def __init__(self, *args, **kwargs):
        self.tokens = kwargs.pop('command', None)
        if not hasattr(ArgumentParser, "_globals_dict"):
            ArgumentParser._globals_dict = get_tool_globals()
        gd = ArgumentParser._globals_dict
        if sys.version_info >= (3, 8):
            self._check_requirements(gd.get('__requires__'))
        configure_docformat(gd)
        self._config_parsed = False
        self._docfmt = gd.get('__docformat__')
        self._reparse_args = {'pos': [], 'opt': [], 'sub': []}
        self.examples = gd.get('__examples__', [])
        script = basename(self.tokens[0])
        _stem = lambda p: splitext(p)[0]
        if gd.get('__script__') is None:
            gd['__script__'] = script
        self.banner = gd.get('__banner__', _stem(script))
        if kwargs.get('prog') is None:
            path = abspath(which(script) or which(_stem(script)) or script)
            ArgumentParser.prog = kwargs['prog'] = "python " + script if not is_executable(path) else \
                                                   "./" + script if not is_in_path(dirname(path)) else script
        kwargs['add_help'] = False
        kwargs['conflict_handler'] = "error"
        # when __docformat__ is set, fixing max_help_position to terminal's width forces argparse to format arguments
        #  with their help on the same line ; in other words, formatting is left to the renderer
        wh = get_terminal_size()
        kwargs['formatter_class'] = HelpFormatter if self._docfmt is None else \
                                    lambda prog: HelpFormatter(prog, max_help_position=80 if wh is None else wh[0])
        # format the epilog message
        if self.examples:
            l = ["{} {}".format(ArgumentParser.prog, e) for e in self.examples]
            l = list(filter(lambda x: x.startswith(kwargs['prog']), l))
            if len(l) > 0:
                kwargs['epilog'] = txt2title(gt("Usage example{}".format(["", "s"][len(l) > 1])) + ":")
                e = '\n'.join(["\n", "  "][self._docfmt is None] + txt2paragraph(e) for e in l)
                kwargs['epilog'] += "\n" + e
        # format the description message
        d = gd.get('__script__', script)
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
                        if s == "":  # do not display 'reason' if no 'author' and 'email' is defined
                            continue
                        reason = contributor.get('reason')
                        if reason:
                            s += " - " + str(reason)
                        m += ["", "\n" + (l + 2) * " "][i > 0] + s
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
        self._namespace = Namespace(self)
    
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
            o, v = re.match(r"^([<>=!]=|[<>]|)(.*)$", v).groups()
            operator = {'': op.ge, '<': op.lt, '>': op.gt, '<=': op.le, '>=': op.ge, '==': op.eq, '!=': op.ne}[o]
            desired, actual = Version(v), Version(get_version(m))
            if not operator(actual, desired):
                errors.append((m, o or ">=", str(desired), str(actual)))
        if len(errors) > 0:
            line = ["", "\n- "][len(errors) > 1] + \
                   "Bad version for module '%s' ; should be %s%s while actual version is %s"
            raise RequirementError(["", "\n"][len(errors) > 1] + "\n".join(line % e for e in errors))
    
    def _filtered_actions(self, *action_types):
        """ Get actions filtered on a list of action types. """
        for action in filter(lambda a: self.is_action(a, *action_types), self._actions):
            yield action
    
    def _get_string(self, action, string):
        """ Get the string from an argument string given its related action, prompting for user input if relevant. This
             also replaces markers using the current namespace. """
        orig = string
        # first, resolve inputs
        if not isinstance(action, _NewSubParsersAction) and string == "<input>":
            string = self._input_arg(action)
        # then, resolve other markers replacing values from the current namespace
        for arg in re.findall(r"<(.*?)>", string):
            if arg in self._namespace.keys():
                val = self._namespace.get(arg)
                if isinstance(val, bool):
                    raise ValueError(gt("marker replacement does not work for boolean options"))
                string = string.replace(f"<{arg}>", str(val))
        # finally, locate and replace string in command's tokens
        if orig != string:
            self.tokens[self.tokens.index(orig)] = string
        return string
    
    def _get_value(self, action, string):
        """ Get the value from an argument string given its related action.
        NB: This method is mostly the same as the original ; it customizes the "invalid ... value" message. """
        type_func = self._registry_get('type', action.type, action.type)
        if not callable(type_func):
            raise ArgumentError(action, gt("%r is not callable") % type_func)
        try:
            result = type_func(string)
        except ArgumentTypeError:
            raise ArgumentError(action, str(sys.exc_info()[1]))
        except (TypeError, ValueError):
            # clean up the name (do not keep the function name, e.g. "_my_argument_action", but make it more
            #  user-friendly, e.g. "my argument action"
            name = getattr(action.type, '__name__', repr(action.type)).strip("_").replace("_", " ")
            raise ArgumentError(action, gt("invalid %s value: %r") % (name, string))
        return result
    
    def _get_values(self, action, arg_strings):
        # first, resolve input and variable markers
        arg_strings = [self._get_string(action, s) for s in arg_strings]
        # for everything but PARSER args, strip out '--'
        if action.nargs not in [PARSER, REMAINDER]:
            arg_strings = [s for s in arg_strings if s != '--']
        # optional argument produces a default when not present
        if not arg_strings and action.nargs == OPTIONAL:
            value = action.const if action.option_strings else action.default
            if isinstance(value, str):
                value = self._get_value(action, value)
                self._check_value(action, value)
        # when nargs='*' on a positional, if there were no command-line args, use default (if not None)
        elif not arg_strings and action.nargs == ZERO_OR_MORE and not action.option_strings:
            value = arg_strings if action.default is None else action.default
            self._check_value(action, value)
        elif len(arg_strings) == 1 and action.nargs in [None, OPTIONAL]:
            value = self._get_value(action, arg_strings[0])
            self._check_value(action, value)
        else:
            value = [self._get_value(action, v) for v in arg_strings]
            if action.nargs == PARSER:
                self._check_value(action, value[0])
            elif action.nargs != REMAINDER:
                for v in value:
                    self._check_value(action, v)
        return value
    
    def _input_arg(self, action):
        """ Ask the user for input of a single argument. """
        # if action of an argument that suppresses any other, just return
        if action.dest == SUPPRESS or action.default == SUPPRESS:
            return
        # prepare the prompt
        prompt = gt((action.help or action.dest).capitalize())
        r = {'newline': True, 'required': action.required}
        # now handle each different action
        try:
            if self.is_action(action, 'store', 'append'):
                return user_input(prompt, action.choices or self._registry_get('type', action.type, action.type),
                                  action.default, **r)
            elif self.is_action(action, 'store_const', 'append_const'):
                return user_input(prompt, (gt("(A)dd"), gt("(D)iscard")), "d", **r)
            elif self.is_action(action, 'store_true'):
                return user_input(prompt, (gt("(Y)es"), gt("(N)o")), "n", **r)
            elif self.is_action(action, 'store_false'):
                return user_input(prompt, (gt("(Y)es"), gt("(N)o")), "y", **r)
            elif self.is_action(action, 'count'):
                return user_input(prompt, is_pos_int, 0, gt("positive integer"), **r)
            elif self.is_action(action, 'parsers'):
                pmap = action._name_parser_map
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
    
    def _set_arg(self, action, section="main", config=False):
        """ Set a single argument. """
        # if action of an argument that suppresses any other, just return
        if action.dest is SUPPRESS or action.default is SUPPRESS:
            return
        # check if an option string is used for this action in command's tokens (either user input or sys.argv) ;
        #  if so, return as it will be parsed normally
        if any(o in self.tokens[1:] for o in action.option_strings):
            return
        # in case of non-null config, get the value from the config object
        default = action.default if action.default is None else str(action.default)
        if config:
            try:
                value = ArgumentParser._config.get(section, action.dest)
            except (NoOptionError, NoSectionError) as e:
                item = "setting" if isinstance(e, NoOptionError) else "section"
                # if the argument is required, just ask for the value
                value = self._input_arg(action) if action.required else default
                logger.debug(gt("{} {} not present in config (set to {})").format(action.dest, item, value))
        # in case of null config, just ask for the value
        else:
            value = self._input_arg(action)
        # collect the option string before continuing
        try:
            ostr = action.option_strings[0]
        except IndexError:  # occurs when positional argument
            ostr = None
        # now handle arguments regarding the action
        if self.is_action(action, 'store', 'append'):
            if value:
                if ostr:
                    self._reparse_args['opt'].extend([ostr, value])
                else:
                    self._reparse_args['pos'].extend([value])
        elif self.is_action(action, 'store_const', 'append_const'):
            if value.lower() == "add" or value != default:
                self._reparse_args['opt'].append(ostr)
        elif self.is_action(action, 'store_true'):
            if value.lower() in ["y", "true"]:
                self._reparse_args['opt'].append(ostr)
        elif self.is_action(action, 'store_false'):
            if value.lower() in ["n", "false"]:
                self._reparse_args['opt'].append(ostr)
        elif self.is_action(action, 'count'):
            v = int(value or 0)
            if v > 0:
                if ostr.startswith("--"):
                    new_arg = [ostr for i in range(v)]
                else:
                    new_arg = ["-{}".format(v * ostr.strip('-'))]
                self._reparse_args['opt'].extend(new_arg)
        elif self.is_action(action, 'parsers'):
            if not value:
                value = self._input_arg(action)
            pmap = action._name_parser_map
            pmap[value].config_args(action.dest) if config else pmap[value].input_args()
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
        """ Additional method for feeding input arguments from a config file. """
        if self._config_parsed:
            return
        for a in self._filtered_actions("config"):
            for o in a.option_strings:
                try:
                    i = self.tokens.index(o)
                    self.tokens.pop(i)  # remove the option string
                    self.tokens.pop(i)  # remove the value that follows
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
    
    def parse_args(self, args=None, namespace=None, **kwargs):
        """ Reparses new arguments when _DemoAction (triggering parser.demo_args()) or _WizardAction (triggering
             input_args()) was called. """
        # use the new argreparse.Namespace class for handling _config
        self._namespace = Namespace(self) if namespace is None else namespace
        self._namespace.update(kwargs)
        if len(self._tokens) == 2 and self._tokens[1] == "DISPLAY_USAGE":
            self.print_usage()
            self.exit()
        self._namespace = super(ArgumentParser, self).parse_args(args or self._tokens[1:], self._namespace)
        ra = self._reparse_args
        if len(ra['pos']) > 0 or len(ra['opt']) > 0 or len(ra['sub']) > 0:
            self._namespace = super(ArgumentParser, self).parse_args(self._reset_args(), self._namespace)
        # process "-hh..." here, after having parsed the arguments
        help_level = getattr(self._namespace, "help", 0)
        if help_level > 0:
            self.print_help()
            self.print_extended_help(help_level)
            self.exit()
        from shlex import join
        self._namespace._command = join(self._tokens)
        return self._namespace
    
    def print_extended_help(self, level=1, file=None):
        if not isinstance(self.details, (tuple, list, set)):
            self.details = [self.details]
        for _, message in zip((level - 1) * [None], self.details):
            message = "\n{}\n".format(message.strip())
            self._print_message(message, file or sys.stdout)
    
    def print_usage(self, file=None):
        self._print_message(txt_terminal_render(self.format_usage()), file or sys.stdout)
    
    @property
    def tokens(self):
        p = self
        while hasattr(p, "_parent") and p._parent is not None:
            p = p._parent
        if hasattr(p, "_tokens"):
            return p._tokens
    
    @tokens.setter
    def tokens(self, command):
        p = self
        while hasattr(p, "_parent") and p._parent is not None:
            p = p._parent
        if hasattr(p, "_tokens"):
            return
        p._tokens = sys.argv if command is None else command
        if isinstance(p._tokens, str):
            from shlex import split
            p._tokens = split(p._tokens)
    
    @classmethod
    def add_to_config(cls, section, name, value):
        """ Add a parameter to the shared ConfigParser object. """
        if value:
            if not cls._config.has_section(section):
                cls._config.add_section(section)
            cls._config.set(section, name, str(value))
    
    @classmethod
    def reset(cls):
        global parser_calls
        parser_calls = []
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
        return action


class Namespace(BaseNamespace):
    """ Modified Namespace class for handling ArgumentParser._config. """
    # private __dict__, so that vars() can still be used with no "junk" variable used for Tinyscript-related processing
    #  (e.g. _current_parser)
    __privdict__ = {}
    # exclude list for saving options in a ConfigParser object
    excludes = ["_current_parser", "_debug_level", "_collisions", "_subparsers", "read_config", "write_config"]
    
    def __init__(self, parser=None, **kwargs):
        self._current_parser = parser.name
        self._collisions = {a.orig: a.dest for a in parser._actions if getattr(a, "orig", None)}
        self._subparsers = [a.dest for a in parser._filtered_actions("parsers")]
        super(Namespace, self).__init__(**kwargs)
    
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
        if hasattr(self, "_subparsers") and name in self._subparsers:
            self._current_parser = name
    
    def get(self, name):
        try:
            return self.__getattr__(name)
        except AttributeError:
            return
    
    def keys(self):
        return [k for k in self.__dict__ if not k.startswith("_")]
    
    def update(self, kwargs_dict=None, **kwargs):
        for d in [kwargs, kwargs_dict or {}]:
            for k, v in d.items():
                setattr(self, k, v)

