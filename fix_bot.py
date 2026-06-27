import re

with open(r'C:\Users\DELL\Desktop\playwright-demo\coindcx-bot\coindcx_bot.py', 'r') as f:
    content = f.read()

content = content.replace('r["short_pct\']', "r['short_pct']")

# Add newlines between import/from statements  
content = re.sub(r'(import [a-z_0-9]+)(from |import |def |class |if |for |while |try:|except |with |return |else:|elif |break|continue|pass|raise )', r'\1\n\2', content)
content = re.sub(r'(from [a-z_0-9.]+ import [a-z_0-9_, ]+)(from |import |def |class |if |for |while |try:|except |with |return |else:|elif |break|continue|pass|raise )', r'\1\n\2', content)

# After closing bracket/paren followed by keyword start
content = re.sub(r'(\)|]) *(def |class |if |for |while |try:|except |with |return |else:|elif |import |from |break|continue|pass|raise )', r'\1\n\2', content)

# After colon then new statement (but not inside dict literals)
content = re.sub(r':(def |class |if |for |while |try:|except |with |return |else:|elif |import |from )', r':\n\1', content)

# Handle ending bracket patterns  
content = re.sub(r'(?<=})\s*(?=def |class |if |for |while |try:|except |with |return |else:|elif |import |from )', r'\n', content)

# Remove leading/trailing whitespace per line
lines = content.split('\n')
lines = [l.strip() for l in lines]
lines = [l for l in lines if l]
content = '\n'.join(lines)

# Restore proper indentation by counting braces/colons
result = []
indent = 0
for line in content.split('\n'):
    dedent = 0
    # Check if this line causes dedent
    stripped = line.strip()
    if any(stripped.startswith(kw) for kw in ['return', 'break', 'continue', 'pass', 'elif ', 'else:', 'except ', 'finally:']):
        dedent = 1
    if stripped.startswith('except ') or stripped.startswith('elif ') or stripped.startswith('else:') or stripped.startswith('finally:'):
        # Same indent as matching if/for/try
        pass
    indent = max(0, indent - dedent)
    
    result.append('    ' * indent + stripped)
    
    if stripped.endswith(':') and not stripped.startswith('#'):
        indent += 1

content = '\n'.join(result)
content = content.replace('\n    \n', '\n\n')

with open(r'C:\Users\DELL\Desktop\playwright-demo\coindcx-bot\coindcx_bot.py', 'w') as f:
    f.write(content)

print("4H bot fix done")
