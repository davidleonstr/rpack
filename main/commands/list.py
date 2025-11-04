from rpack import ResourcePack

def rlist(args):
    pack = ResourcePack(
        args.file, 
        args.compression
    )

    print(f'Content of {args.file}:')
        
    def list_recursive(path='', indent=0):
        items = pack.listdir(path)
        for item in items:
            full_path = f'{path}/{item}' if path else item
            prefix = '  ' * indent
                
            if pack.isdir(full_path):
                print(f'{prefix}Folder: {item}/')
                list_recursive(full_path, indent + 1)
            else:
                info = pack._index[full_path]
                size_kb = info['size_original'] / 1024
                print(f'{prefix}File: {item} ({size_kb:.2f} KB)')
        
    list_recursive()