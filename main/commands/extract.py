from pathlib import Path
from rpack import ResourcePack

def rextract(args):
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    pack = ResourcePack(
        args.file, 
        args.compression
    ) 
    
    print(f'Extracting from {output_dir}...')
        
    for file_path in pack._index.keys():
        data = pack.get(file_path)
        target_path = output_dir / file_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(target_path, 'wb') as f:
            f.write(data)
            
        print(f'Done {file_path}')
        
    print('Extraction complete')