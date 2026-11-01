import os
import re

targets = ['/opt/odoo/addons', '/opt/odoo/odoo', '/mnt/custom-addons']

count = 0
for target in targets:
    if os.path.exists(target):
        for root, dirs, files in os.walk(target):
            # Skip node_modules or .git
            if 'node_modules' in dirs:
                dirs.remove('node_modules')
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if file.endswith(('.py', '.js', '.xml', '.html')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        new_content = content
                        new_content = re.sub(r'https?://(www\.)?odoo\.com', 'https://monerp.com', new_content)
                        new_content = re.sub(r'https?://accounts\.odoo\.com', 'https://monerp.com', new_content)
                        
                        if new_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            count += 1
                    except Exception as e:
                        pass

print(f"REPLACED_LINKS_IN_{count}_FILES")
