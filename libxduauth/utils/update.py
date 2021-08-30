import warnings

from requests import get

package = __package__.split('.')[0]


def get_self_version(package):
    try:
        from importlib.metadata import version
        return version(package)
    except:
        from pkg_resources import get_distribution
        return get_distribution(package)
    warnings.warn('unable to get local package version')


def get_latest_version(package, source='pypi.org'):
    pkginfo = get(f'https://{source}/pypi/{package}/json').json()
    return pkginfo['info']['version']


try:
    latest = get_latest_version(package)
    if get_self_version(package) != latest:
        warnings.warn(f'''
You are not using the latest version of libxduauth({latest}).
upgrade the package by running:
`pip3 install --upgrade libxduauth`
''')
except:
    pass
