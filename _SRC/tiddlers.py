from datetime import datetime
import os.path
import json
import re
import os


MAIN_DIR = 'tiddlers'
ASSETS_DIR = '../../assets'

ORG_HEADER = '''
#+description: My Blog
#+keywords: {keys}
#+options: html-style:nil html-scripts:nil author:nil validate:nil html-allow-html:t {extra_options}
#+tags: {tags}
'''

PREFERRED_DIRS = [
    "algorithms",
    "dsp",
    "embedded",
    "haskell",
    "python",
    "tcl/tk",
]

UNPREFERRED_DIRS = ['misc', 'windows']

def _determine_out_dir(tags:list[str]) -> list[str]:
    # XXX pass lower-cased tags list
    if len(tags) == 0:
        return [MAIN_DIR, 'Misc']
    elif len(tags) == 1:
        return [MAIN_DIR, tags[0].capitalize()]
    tags = [t for t in tags if t not in UNPREFERRED_DIRS]
    if len(tags) > 1:
        for pd in PREFERRED_DIRS:
            if pd in tags:
                return [MAIN_DIR, pd.capitalize()]
    if len(tags) in (0, 1):
        return _determine_out_dir(tags)
    else:
        return [MAIN_DIR, tags[0].capitalize()]

def determine_out_dir(tags:list[str]):
    res = _determine_out_dir(tags)
    for r in res:
        yield r.replace('/', '')

def timestamp_to_org(ts: str) -> str:
    dt = datetime(
        year=int(ts[0:4]),
        month=int(ts[4:6]),
        day=int(ts[6:8]),
        hour=int(ts[8:10]),
        minute=int(ts[10:12]),
        second=int(ts[12:14]),
    )
    return dt.strftime("[%Y-%m-%d %a %H:%M]")


def md_to_org(text: str, depth_from_root_dir:int, number_of_headings:list[int]) -> str:
    def path_to_asset(matched):
        up_dirs = ['..']*depth_from_root_dir
        up = os.path.join(*up_dirs)
        title = matched.group(1)
        p = os.path.join(up, ASSETS_DIR, title) + '.svg'
        return f'[[file:{p}]]'

    def md_to_org_link(matched):
        nonlocal number_of_headings
        number_of_headings[0] += 1
        return "*" * len(matched.group(1)) + " " + matched.group(2)

    lines = text.splitlines()
    out = []
    in_code = False
    code_lang = ""
    for line in lines:
        # Code block start/end
        if line.startswith("```"):
            if not in_code:
                code_lang = line[3:].strip()
                out.append(f"#+BEGIN_SRC {code_lang}" if code_lang else "#+BEGIN_SRC")
                in_code = True
            else:
                out.append("#+END_SRC")
                in_code = False
            continue
        if in_code:
            out.append(line)
            continue
        # Lists
        line = re.sub(r'^(\s*)\*\s+([^*]*)$', r'\1- \2', line)
        # Headings
        # line = re.sub(r'^(#{1,6})\s*(.*)', lambda m: "*" * len(m.group(1)) + " " + m.group(2), line)
        line = re.sub(r'^(#{1,6})\s*(.*)', md_to_org_link, line)
        # Bold: **text** → *text*
        line = re.sub(r'\*\*(.+?)\*\*', r'*\1*', line)
        # Italic: *text* → /text/
        line = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'/\1/', line)
        # Inline code: `code` → ~code~
        line = re.sub(r'`([^`]+)`', r'~\1~', line)
        # Tiddly links
        line = re.sub(r'\[\[([^\]]+)\|([^\]]+)]\]', r'[[\2][\1]]', line)
        # Images: ![alt](url) → [[url]]
        line = re.sub(r'''!\[[^\]]*\]\(([^)]+)\)''', r'[[\1]]', line)
        # Links: [text](url) → [[url][text]]
        line = re.sub(r'''\[([^\]]+)\]\(([^)]+)\)''', r'[[\2][\1]]', line)
        # TiddlyWiki transclusions: {{Title}} → [[Title]]
        line = re.sub(r'\{\{([^}]+)\}\}', path_to_asset, line)
        out.append(line)
    return "\n".join(out)


# TODO {{xxx}} - must insert referred article by it's title

####################################################################
with open('tiddlers.json', 'rt') as f:
    tiddlers = json.load(f)

for i, t in enumerate(tiddlers):
    number_of_headings = [0]
    # if i > 10: break
    if t['title'] and t.get('text'):
        tags = t.get('tags', '')
        tags_list = tags.split()
        l_tag_list = [x.lower() for x in tags_list]
        created = t.get('created')
        if t.get('type') == 'image/svg+xml':
            in_dir = os.path.join(MAIN_DIR, ASSETS_DIR)
            os.makedirs(in_dir, exist_ok=True)
            fname = t['title'] + '.svg'
            path = os.path.join(in_dir, fname)
            with open(path, 'wt') as f:
                f.write(t['text'])
                print(f'Saved ASSET file {path}')
        else:
            fname = '_'.join(w for w in t['title'].split() if len(w) > 1)
            fname = ''.join(ch for ch in fname if (ch.isalnum() or ch in ['_']))
            in_dir = list(determine_out_dir(l_tag_list))
            os.makedirs(os.path.join(*in_dir), exist_ok=True)
            fname += '.org'
            path = os.path.join(*in_dir, fname)
            # print(path, in_dir)
            with open(path, 'wt') as f:
                org_text = md_to_org(t['text'], len(in_dir) - 1, number_of_headings).strip()
                print(f'#+title: {t["title"].strip()}', file=f)
                extra_options = "toc:nil" if number_of_headings[0] <= 1 else ""
                org_tags = ' '.join(l_tag_list)
                org_keys = ', '.join(l_tag_list)
                print(ORG_HEADER.format(tags=org_tags, keys=org_keys, extra_options=extra_options).strip(), file=f)
                if (created := timestamp_to_org(created) if created else ''):
                    print(f'#+date: {created}', file=f)
                print('', file=f)
                print(f'* {t["title"].strip()}', file=f)
                print('', file=f)
                print(org_text, file=f)
                print(f'Saved file {path}')
