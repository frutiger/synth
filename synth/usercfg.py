# synth.usercfg

import configparser
import pathlib

def validate_target_path(value):
    path = pathlib.Path(value)
    if not path.expanduser().is_dir():
        raise RuntimeError(f'target.path {value} is not a directory')
    return path.resolve()

validators = {
        'target.path': validate_target_path,
        }

def validate_item(key, value):
    if key not in validators.keys():
        raise RuntimeError(f'Unknown config key: {key}')

    return validators[key](value)

def read(skip_validation=False):
    parser = configparser.ConfigParser()

    path = pathlib.Path('~/.synth.cfg').expanduser()
    if not path.is_file():
        return parser

    parser.read(path)

    if skip_validation:
        return parser

    for section_name, section in parser.items():
        for option, value in section.items():
            validate_item(f'{section_name}.{option}', value)

    return parser

def write(items):
    validated_items = {}
    for key, value in items:
        validated_items[key] = str(validate_item(key, value))

    parser = configparser.ConfigParser()

    path = pathlib.Path('~/.synth.cfg').expanduser()
    parser.read(path)

    for key, value in validated_items.items():
        section, option = key.split('.')

        if not parser.has_section(section):
            parser.add_section(section)

        parser.set(section, option, value)

    with open(path, 'w') as f:
        parser.write(f)

