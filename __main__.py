import sys
import argparse
from main import COMMANDS
from rpack.compressor import CompressionType

parser = argparse.ArgumentParser(description='rpack - Resource packaging system')
subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
create_parser = subparsers.add_parser('create', help='Create .rpack file')
create_parser.add_argument('--input', '-i', required=True, help='Input folder or file')
create_parser.add_argument('--output', '-o', required=True, help='Output .rpack file')
create_parser.add_argument(
    '--compression', 
    '-c', 
    default='zlib', 
    choices=CompressionType,
    help='Compression method (default: zlib)'
)
create_parser.add_argument(
    '--compression-level', 
    '-l', 
    default=6, 
    help='Compression method level (default: 6)'
)

list_parser = subparsers.add_parser('list', help='List contents of .rpack')
list_parser.add_argument('file', help='.rpack file')
list_parser.add_argument(
    '--compression', 
    '-c', 
    default='zlib', 
    choices=CompressionType,
    help='Compression method (default: zlib)'
)
    
extract_parser = subparsers.add_parser('extract', help='Extract contents of .rpack')
extract_parser.add_argument('file', help='.rpack file')
extract_parser.add_argument(
    '--output', 
    '-o', 
    default='extracted', 
    help='Output folder (default: extracted)'
)
extract_parser.add_argument(
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