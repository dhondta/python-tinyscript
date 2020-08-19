# -*- coding: UTF-8 -*-
"""Config-related checking functions and argument types.

"""
import json
import toml
import yaml
try:
    import ConfigParser as ini
except ImportError:
    import configparser as ini
from six import u


__all__ = __features__ = []


# config check functions
__all__ += ["is_ini", "is_ini_file", "is_json", "is_json_file", "is_toml", "is_toml_file", "is_yaml", "is_yaml_file"]
is_ini       = lambda c: __check_config(c, "ini", False, False) is not None
is_ini_file  = lambda c: __check_config(c, "ini", False) is not None
is_json      = lambda c: __check_config(c, "json", False, False) is not None
is_json_file = lambda c: __check_config(c, "json", False) is not None
is_toml      = lambda c: __check_config(c, "toml", False, False) is not None
is_toml_file = lambda c: __check_config(c, "toml", False) is not None
is_yaml      = lambda c: __check_config(c, "yaml", False, False) is not None
is_yaml_file = lambda c: __check_config(c, "yaml", False) is not None


# config argument types
__all__ += ["ini_config", "json_config", "toml_config", "yaml_config"]


def __check_config(c, ctype, fail=True, is_file=True):
    try:
        if ctype == "ini":
            cfg = ini.ConfigParser()
            if is_file:
                if len(cfg.read(c)) == 0:
                    raise ValueError("Config file does not exist")
            else:
                cfg.read_string(u(c))
        elif ctype in ["json", "toml"]:
            m = globals()[ctype]
            if is_file:
                with open(c, 'rt') as f:
                    cfg = m.load(f)
            else:
                cfg = m.loads(c)
        elif ctype == "yaml":
            if is_file:
                with open(c, 'rb') as f:
                    c = f.read()
            cfg = yaml.safe_load(c)
        return cfg
    except Exception as e:
        if fail:
            raise ValueError("Bad {} input config ({})".format(ctype, e))
ini_config  = lambda c: __check_config(c, "ini")
json_config = lambda c: __check_config(c, "json")
toml_config = lambda c: __check_config(c, "toml")
yaml_config = lambda c: __check_config(c, "yaml")

