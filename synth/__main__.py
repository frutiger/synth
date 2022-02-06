# synth.__main__

import argparse
import subprocess
import sys

import synth.metadata
import synth.usercfg

class CommandlineParsingError(RuntimeError):
    pass

class CustomFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action: argparse.Action) -> str:
        result = super()._format_action(action)
        if action.nargs == argparse.PARSER:
            # since we aren't showing the subcommand group, de-indent by 2
            # spaces
            lines = result.split('\n')
            lines = [line[2:] for line in lines]
            result = '\n'.join(lines)
        return result

def get_parser():
    parser = argparse.ArgumentParser(formatter_class=CustomFormatter)

    subparsers = parser.add_subparsers(
            dest='mode',
            required=True,
            metavar='<mode>',
            title=argparse.SUPPRESS)

    subparsers.add_parser(
            'init',
            help='Initialize a new `synth` repository')

    add_parser = subparsers.add_parser(
            'add',
            help='Track the repository at <origin>')
    add_parser.add_argument('origin', metavar='<origin>')
    add_parser.add_argument('--ref', metavar='<ref>', default='HEAD')
    add_parser.add_argument('--name', metavar='<name>')

    compose_parser = subparsers.add_parser(
            'compose',
            help='Compose a directory structure at <target>')
    compose_parser.add_argument('names', metavar='<name>', nargs='*')
    compose_parser.add_argument('target', metavar='<target>', nargs='?')

    extract_parser = subparsers.add_parser(
            'extract',
            help='Extract modifications to the module at <target>/<name>')
    extract_parser.add_argument('name', metavar='<name>', nargs='?')
    extract_parser.add_argument('target', metavar='<target>', nargs='?')

    set_parser = subparsers.add_parser(
            'set',
            help='Update configuration <key> to <value>')
    set_parser.add_argument(
            'key',
            metavar='<key>',
            choices=synth.usercfg.validators.keys())
    set_parser.add_argument(dest='value', metavar='<value>')

    return parser

def post_process_args(args, config):
    if args.mode == 'compose':
        config_target_path = config.get('target', 'path', fallback=None)
        if config_target_path:
            args.target = config_target_path
        else:
            args.target = args.names.pop()
    elif args.mode == 'extract':
        if not args.target:
            config_target_path = config.get('target', 'path', fallback=None)
            if config_target_path:
                args.target = config_target_path
            else:
                raise CommandlineParsingError('target not specified')

def git_cmd(args):
    return subprocess.run(
            ['git'] + args,
            capture_output=True,
            check=True,
            encoding='ascii').stdout.split('\n')

def synth_set(key, value):
    synth.usercfg.write({ key: value }.items())

def synth_init():
    synth.metadata.initialize()

def synth_add(origin, ref, name):
    if origin[-1] == '/':
        origin = origin[:-1]

    if name is not None and synth.metadata.has_module(name):
            raise RuntimeError(f'Module with {name} already exists')
    else:
        name = origin.split('/')[-1]
        if synth.metadata.has_module(name):
            raise RuntimeError(f'Module with inferred {name} already exists')

    resolved_hash = None
    for line in git_cmd(['ls-remote', origin, ref]):
        if line == '':
            continue
        if resolved_hash:
            raise RuntimeError(f'{ref} is ambiguous and lists multiple refs')
        resolved_hash, _ = line.split()
    if not resolved_hash:
        raise RuntimeError(f'Could not find {ref} at {origin}')

    synth.metadata.create_module(name, origin, resolved_hash)

def main():
    args = get_parser().parse_args()
    if args.mode == 'set':
        synth_set(args.key, args.value)
        return

    if args.mode == 'init':
        return synth_init()

    if args.mode == 'add':
        return synth_add(args.origin, args.ref, args.name)

    post_process_args(args, synth.usercfg.read())

if __name__ == '__main__':
    sys.exit(main())

