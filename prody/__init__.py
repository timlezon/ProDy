# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2011 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2011 Ahmet Bakan'
__version__ = '0.9.1'

release = tuple([int(x) for x in __version__.split('.')])

try:
    import numpy as np
except ImportError:
    raise ImportError('numpy not found, it is a required package')


import os
import sys
import os.path
import platform

if not (2,6) <= sys.version_info[:2] <= (2,7):
    raise Exception("prody is compatible with Python 2.6 and 2.7, you are "
                    "using Python " + platform.python_version())

from tools import *

import warnings

DEPRECATION_WARNINGS = False

CONFIGURATION = {
    'backup': False,
    'backup_ext': '.BAK',
}

from datetime import date
today = date.today()

if today.year == 2012:
    warnings.filterwarnings('default', category=DeprecationWarning)

def deprecate(dep, alt, sl=3):
    """Issue a deprecation warning for *dep* and recommend using *alt*, if 
    current year is 2012."""

    if DEPRECATION_WARNINGS or today.year >= 2012:
        warnings.warn('`{0:s}` is deprecated for removal in v1.0, use `{1:s}`.'
                      .format(dep, alt), DeprecationWarning, stacklevel=sl)

def turnonDepracationWarnings(action='always'):
    """Turn on deprecation warnings for the current session.  By default
     (``action='always'``), deprecation warnings will be printed every time
     a function is called to help identification of multiple occurrence 
     of deprecated function and method names.  When ``action='default'``
     is passed, warning will be issued at the first call of a function.
     The latter behavior will automatically kick in when v0.9 is released.
     Until v0.9 is released, restarting the session will turn of warnings.
     This function must be called as ``prody.turnonDepracationWarnings``. """
    
    global DEPRECATION_WARNINGS
    DEPRECATION_WARNINGS = True
    warnings.filterwarnings(action, category=DeprecationWarning)

    
_PY3K = sys.version_info[0] > 2

USERHOME = os.getenv('USERPROFILE') or os.getenv('HOME')
PACKAGEPATH = os.path.join(USERHOME, '.' + __package__)
PACKAGECONF =  os.path.join(USERHOME, '.' + __package__ + 'rc')
if not os.path.isfile(PACKAGECONF) and os.path.isfile(PACKAGECONF[:-2]):
    os.rename(PACKAGECONF[:-2], PACKAGECONF)

LOGGER = PackageLogger('.prody')

def importLA():
    try:
        import scipy.linalg as linalg
        dynamics.scipyla = True
    except ImportError:
        dynamics.scipyla = False
        try:
            import numpy.linalg as linalg
        except:
            raise ImportError('scipy.linalg or numpy.linalg is required for '
                              'NMA calculations and aligning structures.')
    dynamics.linalg = linalg
    measure.linalg = linalg

def importScipySparse():
    try:
        from scipy import sparse
    except ImportError:    
        raise ImportError('scipy.sparse is required, but could not be '
                          'imported.')
    dynamics.scipy_sparse = sparse
    
def importScipySparseLA():
    try:
        from scipy.sparse import linalg
    except ImportError:    
        raise ImportError('scipy.sparse is required, but could not be '
                          'imported.')
    dynamics.scipy_sparse_la = linalg

def importPyPlot():
    try:
        import matplotlib.pyplot as pyplot
        from mpl_toolkits.mplot3d import Axes3D
        dynamics.Axes3D = Axes3D
        proteins.Axes3D = Axes3D 
    except ImportError:
        pyplot = False 
        LOGGER.warning('Matplotlib is required for plotting.')
    dynamics.plt = pyplot
    ensemble.plt = pyplot
    proteins.plt = pyplot

def importBioKDTree():
    try:
        from prody.KDTree import KDTree
    except ImportError:
        try:
            from Bio.KDTree import KDTree
        except ImportError:
            KDTree = False
            LOGGER.warning('KDTree module could not be imported. '
                           'Reinstalling ProDy or installing BioPython '
                           'can resolve the problem.')
    dynamics.KDTree = KDTree
    select.KDTree = KDTree

SETTINGS = PackageSettings(logger=LOGGER) 
SETTINGS.load()
def setPackagePath(path):
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except Exception as err:
            LOGGER.warning('Failed to make folder "{0:s}": {1:s}'
                           .format(path, err.strerror))
            return False
    SETTINGS['package_path'] = path
    return path    

def getPackagePath():
    
    path = SETTINGS.get('package_path', None)
    
    update = False
    if path is None:
        LOGGER.warning('{0:s} package path is not yet set by the user.'
                       .format(__package__))
        update = True
    elif not os.path.isdir(path):
        LOGGER.warning('{0:s} package path "{1:s}" does not exist.'
                       .format(__package__, path))
        update = True
    elif not os.access(path, os.W_OK):
        LOGGER.warning('User does not have write access to {0:s} package path '
                       ' "{1:s}".'
                       .format(__package__, path))
        update = True
        
    if update:
        default = os.path.join(USERHOME, '.' + __package__)
        path = raw_input('Please specify a folder for storing {0:s} data '
                         '(press enter for "{1:s}"):'
                         .format(__package__, default)) or default
        while not setPackagePath(path):
            path = raw_input('Please specify a valid folder name with write ' 
                             'access:')
    return path


