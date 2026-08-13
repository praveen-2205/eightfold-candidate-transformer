import argparse
import json
import sys
from candidate_transformer import __version__
from candidate_transformer.pipeline import run
from candidate_transformer.projection import load_config, project, validate_output
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    parser.add_argument("--input", action="append", required=False, help="Input file paths (repeatable)")
    parser.add_argument("--config", type=str, default="configs/default.json", help="Path to output config JSON")
    parser.add_argument("--out", type=str, help="Output JSON file path (default: stdout)")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM and use deterministic stub")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the JSON output")
    
    args, _ = parser.parse_known_args(argv)
    
    if args.version:
        print(__version__)
        return 0
        
    if not args.input:
        parser.error("At least one --input argument is required.")
        
    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return 1

    # Run the pipeline
    profiles = run(args.input, use_llm=not args.no_llm)
    
    if not profiles:
        logger.error("All inputs unusable. No profiles generated.")
        return 1
        
    output_data = []
    for p in profiles:
        try:
            proj = project(p, config)
            validate_output(proj, config)
            output_data.append(proj)
        except Exception as e:
            logger.error(f"Failed to project/validate profile {p.candidate_id}: {e}")
            
    if not output_data:
        return 1

    # Output formatting
    if len(output_data) == 1:
        final_json = output_data[0]
    else:
        final_json = output_data

    indent = 2 if args.pretty else None
    json_str = json.dumps(final_json, indent=indent, default=str)

    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(json_str)
            logger.info(f"Wrote output to {args.out}")
        except Exception as e:
            logger.error(f"Failed to write output to {args.out}: {e}")
            return 1
    else:
        print(json_str)

    return 0

if __name__ == "__main__":
    sys.exit(main())