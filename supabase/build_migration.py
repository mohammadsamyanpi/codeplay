"""Build the single SQL Editor script from the tested schema and original catalog."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from catalog import LESSONS


def build():
    source = ROOT / 'supabase'
    chunks = [source.joinpath('schema.sql').read_text(encoding='utf-8')]
    for position, item in enumerate(LESSONS):
        document = json.dumps(item, ensure_ascii=False).replace("'", "''")
        lesson_id = item['id'].replace("'", "''")
        chunks.append(f"INSERT INTO codeplay_private.lessons(id,position,content) VALUES('{lesson_id}',{position},'{document}'::jsonb) ON CONFLICT(id) DO UPDATE SET position=excluded.position,content=excluded.content;")
    chunks.extend(["NOTIFY pgrst, 'reload schema';", 'COMMIT;', ''])
    source.joinpath('setup.sql').write_text('\n'.join(chunks), encoding='utf-8')


if __name__ == '__main__':
    build()
