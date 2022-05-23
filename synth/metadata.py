# synth.metadata

import collections.abc
import json
from pathlib import Path
import typing

VERSION = 1
SYNTH_DIR = Path('.synth')

class Module(typing.TypedDict):
    origin: str
    commit: str

def initialize() -> None:
    if SYNTH_DIR.exists():
        raise RuntimeError('synth configuration already exists here')
    SYNTH_DIR.mkdir()

    metadata = {
            'version': VERSION,
            }

    metadata_path = SYNTH_DIR/'metadata'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, sort_keys=True, indent=2)
        f.write('\n')

def _discover_dir() -> Path:
    candidate = Path.cwd()

    while not candidate.samefile(candidate.root):
        if (candidate/SYNTH_DIR).is_dir():
            return candidate/SYNTH_DIR
        candidate = candidate.parent

    raise RuntimeError('Not in a synth repo')

def _check_version(synth_dir: Path) -> None:
    metadata_path = synth_dir/'metadata'
    with open(metadata_path) as f:
        metadata = json.load(f)

    if 'version' not in metadata:
        raise RuntimeError('Corrupt synth metadata')

    version = metadata['version']
    if version != VERSION:
        raise RuntimeError(f'Unsupported synth metadata version: {version}')

def get_config_path() -> Path:
    return _discover_dir()/'config'

def _get_module_dir(name: str) -> Path:
    synth_dir = _discover_dir()
    _check_version(synth_dir)
    return synth_dir/'modules'/name

def create_module(name: str, origin: str, commit: str) -> None:
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
        json.dump(metadata, f, sort_keys=True, indent=2)
        f.write('\n')

    (module_dir/'patches').mkdir()

def get_module(name: str) -> Module:
    module_dir = _get_module_dir(name)
    if not module_dir.is_dir():
        raise RuntimeError(f'Module {name} does not exist')

    metadata_path = module_dir/'metadata'
    with open(metadata_path) as f:
        metadata = json.load(f)
        return {
                'commit': metadata['commit'],
                'origin': metadata['origin'],
                }

def update_module(name: str, module: Module) -> None:
    module_dir = _get_module_dir(name)
    if not module_dir.is_dir():
        raise RuntimeError(f'Module {name} does not exist')

    metadata_path = module_dir/'metadata'
    with open(metadata_path, 'w') as f:
        json.dump(module, f, sort_keys=True, indent=2)
        f.write('\n')

def get_module_names() -> collections.abc.Iterator[str]:
    synth_dir = _discover_dir()
    _check_version(synth_dir)
    for path in (synth_dir/'modules').iterdir():
        yield path.stem

def get_patch_dir(name: str) -> Path:
    module_dir = _get_module_dir(name)
    return module_dir/'patches'

def clear_patches(name: str) -> None:
    patch_dir = get_patch_dir(name)
    if patch_dir.exists():
        for patch in patch_dir.iterdir():
            patch.unlink()
    else:
        patch_dir.mkdir(parents=True)

def get_patches(name: str) -> collections.abc.Iterator[Path]:
    yield from get_patch_dir(name).iterdir()

