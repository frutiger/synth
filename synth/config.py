# synth.config

import collections.abc
import configparser
import pathlib

import synth.metadata

def validate_target_path(value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    if not path.expanduser().is_dir():
        raise RuntimeError(f'target.path {value} is not a directory')
    return path.resolve()

validators = {
        'target.path': validate_target_path,
        }

def validate_item(key: str, value: str) -> pathlib.Path:
    if key not in validators.keys():
        raise RuntimeError(f'Unknown config key: {key}')

    return validators[key](value)

def read(skip_validation: bool=False) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()

    path = synth.metadata.get_config_path()
    if not path.is_file():
        return parser

    parser.read(path)

    if skip_validation:
        return parser

    for section_name, section in parser.items():
        for option, value in section.items():
            validate_item(f'{section_name}.{option}', value)

    return parser

def write(items: collections.abc.ItemsView[str, str]) -> None:
    validated_items = {}
    for key, value in items:
        validated_items[key] = str(validate_item(key, value))

    parser = configparser.ConfigParser()

    path = synth.metadata.get_config_path()
    parser.read(path)

    for key, value in validated_items.items():
        section, option = key.split('.')

        if not parser.has_section(section):
            parser.add_section(section)

        parser.set(section, option, value)

    with open(path, 'w') as f:
        parser.write(f)

