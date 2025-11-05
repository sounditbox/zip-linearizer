"""Command-line interface for Zip Linearizer."""

import argparse
import sys
from pathlib import Path

from zip_linearizer.core.exceptions import ZipLinearizerError
from zip_linearizer.core.file_processor import FileProcessor
from zip_linearizer.core.github_handler import GitHubRepositoryHandler
from zip_linearizer.core.text_file_detector import ExtensionBasedDetector
from zip_linearizer.utils.decoder import UTF8Decoder
from zip_linearizer.utils.logger import setup_logging, get_logger
from zip_linearizer.config.settings import ProcessingSettings


class ConsoleProgressReporter:
    """Console progress reporter."""

    def __init__(self, verbose: bool = False):
        """
        Initialize progress reporter.

        Args:
            verbose: Show detailed information.
        """
        self._verbose = verbose
        self._logger = get_logger(__name__)

    def report(self, processed: int, skipped: int) -> None:
        """Print progress to console."""
        message = f"Processed files: {processed}, skipped: {skipped}"
        if self._verbose:
            self._logger.info(message)
        else:
            print(message, file=sys.stderr)

    def report_error(self, filename: str, error: str) -> None:
        """Print error to console."""
        message = f"Error reading {filename}: {error}"
        self._logger.warning(message)
        if self._verbose:
            print(message, file=sys.stderr)


def main() -> int:
    """Main command-line function."""
    parser = argparse.ArgumentParser(
        description="Linearizes ZIP archive contents into a single text file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s archive.zip
  %(prog)s archive.zip -o output.txt
  %(prog)s https://github.com/owner/repo
  %(prog)s https://github.com/owner/repo -o output.txt
  %(prog)s https://github.com/owner/repo/tree/main
  %(prog)s https://github.com/owner/repo/pull/123
  %(prog)s https://github.com/owner/repo/pull/123/files
        """,
    )
    parser.add_argument(
        "source",
        help="Path to ZIP file or GitHub repository URL",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to output file (default: <zip_name>.linearized.txt)",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        default="\n---\n",
        help="Delimiter between files (default: \\n---\\n)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output (DEBUG level logging)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Quiet mode (errors only)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Do not delete temporary file after processing GitHub repository",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose, quiet=args.quiet)
    logger = get_logger(__name__)

    # Check if source is GitHub URL
    is_github_url = "github.com" in args.source.lower() or args.source.startswith(
        ("http://", "https://")
    )

    zip_path: Path
    temp_zip_path: Path | None = None

    if is_github_url:
        # Process GitHub repository
        logger.info(f"GitHub URL detected: {args.source}")
        github_handler = GitHubRepositoryHandler()

        try:
            temp_zip_path = github_handler.download_from_url(args.source)
            zip_path = temp_zip_path
            logger.info(f"Repository archive downloaded: {zip_path}")
        except Exception as e:
            error_msg = f"Error working with GitHub repository: {str(e)}"
            logger.error(error_msg, exc_info=args.verbose)
            if not args.quiet:
                print(error_msg, file=sys.stderr)
            return 1
    else:
        # Process regular ZIP file
        zip_path = Path(args.source)

    # Determine output file
    if args.output:
        output_path = Path(args.output)
    else:
        if is_github_url and temp_zip_path:
            # Use name from repository URL
            output_path = temp_zip_path.with_suffix(".linearized.txt")
        else:
            output_path = zip_path.with_suffix(".linearized.txt")

    settings = ProcessingSettings(delimiter=args.delimiter)
    detector = ExtensionBasedDetector()
    decoder = UTF8Decoder()
    reporter = ConsoleProgressReporter(verbose=args.verbose)

    processor = FileProcessor(
        text_file_detector=detector,
        decoder=decoder,
        settings=settings,
        progress_reporter=reporter,
    )

    try:
        if not args.quiet:
            source_name = args.source if not is_github_url else f"GitHub repository: {args.source}"
            print(f"Processing: {source_name}", file=sys.stderr)

        logger.info(f"Starting processing: {zip_path}")
        stats = processor.process_zip(zip_path, output_path)

        if not args.quiet:
            print(f"\nProcessing completed!", file=sys.stderr)
            print(str(stats), file=sys.stderr)
            print(f"Result saved to: {output_path}", file=sys.stderr)

        logger.info(f"Processing completed successfully. Result: {output_path}")

        # Delete temporary file if GitHub repository and --keep-temp not specified
        if is_github_url and temp_zip_path and not args.keep_temp:
            github_handler = GitHubRepositoryHandler()
            github_handler.cleanup_temp_file(temp_zip_path)
            logger.debug("Temporary file deleted")

        # Return non-zero code if there were errors
        return 1 if stats.error_files > 0 else 0

    except ZipLinearizerError as e:
        error_msg = f"Zip Linearizer error: {str(e)}"
        logger.error(error_msg, exc_info=args.verbose)
        if not args.quiet:
            print(error_msg, file=sys.stderr)
        # Delete temporary file on error
        if is_github_url and temp_zip_path:
            github_handler = GitHubRepositoryHandler()
            github_handler.cleanup_temp_file(temp_zip_path)
        return 1
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=args.verbose)
        if not args.quiet:
            print(error_msg, file=sys.stderr)
        # Delete temporary file on error
        if is_github_url and temp_zip_path:
            github_handler = GitHubRepositoryHandler()
            github_handler.cleanup_temp_file(temp_zip_path)
        return 1


if __name__ == "__main__":
    sys.exit(main())