docstring = """

    ================  ====================================================
    Option            Default setting (type)         
    ================  ===================================================="""

conf = {}
for key, value in CONFIGURATION.iteritems():
    docstring += """
    {0:16s}  {1:52s}""".format(key, str(value) + 
                                    ' (' + type(value).__name__  + ')')
    if SETTINGS.get(key) is None:
        conf[key] = value
docstring += """
    ================  ====================================================
    
    Usage example:
        
    >>> confProDy('backup')
    True
    >>> confProDy('backup', 'backup_ext')
    [True, '.BAK']
    >>> confProDy(backup=True, backup_ext='.bak')
    >>> confProDy(backup_ext='.BAK')"""

if conf:
    SETTINGS.update(conf)

def confProDy(*args, **kwargs):
    """Configure ProDy.
    
    .. versionadded:: 0.9.2"""

    if args:
        if len(args) == 1:
            return SETTINGS.get(args[0])
        else:
            return [SETTINGS.get(option) for option in args]

    for option, value in kwargs.iteritems():    
        if isinstance(option, str):
            if option in CONFIGURATION:
                type_ = type(CONFIGURATION[option])
                if type(value) == type_:
                    SETTINGS[option] = value
                    SETTINGS.save()
                    LOGGER.debug('ProDy configuration is set: {0:s}={1:s}'
                                 .format(option, str(value)))
                else:
                    raise TypeError('value must be a ' + type_.__name__)
                    
            else:
                raise KeyError("'{0:s}' is not a valid option".format(option))
        else:
            raise TypeError('option must be a string')

confProDy.__doc__ += docstring

class ProDyException(Exception):
    pass

def plog(*text):
    """Log *text* using ProDy logger at log level info.
    
    .. versionadded:: 0.6.2
    
    .. versionchanged:: 0.7
       Multiple arguments are accepted. Each argument will be converted to 
       string and joined using a white space as delimiter. """
    
    LOGGER.info(' '.join([str(s) for s in text]))

def startLogfile(filename, **kwargs):
    
    LOGGER.startLogfile(filename, **kwargs)
    
startLogfile.__doc__ = LOGGER.startLogfile.__doc__
    
def closeLogfile(filename):
    """Close logfile with *filename*."""

    LOGGER.closeLogfile(filename)

def changeVerbosity(level):
    """Deprecated, see :func:`setVerbosity`."""
    
    deprecate('changeVerbosity', 'setVerbosity')
    setVerbosity(level)
    
def setVerbosity(level):
    """Change ProDy console verbosity *level* for the current session.  Default
    console verbosity level **debug**.  Log messages are written to ``sys.
    stderr``.  This function accepts one of the following as *level* argument:
    
    ========  ===========================================
    Level     Description
    ========  ===========================================
    debug     Everything will be printed on the console.
    info      Only brief information will be printed.
    warning   Only warning information will be printed.
    none      ProDy will not log any messages.
    ========  ===========================================
    
    >>> from prody import *
    >>> changeVerbosity('none')
    >>> plog('test')
    >>> changeVerbosity('debug')
    >>> plog('test')"""

    LOGGER.setVerbosity(level)

def getVerbosity():
    """Return ProDy console verbosity level."""
    
    return LOGGER.getVerbosity()

def checkUpdates():
    """Check PyPI to see if there is a newer ProDy version available."""
    
    import xmlrpclib
    pypi = xmlrpclib.Server('http://pypi.python.org/pypi')
    releases = pypi.package_releases('ProDy')
    if releases[0] == __version__:
        LOGGER.info('You are using the latest ProDy release (v{0:s}).'
                    .format(__version__))
    else:
        LOGGER.info('ProDy v{0:s} is available, you are using {1:s}.'
                    .format(releases[0], __version__))

def test(**kwargs):
    """Run ProDy tests. See :mod:`prody.testing` documentation for more 
    details, i.e. ``import prody.tests; help(prody.tests)``"""
    
    try:
        import prody.tests
    except ImportError:
        LOGGER.warning('Could not import test modules. '
                       'Tests are available for Python 2.7')
    else:
        tests.test(**kwargs)

__all__ = ['checkUpdates', 'confProDy', 'getVerbosity', 'setVerbosity',
           'startLogfile', 'closeLogfile', 'changeVerbosity',
           'plog']

from . import atomic 
from atomic import *
__all__.extend(atomic.__all__)
__all__.append('atomic')

from . import select
from select import *
__all__.extend(select.__all__)
__all__.append('select')

ProDyAtomSelect = Select()

import proteins
from proteins import *  
__all__.extend(proteins.__all__)
__all__.append('proteins')

from . import measure
from measure import *
__all__.extend(measure.__all__)
__all__.append('measure')

from . import compare
from compare import *
__all__.extend(compare.__all__)
__all__.append('compare')

from . import dynamics
from .dynamics import *
__all__.extend(dynamics.__all__)
__all__.append('dynamics')

from . import ensemble
from .ensemble import *
__all__.extend(ensemble.__all__)
__all__.append('ensemble')

#from . import volume
#from .volume import *
#__all__.extend(volume.__all__)

import prody
__all__.append('prody')
