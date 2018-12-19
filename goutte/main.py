from typing import Dict, List
import sys

import click
import colorlog
import digitalocean
import toml

from goutte import __version__

log = colorlog.getLogger(__name__)
token = None


@click.command(help='DigitalOcean snapshot automation service')
@click.argument('config', envvar='GOUTTE_CONFIG', type=click.File('r'))
@click.argument('do_key', envvar='GOUTTE_DO_KEY')
@click.version_option(version=__version__)
def entrypoint(config: click.File, do_key: str) -> None:
    """Command line interface entrypoint"""
    log.info('Starting goutte v{}.'.format(__version__))
    c = _load_config(config)
    for droplet in c['droplets']['names']:
        # do.droplet.snapshot(droplet, c['retention'])
        pass
    for volume in c['volumes']['names']:
        # do.volume.snapshot(volume, c['retention'])
        pass


def _load_config(config: click.File) -> Dict[str, Dict]:
    """Return a config dict from a toml config file"""
    try:
        # TODO check minimum validity (retention)
        log.debug('Loading config from {}'.format(config.name))
        return toml.load(config)
    except TypeError as e:
        log.critical('Could not read conf {}: {}'.format(config.name, e))
        sys.exit(1)
    except toml.TomlDecodeError as e:
        log.critical('Could not parse toml in config from {}: {}'
                     .format(config.name, e))
        sys.exit(1)


def _get_droplets(names: List[str]) -> List[digitalocean.Droplet]:
    """Get the droplets objects from the configuration doplets names"""
    try:
        manager = digitalocean.Manager(token=token)
        droplets = manager.get_all_droplets()
        return [droplet for droplet in droplets if droplet.name in names]
    except digitalocean.baseapi.TokenError as e:
        log.error(f'Token not valid: {e}')
    except digitalocean.baseapi.DataReadError as e:
        log.error(f'Could not read response: {e}')
    except digitalocean.baseapi.JSONReadError as e:
        log.error(f'Could not parse json: {e}')
    except digitalocean.baseapi.NotFoundError as e:
        log.error(f'Ressource not found: {e}')
    except Exception as e:
        log.error(f'Unexpected exception: {e}')

