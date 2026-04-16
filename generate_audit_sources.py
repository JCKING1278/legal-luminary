import os,json
from pathlib import Path

def audit():
    candidates_dir = Path('_candidates')
    data_path = Path('_data/audit_sources.json')
    result={}
    for file in candidates_dir.glob('*.md'):
        slug=file.stem
        # sources listed in front matter? assume _data/sources_{slug}.json exists
        src_file=Path('_data/sources_'+slug+'.json')
        if src_file.is_file():
            with open(src_file) as f:
                src=json.load(f)
            count=len(src.get('sources',[]))
        else:
            count=0
        result[slug]={'source_count':count,'verified':count>=2}
    data_path.parent.mkdir(parents=True,exist_ok=True)
    with open(data_path,'w') as f: json.dump(result,f,indent=2)
    print(f"Audit written to {data_path}")

if __name__=='__main__':audit()
