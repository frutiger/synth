# synth.__main__

import argparse
import pathlib
import sys

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
    add_parser.add_argument('name', metavar='<name>', nargs='?')

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

def synth_set(key, value):
    synth.usercfg.write({ key: value }.items())

def main():
    args = get_parser().parse_args()
    post_process_args(args, synth.usercfg.read())
    if args.mode == 'set':
        synth_set(args.key, args.value)

if __name__ == '__main__':
    sys.exit(main())

