import sys
import argparse
import logging
from insyt.db import Database
from insyt.file_watcher import watch_files
from insyt.classification import classify
from insyt.analysis import analyze
from insyt.worker import main as worker_main
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer

# check must be located before importing code that uses 3.10 features
if sys.version_info < (3, 10):
    exit("Error: Python version 3.10 or higher is required.")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    #add -- arguments
    parser.add_argument("--analyze", help="Run analysis on the database", action="store_true")
    parser.add_argument("--db", help="Database file to use", default="insyt.db")
    parser.add_argument("--debug", help="Enable debug logging", action="store_true")
    parser.add_argument("--detect", help="Run classifier to detect suspicious activity", action="store_true")
    parser.add_argument("--watch", nargs="+", help="List of files to watch")
    parser.add_argument("--run", help="Run the redis worker to process jobs", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
        logging.getLogger("INSyT").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.getLogger("INSyT").setLevel(logging.INFO)

    logging.info("Starting INSyT")
    logging.debug(f"Command line arguments: {args}")

    assert args.detect or args.watch or args.analyze or args.run, "Must specify either --detect, --watch, --analyze, or --run"
    assert not (args.detect and args.watch), "Cannot specify both --detect and --watch"
    assert not (args.detect and args.analyze), "Cannot specify both --detect and --analyze"
    assert not (args.watch and args.analyze), "Cannot specify both --watch and --analyze"

    model_ckpt = "distilbert-base-uncased"
    model_name = 'isaacwilliam4/distilbert-base-uncased-logline-v3'
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    # Check if the user wants to run the classifier
    if args.run:
        logging.debug("Starting worker")
        worker_main()
    
    elif args.detect:
        logging.debug(f"Using database file: {args.db}")
        logging.debug("Running classifier")
        classify(args.db, model, tokenizer)

    elif args.watch:
        # Create and purge database object
        db = Database(args.db)
        db.purge()
        logging.debug(f"Using database file: {args.db}")
        file_list = args.watch
        logging.debug(f"Configuring the following files to watch: {file_list}")
        logging.debug("Starting file watcher")
        # Watch files
        watch_files(file_list, args.db)

    elif args.analyze:
        logging.debug(f"Using database file: {args.db}")
        logging.debug("Running analysis")
        analyze(args.db)

    # this is meant just to test some functionality during development TODO: Add actual runtime functionality at the end

if __name__ == "__main__":
    main()