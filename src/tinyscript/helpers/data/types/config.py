# -*- coding: UTF-8 -*-
"""Config-related checking functions and argument types.

"""
try:
    import ConfigParser as ini
except ImportError:
    import configparser as ini
from six import u

from ...common import lazy_load_module

for _m in ["json", "toml", "yaml"]:
    lazy_load_module(_m)


__all__ = __features__ = []


# config check functions
__all__ += ["is_ini", "is_ini_file", "is_json", "is_json_file", "is_toml", "is_toml_file", "is_yaml", "is_yaml_file"]
is_ini       = lambda c: __check_file(c, "ini", False, False) is not None
is_ini_file  = lambda c: __check_file(c, "ini", False) is not None
is_json      = lambda c: __check_file(c, "json", False, False) is not None
is_json_file = lambda c: __check_file(c, "json", False) is not None
is_toml      = lambda c: __check_file(c, "toml", False, False) is not None
is_toml_file = lambda c: __check_file(c, "toml", False) is not None
is_yaml      = lambda c: __check_file(c, "yaml", False, False) is not None
is_yaml_file = lambda c: __check_file(c, "yaml", False) is not None


# config argument types
__all__ += ["ini_config", "ini_file", "json_config", "json_file", "toml_config", "toml_file", "yaml_config",
            "yaml_file"]


def __check_file(c, ctype, fail=True, is_file=True):
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
ini_config  = ini_file  = lambda c: __check_file(c, "ini")
json_config = json_file = lambda c: __check_file(c, "json")
toml_config = toml_file = lambda c: __check_file(c, "toml")
yaml_config = yaml_file = lambda c: __check_file(c, "yaml")
ini_config.__name__  = ini_file.__name__  = "INI file"
json_config.__name__ = json_file.__name__ = "JSON file"
toml_config.__name__ = toml_file.__name__ = "TOML file"
yaml_config.__name__ = yaml_file.__name__ = "YAML file"

