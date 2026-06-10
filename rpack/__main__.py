import sys
import argparse
from main import COMMANDS
from rpack.compressor import CompressionType

def main():
    parser = argparse.ArgumentParser(description='rpack - Resource packaging system')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
    createParser = subparsers.add_parser('create', help='Create .rpack file')
    createParser.add_argument(
        '--input', 
        '-i', 
        required=False, 
        default=None, 
        help='Input folder or file'
    )
    createParser.add_argument('--output', '-o', required=True, help='Output .rpack file')
    createParser.add_argument(
        '--compression', 
        '-c', 
        default='zlib', 
        choices=CompressionType,
        help='Compression method (default: zlib)'
    )
    createParser.add_argument(
        '--compression-level', 
        '-l', 
        default=6, 
        help='Compression method level (default: 6)'
    )
    createParser.add_argument(
        '--files', 
        '-f', 
        default=None, 
        required=False,
        help='For especific paths: file/path.ext file/path.ext'
    )

    listParser = subparsers.add_parser('list', help='List contents of .rpack')
    listParser.add_argument('file', help='.rpack file')
    listParser.add_argument(
        '--compression', 
        '-c', 
        default='zlib', 
        choices=CompressionType,
        help='Compression method (default: zlib)'
    )
        
    extractParser = subparsers.add_parser('extract', help='Extract contents of .rpack')
    extractParser.add_argument('file', help='.rpack file')
    extractParser.add_argument(
        '--output', 
        '-o', 
        default='extracted', 
        help='Output folder (default: extracted)'
    )
    extractParser.add_argument(
        '--compression', 
        '-c', 
        default='zlib', 
        choices=CompressionType,
        help='Compression method (default: zlib)'
    )
        
    args = parser.parse_args()
        
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command in COMMANDS:
        COMMANDS[args.command](args)

if __name__ == '__main__':
    main()