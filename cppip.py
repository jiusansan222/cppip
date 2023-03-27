#!/usr/bin/env python3

import argparse
import subprocess
import sys

from getdeps.subcmd import add_subcommands, cmd, SubCmd


class ProjectCmdBase(SubCmd):
    def run(self, args):
        self.run_project_cmd(args)
        pass


@cmd("build", "build a given project")
class BuildCmd(ProjectCmdBase):
    def run_project_cmd(self, args):
        pass


class UsageError(Exception):
    pass


def get_arg_var_name(args):
    for arg in args:
        if arg.startswith("--"):
            return arg[2:].replace("-", "_")

    raise Exception(
        "unable to determine argument variable name from %r" % (args,))


def parse_args():
    common_args = argparse.ArgumentParser(add_help=False)
    common_defaults = {}

    def add_common_arg(*args, **kwargs):
        var_name = get_arg_var_name(args)
        default_value = kwargs.pop("default", None)
        common_defaults[var_name] = default_value
        kwargs["default"] = argparse.SUPPRESS
        common_args.add_argument(*args, **kwargs)

    add_common_arg(
        "-v",
        "--verbose",
        help="print more output",
        action="store_true",
        default=False,
    )

    ap = argparse.ArgumentParser(
        description="[cppip] cpp package management tool", parents=[common_args]
    )
    sub = ap.add_subparsers(
        metavar="",
        title="available commands",
        help="",
    )

    add_subcommands(sub, common_args)

    args = ap.parse_args()
    for var_name, default_value in common_defaults.items():
        if not hasattr(args, var_name):
            setattr(args, var_name, default_value)

    return ap, args


def main():
    ap, args = parse_args()
    if getattr(args, "func", None) is None:
        ap.print_help()
        return 0
    try:
        return args.func(args)
    except UsageError as exc:
        ap.error(str(exc))
        return 1
    # except TransientFailure as exc:
    #     print("TransientFailure: %s" % str(exc))
    #     # This return code is treated as a retryable transient infrastructure
    #     # error by Facebook's internal CI, rather than eg: a build or code
    #     # related error that needs to be fixed before progress can be made.
    #     return 128
    except subprocess.CalledProcessError as exc:
        print("%s" % str(exc), file=sys.stderr)
        print("!! Failed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
