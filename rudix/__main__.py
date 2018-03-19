"""Main entry point when called by 'python -m'"""

import sys

from .main import main


if sys.argv[0].endswith('__main__.py'):
    sys.argv[0] = 'python -m rudix'


if __name__ == '__main__':
    sys.exit(main())
