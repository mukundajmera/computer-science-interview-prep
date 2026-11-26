import os
import re

def verify_links():
    base_dir = "01-design-patterns"
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                links = link_pattern.findall(content)
                for text, link in links:
                    if 'v2-variant' in link or 'v3-advanced' in link:
                        print(f"Found link: [{text}]({link}) in {file_path}")

if __name__ == '__main__':
    verify_links()
