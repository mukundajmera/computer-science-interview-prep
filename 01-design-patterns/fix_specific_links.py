import os
import re

def fix_links():
    base_dir = "01-design-patterns"
    
    # We want to replace `[Something](./path/to/missing/)` with `Something (planned)`
    # Or replace `[Something](./path/to/missing)` with `Something (planned)`
    
    total_fixed = 0
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                replacements = []
                
                # Manual replacement for known missing directories
                missing_dirs = [
                    'java/v2-variant', 'java/v3-advanced', 
                    'python/v2-variant', 'python/v3-advanced',
                    'python/v2-pythonic'
                ]
                
                # Use regex to find links like `[Text](./java/v2-variant/)`
                # or `[Text](./python/v2-pythonic/)`
                link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
                links = link_pattern.findall(content)
                
                for text, link in links:
                    if any(missing in link for missing in missing_dirs):
                        # Construct the absolute path to check if it exists
                        link_path = link.split('#')[0]
                        if not link_path:
                            continue
                            
                        target_path = os.path.normpath(os.path.join(root, link_path))
                        if not os.path.exists(target_path):
                            replacements.append((f"[{text}]({link})", f"{text} (planned)"))
                
                if replacements:
                    # Remove duplicates
                    replacements = list(set(replacements))
                    for old, new in replacements:
                        content = content.replace(old, new)
                        
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    total_fixed += len(replacements)
                    print(f"Fixed {len(replacements)} links in {file_path}")

    print(f"Total links fixed: {total_fixed}")

if __name__ == '__main__':
    fix_links()
