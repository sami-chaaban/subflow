import argparse
from importlib import resources
from pathlib import Path
import sys


def create_config(destination):
    destination = Path(destination).expanduser()
    if destination.is_dir():
        destination = destination / "config.json"
    destination = destination.resolve()

    if destination.exists():
        raise FileExistsError(f"Config already exists: {destination}")
    if not destination.parent.is_dir():
        raise FileNotFoundError(
            f"Parent directory does not exist: {destination.parent}"
        )

    example = resources.files("subflow").joinpath("config.json")
    with destination.open("xb") as config_file:
        config_file.write(example.read_bytes())

    return destination


def build_parser():
    parser = argparse.ArgumentParser(
        prog="subflow",
        description="Start the Subflow GUI or create an editable configuration file.",
    )
    parser.add_argument(
        "--init",
        nargs="?",
        const="config.json",
        metavar="PATH",
        help="copy the example configuration to PATH (default: ./config.json)",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.init is not None:
        try:
            destination = create_config(args.init)
        except OSError as error:
            print(f"Could not create config: {error}", file=sys.stderr)
            return 1

        print(f"Created config: {destination}")
        return 0

    from subflow import subflow

    subflow.gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
