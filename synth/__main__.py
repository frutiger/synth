# synth.__main__

import argparse
import configparser
import pathlib
import subprocess
import typing

import synth.metadata
import synth.config

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

def get_parser() -> argparse.ArgumentParser:
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
            help='Extract modifications from <target>>')
    extract_parser.add_argument('names', metavar='<name>', nargs='*')
    extract_parser.add_argument('target', metavar='<target>', nargs='?')
    extract_parser.add_argument(
            '--upstream',
            metavar='<upstream>',
            default='@{upstream}')

    set_parser = subparsers.add_parser(
            'config',
            help='Update configuration <property> to <value>')
    set_parser.add_argument(
            'property',
            metavar='<property>',
            choices=synth.config.validators.keys())
    set_parser.add_argument(dest='value', metavar='<value>')

    return parser

def post_process_args(
        args: argparse.Namespace,
        config: configparser.ConfigParser) -> None:
    if args.mode == 'compose' or args.mode == 'extract':
        config_target_path = config.get('target', 'path', fallback=None)
        if config_target_path:
            args.target = config_target_path
        else:
            if len(args.names) == 0:
                raise CommandlineParsingError('target not specified')
            args.target = args.names.pop()

def git_cmd(
        args: list[str],
        working_dir: typing.Optional[pathlib.Path]=None) -> list[str]:
    return subprocess.run(
            ['git'] + args,
            capture_output=True,
            check=True,
            cwd=working_dir,
            encoding='ascii').stdout.split('\n')

def synth_config(property: str, value: str) -> None:
    synth.config.write({ property: value }.items())

def synth_init() -> None:
    synth.metadata.initialize()

def synth_add(origin: str, ref: str, name: str) -> None:
    if origin[-1] == '/':
        origin = origin[:-1]

    if name is None:
        name = origin.split('/')[-1]

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

def synth_compose(raw_target: str, raw_names: list[str]) -> None:
    target = pathlib.Path(raw_target)
    if len(raw_names) == 0:
        names = synth.metadata.get_module_names()
    else:
        names = iter(raw_names)
    for name in names:
        module = synth.metadata.get_module(name)
        print(f'Composing {name} from {module["origin"]} at '
              f'{module["commit"]}')
        dest = target/name
        if not dest.exists():
            git_cmd(['clone', module['origin'], str(dest)])
        git_cmd(['fetch', 'origin', module['commit']], dest)
        git_cmd(['reset', '--hard', module['commit']], dest)
        patches = synth.metadata.get_patch_dir(name)
        if patches.exists():
            git_cmd(['am', '-3', str(patches)], dest)

def synth_extract(
        raw_target: str,
        raw_names: list[str],
        upstream: str) -> None:
    target = pathlib.Path(raw_target)
    if len(raw_names) == 0:
        names = synth.metadata.get_module_names()
    else:
        names = iter(raw_names)
    for name in names:
        src = target/name
        if not src.is_dir():
            raise RuntimeError(f'{name} has not been composed')

        module = synth.metadata.get_module(name)
        module['commit'] = git_cmd(['rev-parse', upstream], src)[0]
        synth.metadata.update_module(name, module)

        print(f'Extracting patches from {name} since {upstream}')
        synth.metadata.clear_patches(name)
        git_cmd([
            'format-patch',
            '-N',
            upstream,
            '-o',
            str(synth.metadata.get_patch_dir(name).resolve())],
            src)

def main() -> None:
    args = get_parser().parse_args()
    if args.mode == 'config':
        synth_config(args.property, args.value)

    if args.mode == 'init':
        synth_init()

    if args.mode == 'add':
        synth_add(args.origin, args.ref, args.name)

    post_process_args(args, synth.config.read())

    if args.mode == 'compose':
        synth_compose(args.target, args.names)

    if args.mode == 'extract':
        synth_extract(args.target, args.names, args.upstream)

if __name__ == '__main__':
    main()

