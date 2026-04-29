#!/usr/bin/env python3
import os
import re
from pathlib import Path

def fix_header_line(line):
    """Fix a single 'By:' header line to have proper 80-char alignment"""
    if not line.startswith('/*   By:'):
        return line

    # Extract the by line components
    # Format should be: /*   By: omischle <omischle@student.42.fr>            +#+  +:+       +#+        */
    match = re.match(r'(/\*\s+By:\s+)(.+?)\s+(<.+?>)', line)
    if not match:
        return line

    prefix = match.group(1)  # '/*   By: '
    name = match.group(2)    # 'omischle'
    email = match.group(3)   # '<omischle@student.42.fr>'

    # The correct format with proper spacing to reach exactly 80 chars
    fixed = f"{prefix}{name} {email}            +#+  +:+       +#+        */"
    return fixed[:80]

def fix_created_line(line):
    """Fix the Created: line"""
    if not line.startswith('/*   Created:'):
        return line

    match = re.match(r'(/\*\s+Created:\s+)(.+?)(\s+by\s+)(.+?)(.*)$', line)
    if not match:
        return line

    prefix = match.group(1)
    date = match.group(2)
    by_part = match.group(3)
    author = match.group(4)

    # Fix format: /*   Created: YYYY/MM/DD HH:MM:SS by AUTHOR           #+#    #+#             */
    created = f"{prefix}{date}{by_part}{author}"
    # Pad to 80 chars with spaces before #+#
    fixed = created + ' ' * (73 - len(created)) + '#+#    #+#             */'
    return fixed[:80]

def fix_updated_line(line):
    """Fix the Updated: line"""
    if not line.startswith('/*   Updated:'):
        return line

    match = re.match(r'(/\*\s+Updated:\s+)(.+?)(\s+by\s+)(.+?)(.*)$', line)
    if not match:
        return line

    prefix = match.group(1)
    date = match.group(2)
    by_part = match.group(3)
    author = match.group(4)

    # Fix format: /*   Updated: YYYY/MM/DD HH:MM:SS by AUTHOR          ###   ########.fr       */
    updated = f"{prefix}{date}{by_part}{author}"
    # Pad to 80 chars with spaces before ###
    fixed = updated + ' ' * (72 - len(updated)) + '###   ########.fr       */'
    return fixed[:80]

def fix_header_alignment(content):
    """Fix all header alignment issues"""
    lines = content.split('\n')

    # Process lines looking for header lines
    for i, line in enumerate(lines):
        if i < 11:  # Header is in first 11 lines
            if line.startswith('/*   By:'):
                lines[i] = fix_header_line(line)
            elif line.startswith('/*   Created:'):
                lines[i] = fix_created_line(line)
            elif line.startswith('/*   Updated:'):
                lines[i] = fix_updated_line(line)

    return '\n'.join(lines)

def process_files():
    """Process all C and H files in the specified directories"""
    dirs = [
        '/home/omischle/42/tronc-commun-42/get_next_line',
        '/home/omischle/42/tronc-commun-42/ft_printf',
        '/home/omischle/42/tronc-commun-42/libft',
        '/home/omischle/42/tronc-commun-42/push_swap',
    ]

    files_to_process = []
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            files_to_process.extend(path.glob('*.c'))
            files_to_process.extend(path.glob('*.h'))

    print(f"Found {len(files_to_process)} files to process\n")

    fixed_count = 0
    for file_path in sorted(files_to_process):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original = f.read()

            fixed = fix_header_alignment(original)

            if original != fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                print(f"✓ Fixed: {file_path.name}")
                fixed_count += 1
        except Exception as e:
            print(f"✗ Error with {file_path.name}: {e}")

    print(f"\n✓ Total files fixed: {fixed_count}")
