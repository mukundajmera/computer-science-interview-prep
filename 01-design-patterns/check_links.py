import os
import re
import sys

def check_links():
    base_dir = "01-design-patterns"
    broken_links = 0
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                links = link_pattern.findall(content)
                for text, link in links:
                    if link.startswith('http') or link.startswith('#'):
                        continue
                    
                    link_path = link.split('#')[0]
                    if not link_path:
                        continue
                        
                    target_path = os.path.normpath(os.path.join(root, link_path))
                    
                    if not os.path.exists(target_path):
                        print(f"Broken link in {file_path}: [{text}]({link}) -> {target_path}")
                        broken_links += 1
                        
    print(f"Found {broken_links} broken links.")
    if broken_links > 0:
        sys.exit(1)

if __name__ == '__main__':
    check_links()
