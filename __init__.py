__title__ = 'Discord Bot Code'
__author__ = 'Mirinano'
__copyright__ = 'Copyright 2019 Mirinano'
__version__ = '2.0.0' #2020/07/22

from collections import namedtuple

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=2, minor=0, micro=0, releaselevel='alpha', serial=0)

class Developer():
    name = "Mirinano"
    id = 0
