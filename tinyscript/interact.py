#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Module for defining interactive mode logic.

"""
import readline
import socket
import sys
from code import compile_command, interact as base_interact, \
                 InteractiveConsole as BaseInteractiveConsole


__all__ = ["set_interact_items"]


def set_interact_items(glob):
    """
    This function prepares the interaction items for inclusion in main script's
     global scope.
    
    :param glob: main script's global scope dictionary reference
    """
    a, l = glob['args'], glob['logger']
    enabled = getattr(a, a._collisions.get("interact") or "interact", False)
    if enabled:
        readline.parse_and_bind('tab: complete')

    # InteractiveConsole as defined in the code module, but handling a banner
    #  using the logging of tinyscript
    class InteractiveConsole(BaseInteractiveConsole, object):
        def __init__(self, banner=None, namespace=None, filename='<console>',
                     exitmsg=None):
            if enabled:
                self.banner = banner
                self.exitmsg = exitmsg
                ns = glob
                ns.update(namespace or {})
                super(InteractiveConsole, self).__init__(locals=ns,
                                                         filename=filename)
            
        def __enter__(self):
            if enabled and self.banner is not None:
                l.interact(self.banner)
            return self
        
        def __exit__(self, *args):
            if enabled and self.exitmsg is not None:
                l.interact(self.exitmsg)
        
        def interact(self, *args, **kwargs):
            if enabled:
                super(InteractiveConsole, self).interact(*args, **kwargs)

    glob['InteractiveConsole'] = InteractiveConsole
    
    def interact(banner=None, readfunc=None, namespace=None, exitmsg=None):
        if enabled:
            if banner is not None:
                l.interact(banner)
            ns = glob
            ns.update(namespace or {})
            base_interact(readfunc=readfunc, local=ns)
            if exitmsg is not None:
                l.interact(exitmsg)

    glob['interact'] = interact
    
    glob['compile_command'] = compile_command if enabled else \
                              lambda *a, **kw: None

    # ConsoleSocket for handling duplicating std*** to a socket for the
    #  RemoteInteractiveConsole
    host = getattr(a, a._collisions.get("host") or "host", None)
    port = getattr(a, a._collisions.get("port") or "port", None)

    # custom socket, for handling the bindings of stdXXX through a socket
    class ConsoleSocket(socket.socket):
        def readline(self, nbytes=2048):
            return self.recv(nbytes)

        def write(self, *args, **kwargs):
            return self.send(*args, **kwargs)

    # RemoteInteractiveConsole as defined in the code module, but handling 
    #  interaction through a socket
    class RemoteInteractiveConsole(InteractiveConsole):
        def __init__(self, *args, **kwargs):
            if enabled:
                # open a socket
                self.socket = ConsoleSocket()
                self.socket.connect((str(host), port))
                # save STDIN, STDOUT and STDERR
                self.__stdin = sys.stdin
                self.__stdout = sys.stdout
                self.__stderr = sys.stderr
                # rebind STDIN, STDOUT and STDERR to the socket
                sys.stdin = sys.stdout = sys.stderr = self.socket
                # now initialize the interactive console
                super(RemoteInteractiveConsole, self).__init__(*args, **kwargs)
        
        def __exit__(self, *args):
            if enabled:
                super(RemoteInteractiveConsole, self).__exit__(*args)
                self.socket.close()
                self.close()
            
        def close(self):
            if enabled:
                # restore STDIN, STDOUT and STDERR
                sys.stdin = self.__stdin
                sys.stdout = self.__stdout
                sys.stderr = self.__stderr

    glob['RemoteInteractiveConsole'] = RemoteInteractiveConsole
