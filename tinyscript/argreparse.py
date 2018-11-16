#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for extending argparse features, for simplifying parser.py.

"""
from argparse import _ActionsContainer, _ArgumentGroup, _AttributeHolder, \
                     _SubParsersAction, ArgumentDefaultsHelpFormatter, \
                     ArgumentError, RawTextHelpFormatter, SUPPRESS, \
                     ArgumentParser as BaseArgumentParser
from gettext import gettext as gt


__all__ = ["gt", "ArgumentError", "ArgumentParser", "HelpFormatter", "SUPPRESS"]


DEFAULT_MAX_LEN = 20
DEFAULT_LST_MAX_LEN = 10


class _NewActionsContainer(_ActionsContainer):
    """
    Modified version of argparse._ActionsContainer for handling a new "note"
     keyword argument.
    """
    
    def __init__(self, *args, **kwargs):
        super(_NewActionsContainer, self).__init__(*args, **kwargs)
        self.register('action', 'parsers', _NewSubParsersAction)

    def add_argument(self, *args, **kwargs):
        note = kwargs.pop("note", None)
        action = super(_NewActionsContainer, self).add_argument(*args, **kwargs)
        action.note = note

    def add_argument_group(self, *args, **kwargs):
        group = _NewArgumentGroup(self, *args, **kwargs)
        self._action_groups.append(group)
        return group


class _NewArgumentGroup(_ArgumentGroup, _NewActionsContainer):
    """
    Modified version of argparse._ArgumentGroup for modifying arguments groups
     handling in the modified ActionsContainer.
    """
    pass


class _NewSubParsersAction(_SubParsersAction):
    """
    Modified version of argparse._SubParsersAction for handling formatters of
     subparsers, inheriting from this of the main parser.
    """
    def add_parser(self, name, **kwargs):
        # set prog from the existing prefix
        if kwargs.get('prog') is None:
            kwargs['prog'] = '%s %s' % (self._prog_prefix, name)
        # create a pseudo-action to hold the choice help
        if 'help' in kwargs:
            help = kwargs.pop('help')
            choice_action = self._ChoicesPseudoAction(name, help)
            self._choices_actions.append(choice_action)
        # create the parser, but with another formatter and separating the help
        #  into an argument group
        parser = self._parser_class(formatter_class=HelpFormatter,
                                    add_help=False, **kwargs)
        info = parser.add_argument_group("extra arguments")
        info.add_argument("-h", "--help", action='help', default=SUPPRESS,
                          help=gt('show this help message and exit'))
        # add it to the map
        self._name_parser_map[name] = parser
        return parser
        

class ArgumentParser(_NewActionsContainer, BaseArgumentParser):
    """
    Modified version of argparse.ArgumentParser, based on the modified
     ActionsContainer.
    """
    pass


class HelpFormatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):
    """
    Help message formatter for appending a custom note (as input through the
     add_argument method of CustomArgumentParser) to argument help. It also
     allows to reduce long default values (e.g. a list of integers) to something
     readable.
    """

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
            s = str(params['default'])
            # if the default value string representation is too long, reduce it
            if len(s) > DEFAULT_MAX_LEN:
                p = s.split(',')
                if len(p) > DEFAULT_LST_MAX_LEN:
                    s = ','.join(p[:2] + ["..."] + p[-2:])
            params['default'] = s
        return self._get_help_string(action) % params

    def _get_help_string(self, action):
        help = super(HelpFormatter, self)._get_help_string(action)
        if '%(note)' not in help and hasattr(action, "note") and \
            action.note is not None:
            help += '\n NB: %(note)s'
        return help
