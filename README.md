# 🎹 `synth`

A tool that simulates a monorepo in a polyrepo world, while allowing local
patches/modifications that are not present in upstream repos. `synth` assumes a
reasonably modern version of `git` is available in the user's `PATH`.

## Commands

* `synth init`

    Initialize a new `synth` repository.

* `synth add <origin> [--ref=<ref>] [--name=<name>]`

    Track the repository at `<origin>` at its current `HEAD` (unless an
    alternative `<ref>` is specified) as one of the modules of this monorepo.
    By default, the stem of `<origin>` is used as the name of this module. This
    can be overriden by specifying a `<name>`.

    A `<name>` must be specified if a module already exists with the inferred
    `<name>`.

* `synth compose [<name>...] [<target>]`

    Compose a directory structure at `<target>` from the constitutents of this
    monorepo, applying any patches that were extracted (see `synth extract`)
    earlier.

    If `<name>`s are specified, only compose those constituents, otherwise
    compose all constitutents.

* `synth extract [<name>...] [<target>] [--upstream=<upstream>]`

    Extract any modifications to all the modules at `<target>` from an upstream
    ref to the current `HEAD` into a patch series tracked within this `synth`
    repo.  By default, `@{upstream}` is used but this can be overriden on the
    commandline.

    If `<name>`s are specified, only extract those constituents, otherwise
    extract all constitutents.

* `synth config <property> <value>`

    Update this repository's configuration file to set the `<property>` to
    `<value>`. The following properties are supported:

    * `target.path`

        Set the default `<target>` path for the `compose` and `extract`
        subcommands, making that argument optional.

## License

Copyright (C) 2022 Masud Rahman

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
