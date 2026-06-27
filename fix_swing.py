import re

with open(r'C:\Users\DELL\Desktop\playwright-demo\coindcx-swing\coindcx_swing.py', 'r') as f:
    content = f.read()

content = content.replace('r["short_pct\']', "r['short_pct']")

keywords = [
    'import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ',
    'try:', 'except ', 'with ', 'return ', 'else:', 'elif ', 
    'finally:', 'raise ', 'break', 'continue', 'pass', 'yield ',
    'assert ', 'del ', 'global ', 'nonlocal ', 'lambda ',
]

for kw in keywords:
    content = re.sub(r'(?<!\n)' + re.escape(kw), r'\n' + kw, content)

content = content.lstrip('\n')
content = re.sub(r'\n{3,}', '\n\n', content)

with open(r'C:\Users\DELL\Desktop\playwright-demo\coindcx-swing\coindcx_swing.py', 'w') as f:
    f.write(content)

print("Swing bot fix done")
