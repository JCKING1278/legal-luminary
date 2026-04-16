import os, json
from pathlib import Path

def audit():
    candidates_dir = Path('_candidates')
    assets_base = Path('assets/imgs/candidates')
    result = {}
    for file in candidates_dir.glob('*.md'):
        slug = file.stem
        headshot_path = assets_base / slug / 'headshot.jpg'
        exists = headshot_path.is_file()
        result[slug] = {
            'candidate_file': str(file),
            'headshot_exists': exists,
            'headshot_path': str(headshot_path) if exists else None
        }
    out_path = Path('_data/audit_headshots.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f"Audit written to {out_path}")

if __name__ == '__main__':
    audit()
