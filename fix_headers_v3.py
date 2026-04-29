#!/usr/bin/env python3
import re
from pathlib import Path

def fix_file(filepath):
    """Fix a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    changed = False
    
    # Process first 11 lines (header)
    for i in range(min(12, len(lines))):
        old_line = lines[i]
        
        # Fix "By:" lines
        if lines[i].startswith('/*   By:'):
            match = re.match(r'(/\*\s+By:\s+)(.+?)\s+(<[^>]+>)', lines[i])
            if match:
                prefix = match.group(1)
                name = match.group(2)
                email = match.group(3)
                # By line is exactly: prefix + name + space + email + spaces + suffix
                new_line = f"{prefix}{name} {email}" + ' ' * 10 + '+#+  +:+       +#+        */'
                lines[i] = new_line
                if lines[i] != old_line:
                    changed = True
        
        # Fix "Created:" lines
        elif lines[i].startswith('/*   Created:'):
            match = re.match(r'(/\*\s+Created:\s+)(.+?)(\s+by\s+)(\w+)', lines[i])
            if match:
                prefix = match.group(1)
                date = match.group(2)
                by_part = match.group(3)
                author = match.group(4)
                new_line = f"{prefix}{date}{by_part}{author}" + ' ' * 10 + '#+#    #+#             */'
                lines[i] = new_line
                if lines[i] != old_line:
                    changed = True
        
        # Fix "Updated:" lines
        elif lines[i].startswith('/*   Updated:'):
            match = re.match(r'(/\*\s+Updated:\s+)(.+?)(\s+by\s+)(\w+)', lines[i])
            if match:
                prefix = match.group(1)
                date = match.group(2)
                by_part = match.group(3)
                author = match.group(4)
                new_line = f"{prefix}{date}{by_part}{author}" + ' ' * 9 + '###   ########.fr       */'
                lines[i] = new_line
                if lines[i] != old_line:
                    changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return True
    return False

# Process all files
dirs = [
    'tronc-commun-42/get_next_line',
    'tronc-commun-42/ft_printf',
    'tronc-commun-42/libft',
    'tronc-commun-42/push_swap',
]

files = []
for dir_path in dirs:
    path = Path(dir_path)
    if path.exists():
        files.extend(path.glob('*.c'))
        files.extend(path.glob('*.h'))

print(f"Processing {len(files)} files...")
fixed_count = 0

for filepath in sorted(files):
    if fix_file(filepath):
        print(f"✓ {filepath.name}")
        fixed_count += 1

print(f"\n✓ Total: {fixed_count}/{len(files)} files fixed")
