import sys
import argparse
import logging
from insyt.db import Database
from insyt.file_watcher import watch_files

# check must be located before importing code that uses 3.10 features
if sys.version_info < (3, 10):
    exit("Error: Python version 3.10 or higher is required.")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    #add -- arguments
    parser.add_argument("--watch", nargs="+", help="List of files to watch")
    parser.add_argument("--db", help="Database file to use", default="insyt.db")
    parser.add_argument("--debug", help="Enable debug logging", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
        logging.getLogger("INSyT -- DEBUG").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.getLogger("INSyT").setLevel(logging.INFO)

    logging.info("Starting INSyT")
    logging.debug(f"Command line arguments: {args}")

    file_list = args.watch
    logging.debug(f"Configuring the following files to watch: {file_list}")

    # Create database object
    db = Database(args.db)
    logging.debug(f"Using database file: {args.db}")

    logging.debug("Starting file watcher")
    # Watch files
    watch_files(file_list)

    #this is meant just to test some functionality during development TODO: Add actual runtime functionality at the end
    breakpoint()


if __name__ == "__main__":
    main()