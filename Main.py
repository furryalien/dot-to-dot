import argparse
from pathlib import Path

from DotToDot import makeMaxSizeDot

MAX_DOTS_IN_IMAGE = 800
MAX_INPUT_DIMENSION = 1200
PDF_DPI = 300
SUPPORTED_INPUT_TYPES = ('.jpg', '.jpeg', '.png', '.pdf')

def positiveInteger(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('Value must be greater than zero')
    return number

def inputDimension(value):
    number = positiveInteger(value)
    if number < 400:
        raise argparse.ArgumentTypeError('Maximum dimension must be at least 400')
    return number

def supportedInputPath(value):
    path = Path(value)
    if path.suffix.lower() not in SUPPORTED_INPUT_TYPES:
        supportedTypes = ', '.join(SUPPORTED_INPUT_TYPES)
        raise argparse.ArgumentTypeError(
            'Unsupported input type. Choose one of: ' + supportedTypes)
    if not path.is_file():
        raise argparse.ArgumentTypeError('Input file does not exist: ' + value)
    return str(path)

def parseArguments(arguments=None):
    parser = argparse.ArgumentParser(
        description='Convert a JPG, PNG, or PDF into a dot-to-dot puzzle.')
    parser.add_argument(
        'input_file', type=supportedInputPath,
        help='path to a JPG, PNG, or PDF file')
    parser.add_argument(
        '--max-dots', type=positiveInteger, default=MAX_DOTS_IN_IMAGE,
        help='maximum number of dots (default: %(default)s)')
    parser.add_argument(
        '--max-dimension', type=inputDimension, default=MAX_INPUT_DIMENSION,
        help='maximum tracing width or height in pixels (default: %(default)s)')
    parser.add_argument(
        '--pdf-dpi', type=positiveInteger, default=PDF_DPI,
        help='PDF rendering resolution (default: %(default)s)')
    return parser.parse_args(arguments)

def main():
    arguments = parseArguments()
    makeMaxSizeDot(
        arguments.input_file,
        arguments.max_dots,
        arguments.max_dimension,
        arguments.pdf_dpi)

if __name__ == '__main__':
    main()
