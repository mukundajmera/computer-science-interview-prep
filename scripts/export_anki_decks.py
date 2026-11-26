import argparse
import glob
import os
import re

def parse_markdown_to_html(md_text):
    """
    Very simple fallback Markdown-to-HTML parser if `markdown` module isn't available.
    Supports basic bold, code blocks, inline code, and lists.
    """
    try:
        import markdown
        # Convert simple markdown to HTML using python-markdown
        html = markdown.markdown(md_text, extensions=['fenced_code', 'nl2br', 'sane_lists'])
        # Anki likes single lines in TSV, replace newlines with HTML breaks
        html = html.replace('\n', ' ')
        return html.strip().replace('\t', '    ')
    except ImportError:
        pass
        
    # Regex fallback implementation
    # Code blocks
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', md_text, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'__(.*?)__', r'<b>\1</b>', html)
    
    # Italic
    html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', html)
    html = re.sub(r'_(.*?)_', r'<i>\1</i>', html)
    
    # Lists (simple implementation)
    # Just replacing bullet with HTML, let Anki handle it or just use simple tags
    lines = html.split('\n')
    out_lines = []
    in_list = False
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                out_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:]
            out_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                out_lines.append('</ul>')
                in_list = False
            out_lines.append(line)
            
    if in_list:
        out_lines.append('</ul>')
        
    html = '<br>'.join(out_lines)
    html = html.replace('<br><ul>', '<ul>').replace('</ul><br>', '</ul>')
    html = html.replace('<li>', '<li>').replace('</li><br>', '</li>')
    html = html.replace('\n', ' ')
    
    return html.strip().replace('\t', '    ')

def process_file(filepath, dry_run):
    deck_name = os.path.splitext(os.path.basename(filepath))[0]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    cards = []
    
    # We can split by '### Card'
    parts = re.split(r'###\s+Card\s+\d+', content)
    
    # The first part is usually preamble, skip it
    for part in parts[1:]:
        # Front: text
        front_match = re.search(r'\*\*Front:\*\*(.*?)(?=\*\*Back:\*\*|\Z)', part, re.DOTALL | re.IGNORECASE)
        back_match = re.search(r'\*\*Back:\*\*(.*?)(?=\Z)', part, re.DOTALL | re.IGNORECASE)
        
        # In case the format is just "Front:" without bold
        if not front_match:
            front_match = re.search(r'(?:^|\n)\s*Front:(.*?)(?=(?:^|\n)\s*Back:|\Z)', part, re.DOTALL | re.IGNORECASE)
        if not back_match:
            back_match = re.search(r'(?:^|\n)\s*Back:(.*?)(?=\Z)', part, re.DOTALL | re.IGNORECASE)

        if front_match:
            front_text = front_match.group(1).strip()
            
            # Back can be empty
            back_text = back_match.group(1).strip() if back_match else ""
            
            cards.append((front_text, back_text))

    return deck_name, cards

def main():
    parser = argparse.ArgumentParser(description="Export Markdown flashcards to Anki TSV format.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files, just print what would be done.")
    parser.add_argument("--deck", type=str, help="Specify a single deck to export (e.g., 'hld-concepts').")
    
    args = parser.parse_args()
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    flashcards_dir = os.path.join(base_dir, 'flashcards')
    output_dir = os.path.join(flashcards_dir, 'anki-export', 'decks')
    
    if not args.dry_run:
        os.makedirs(output_dir, exist_ok=True)
        
    md_files = glob.glob(os.path.join(flashcards_dir, '*.md'))
    
    deck_files = []
    for f in md_files:
        basename = os.path.basename(f)
        if basename.lower() in ['readme.md', 'agents.md']:
            continue
        if args.deck and not basename.startswith(args.deck):
            continue
        deck_files.append(f)
        
    for filepath in deck_files:
        deck_name, cards = process_file(filepath, args.dry_run)
        
        if not cards:
            continue
            
        print(f"[{deck_name}] Found {len(cards)} cards")
        
        # Generate tags:
        tags = [deck_name.replace('-', '_')]
        if 'hld' in deck_name:
            tags.extend(['hld', 'system-design'])
        if 'lld' in deck_name or 'design-pattern' in deck_name:
            tags.extend(['lld', 'system-design'])
        if 'algo' in deck_name or deck_name in ['bfs-dfs', 'union-find', 'heap-priority-queue', 'trie', 'dynamic-programming', 'sliding-window', 'greedy', 'backtracking', 'two-pointers', 'binary-search']:
            tags.append('algorithms')
            
        tags_str = " ".join(set(tags)) # Deduplicate
        
        if args.dry_run:
            print(f"  (Dry run) Would write {len(cards)} cards to {deck_name}.tsv")
        else:
            out_file = os.path.join(output_dir, f"{deck_name}.tsv")
            with open(out_file, 'w', encoding='utf-8') as out:
                for front, back in cards:
                    html_front = parse_markdown_to_html(front)
                    html_back = parse_markdown_to_html(back)
                    out.write(f"{html_front}\t{html_back}\t{tags_str}\n")
            print(f"  Wrote {out_file}")

if __name__ == "__main__":
    main()
