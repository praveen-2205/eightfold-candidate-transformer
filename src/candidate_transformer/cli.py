import argparse
from candidate_transformer import __version__

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Candidate Transformer")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    
    args, _ = parser.parse_known_args(argv)
    
    if args.version:
        print(__version__)
        return 0
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())