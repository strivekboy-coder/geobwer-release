"""Tailgap commands with the established argument and validation contracts."""
from __future__ import annotations

import argparse
from rsfm_fairness_audit import cli as implementation


def build_parser() -> argparse.ArgumentParser:
    legacy = implementation.build_parser()
    parser = argparse.ArgumentParser(
        prog="tailgap", description="Tailgap geospatial deployment-tail risk auditing."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    # Reuse argument definitions; dispatch retains the original internal command
    # identities. No protocol, preflight, or support default is changed here.
    legacy_commands = next(
        action for action in legacy._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    descriptions = {
        action.dest: action.help for action in legacy_commands._choices_actions
    }
    for original, command in legacy_commands.choices.items():
        name = original.removeprefix("geobwer-")
        public = commands.add_parser(
            name, parents=[command], add_help=False,
            help=descriptions.get(original, "").replace("GeoBWER", "Tailgap"),
            description=(command.description or "").replace("GeoBWER", "Tailgap"),
        )
        public.set_defaults(command=original)
    return parser


def main(argv: list[str] | None = None) -> None:
    implementation.main(argv=argv, parser=build_parser())
