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

