import re
import sys

# Read the corrupted file
with open(r'C:\Users\DELL\Desktop\playwright-demo\coindcx-bot\coindcx_bot.py', 'r') as f:
    content = f.read()

# Fix the quote
content = content.replace('r["short_pct\']', "r['short_pct']")

# Strategy: Find all statements by looking at Python structure.
# Since the file is one line, we need to handle it differently.
# Let's use tokenize to properly insert newlines.

import io
import tokenize

# Remove all existing newlines first
content = content.replace('\n', ' ').replace('\r', ' ')

tokens = []
try:
    for tok in tokenize.generate_tokens(io.StringIO(content).readline):
        tokens.append(tok)
except:
    pass

if not tokens:
    print("Tokenization failed, using regex approach")
    sys.exit(1)

# Reconstruct with proper newlines
result_lines = []
current_line = ""
prev_end = 0
indent_level = 0
block_stack = []  # track indent levels for blocks

for tok in tokens:
    if tok.type in (tokenize.ENDMARKER, tokenize.NEWLINE, tokenize.NL):
        continue
    if tok.type == tokenize.INDENT:
        indent_level += 1
        continue
    if tok.type == tokenize.DEDENT:
        indent_level -= 1
        current_line = current_line.rstrip()
        if current_line:
            result_lines.append(current_line)
        current_line = ""
        continue
    
    # Check if this token starts a new statement
    if current_line and tok.start[0] > prev_end:
        result_lines.append(current_line)
        current_line = "    " * indent_level
    
    current_line += tok.string
    prev_end = tok.end[0]

if current_line:
    result_lines.append(current_line)

# Join and clean
content = '\n'.join(result_lines)
content = re.sub(r'\n{3,}', '\n\n', content)

with open(r'C:\Users\DELL\Desktop\playwright-demo\coindcx-bot\coindcx_bot.py', 'w') as f:
    f.write(content)

print("4H bot fix done via tokenizer")
