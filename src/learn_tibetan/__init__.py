import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="learn-tibetan")
    parser.add_argument("command", choices=["build-content"])
    args = parser.parse_args()
    if args.command == "build-content":
        from learn_tibetan.content import write

        print(f"wrote {write()}")
