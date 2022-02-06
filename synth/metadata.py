# synth.metadata

import json
import pathlib

def initialize():
    system_dir = pathlib.Path('.synth')
    if system_dir.exists():
        raise RuntimeError('synth configuration already exists here')
    system_dir.mkdir()

    metadata = {
            'version': 1,
            }

    metadata_path = system_dir/'metadata'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        f.write('\n')

def check_version():
    system_dir = pathlib.Path('.synth')
    if not system_dir.is_dir():
        raise RuntimeError('synth configuration not found here')

    metadata_path = system_dir/'metadata'
    with open(metadata_path) as f:
        metadata = json.load(f)

    if 'version' not in metadata:
        raise RuntimeError('Corrupt synth metadata')

    version = metadata['version']
    if version != 1:
        raise RuntimeError(f'Unsupported synth metadata version: {version}')

def has_module(name):
    return pathlib.Path(name).exists()

def create_module(name, origin, commit):
    metadata = {
            'origin': origin,
            'commit': commit,
            'patches': [],
            }

    module_dir = pathlib.Path(name)
    module_dir.mkdir()
    metadata_path = module_dir/'metadata'

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        f.write('\n')

