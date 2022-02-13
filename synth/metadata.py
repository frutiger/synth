# synth.metadata

import json
import pathlib

VERSION = 1
SYNTH_DIR = pathlib.Path('.synth')

def initialize():
    if SYNTH_DIR.exists():
        raise RuntimeError('synth configuration already exists here')
    SYNTH_DIR.mkdir()

    metadata = {
            'version': VERSION,
            }

    metadata_path = SYNTH_DIR/'metadata'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        f.write('\n')

def _discover_dir():
    candidate = pathlib.Path.cwd()

    while not candidate.samefile(candidate.root):
        if (candidate/SYNTH_DIR).is_dir():
            return candidate/SYNTH_DIR
        candidate = candidate.parent

    raise RuntimeError('Not in a synth repo')

def _check_version(synth_dir):
    metadata_path = synth_dir/'metadata'
    with open(metadata_path) as f:
        metadata = json.load(f)

    if 'version' not in metadata:
        raise RuntimeError('Corrupt synth metadata')

    version = metadata['version']
    if version != VERSION:
        raise RuntimeError(f'Unsupported synth metadata version: {version}')

def get_config_path():
    return _discover_dir()/'config'

def _get_module_dir(name) -> pathlib.Path:
    synth_dir = _discover_dir()
    _check_version(synth_dir)
    return synth_dir/'modules'/name

def create_module(name, origin, commit):
    metadata = {
            'origin': origin,
            'commit': commit,
            }

    module_dir = _get_module_dir(name)
    if module_dir.exists():
        raise RuntimeError(f'Module {name} already exists')
    module_dir.mkdir(parents=True)

    metadata_path = module_dir/'metadata'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
        f.write('\n')

    (module_dir/'patches').mkdir()

def get_module(name):
    module_dir = _get_module_dir(name)
    if not module_dir.is_dir():
        raise RuntimeError(f'Module {name} does not exist')

    metadata_path = module_dir/'metadata'
    with open(metadata_path) as f:
        return json.load(f)

def update_module(name, module):
    module_dir = _get_module_dir(name)
    if not module_dir.is_dir():
        raise RuntimeError(f'Module {name} does not exist')

    metadata_path = module_dir/'metadata'
    with open(metadata_path, 'w') as f:
        return json.dump(module, f, indent=2)

def get_module_names():
    synth_dir = _discover_dir()
    _check_version(synth_dir)
    for path in (synth_dir/'modules').iterdir():
        yield path.stem

def get_patch_dir(name):
    module_dir = _get_module_dir(name)
    return module_dir/'patches'

def clear_patches(name):
    for patch in get_patch_dir(name).iterdir():
        patch.unlink()

def get_patches(name):
    yield from get_patch_dir(name).iterdir()

