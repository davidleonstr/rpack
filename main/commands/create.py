from rpack import RPackBuilder

def rcreate(args):
    files = None
    
    if args.files:
        files = args.files.split()

    builder = RPackBuilder(
        args.output, 
        args.input,
        args.compression,
        files,
        level=args.compression_level
    )
    builder.build()