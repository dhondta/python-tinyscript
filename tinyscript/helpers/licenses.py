#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common software licenses.

Source: https://help.github.com/en/articles/licensing-a-repository
"""
from datetime import datetime

from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = ["copyright", "license", "list_licenses"]


LICENSES = {
    'afl-3.0': "Academic Free License v3.0",
    'agpl-3.0': "GNU Affero General Public License v3.0",
    'apache-2.0': "Apache license 2.0",
    'artistic-2.0': "Artistic license 2.0",
    'bsd-2-clause': "BSD 2-clause \"Simplified\" license",
    'bsd-3-clause': "BSD 3-clause \"New\" or \"Revised\" license",
    'bsd-3-clause-clear': "BSD 3-clause Clear license",
    'bsl-1.0': "Boost Software License 1.0",
    'cc': "Creative Commons license family",
    'cc-by-4.0': "Creative Commons Attribution 4.0",
    'cc-by-sa-4.0': "Creative Commons Attribution Share Alike 4.0",
    'cc0-1.0': "Creative Commons Zero v1.0 Universal",
    'ecl-2.0': "Educational Community License v2.0",
    'epl-1.0': "Eclipse Public License 1.0",
    'eupl-1.1': "European Union Public License 1.1",
    'gpl': "GNU General Public License family",
    'gpl-2.0': "GNU General Public License v2.0",
    'gpl-3.0': "GNU General Public License v3.0",
    'isc': "ISC",
    'lgpl': "GNU Lesser General Public License family",
    'lgpl-2.1': "GNU Lesser General Public License v2.1",
    'lgpl-3.0': "GNU Lesser General Public License v3.0",
    'lppl-1.3c': "LaTeX Project Public License v1.3c",
    'mit': "MIT",
    'mpl-2.0': "Mozilla Public License 2.0",
    'ms-pl': "Microsoft Public License",
    'ncsa': "University of Illinois/NCSA Open Source License",
    'ofl-1.1': "SIL Open Font License 1.1",
    'osl-3.0': "Open Software License 3.0",
    'postgresql': "PostgreSQL License",
    'unlicense': "The Unlicense",
    'wtfpl': "Do What The F*ck You Want To Public License",
    'zlib': "zLib License",
}
Y = datetime.now().year


copyright     = lambda t: "© {} {}".format(Y, t) if not t.startswith("©") else t
license       = lambda l, n=False: LICENSES.get(str(l)) or \
                                   ["Invalid license", None][n]
list_licenses = lambda: LICENSES.keys()
