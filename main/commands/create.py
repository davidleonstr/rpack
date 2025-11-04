from rpack import RPackBuilder

def rcreate(args):
    builder = RPackBuilder(
        args.input, 
        args.output, 
        args.compression, 
        level=args.compression_level
    )
    builder.build()