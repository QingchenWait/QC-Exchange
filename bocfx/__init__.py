#!/usr/bin/env python

import sys

if sys.version_info[0] == 3:
    # from .extractor import Extractor, VideoExtractor
    # from .util import log
    from .__main__ import *

    # from .common import *
    # from .version import *
    # from .cli_wrapper import *
    # from .extractor import *
else:
    # Don't import anything.
    print("This module needs python3 support!")