from pathlib import Path
from rpack import ResourcePack

def rextract(args):
    outputDir = Path(args.output)
    outputDir.mkdir(parents=True, exist_ok=True)

    pack = ResourcePack(
        args.file, 
        args.compression
    ) 
    
    print(f'Extracting from {outputDir}...')
        
    for filePath in pack.index.keys():
        data = pack.get(filePath)
        targetPath = outputDir / filePath
        targetPath.parent.mkdir(parents=True, exist_ok=True)
            
        with open(targetPath, 'wb') as f:
            f.write(data)
            
        print(f'Done {filePath}')
        
    print('Extraction complete')