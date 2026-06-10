from rpack import ResourcePack

def rlist(args):
    pack = ResourcePack(
        args.file, 
        args.compression
    )

    print(f'Content of {args.file}:')
        
    def listRecursive(path='', indent=0):
        items = pack.listDir(path)
        for item in items:
            fullPath = f'{path}/{item}' if path else item
            prefix = '  ' * indent
                
            if pack.isDir(fullPath):
                print(f'{prefix}Folder: {item}/')
                listRecursive(fullPath, indent + 1)
            else:
                info = pack.index[fullPath]
                sizeKb = info['size_original'] / 1024
                print(f'{prefix}File: {item} ({sizeKb:.2f} KB)')
        
    listRecursive()