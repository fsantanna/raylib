#!/usr/bin/env python3
# Counts the lines of code (not blank, not only comments) and the tokens of
# C and Atmos files:
#
#   tools/count.py <files>...     prints: lines tokens
#
# C: the blocks of `#if defined(PLATFORM_WEB)` and `PLATFORM_ANDROID` are
# left out (their `#else` is kept), since the port has no such platforms.
# Atmos: the lines between `;; [trace]` and `;; [/trace]` are left out, since
# the trace only serves the comparison with the original. Strings and native
# literals count as one token each, except a block of C between ```, which
# counts as C.

import re, sys

def strip_platforms(src):
    out, stack = [], []         # stack: (skipping this branch, in a platform if)
    for line in src.split('\n'):
        s = line.strip()
        m = re.match(r'#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)', s)
        plat = m and re.search(r'PLATFORM_(WEB|ANDROID)', m.group(2) or '')
        if m and m.group(1) in ('if', 'ifdef', 'ifndef'):
            stack.append((bool(plat) and m.group(1) != 'ifndef', bool(plat)))
            if plat: continue
        elif m and m.group(1) in ('elif', 'else') and stack and stack[-1][1]:
            stack[-1] = (not stack[-1][0] if m.group(1) == 'else' else True, True)
            continue
        elif m and m.group(1) == 'endif' and stack:
            if stack.pop()[1]: continue
        if any(skip for skip, _ in stack):
            continue
        out.append(line)
    return '\n'.join(out)

C_TOK = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_]\w*|\d[\w.]*|->|\+\+|--|<<=|>>=|<=|>=|==|!=|&&|\|\||[-+*/%&|^]=|<<|>>|\S')
A_TOK = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`[^`]*`|:[A-Za-z0-9_.]+|[A-Za-z_]\w*|\d[\w.]*|<--|-->|<-|->|\+\+|==|!=|\?\?|!\?|<=|>=|&&|\|\||//|=>|::|\.\.\.|<<|>>|\S')

def c_count(src):
    src = strip_platforms(src)
    src = re.sub(r'/\*.*?\*/', lambda m: '\n' * m.group(0).count('\n'), src, flags=re.S)
    src = re.sub(r'//[^\n]*', '', src)
    lines = [l for l in src.split('\n') if l.strip()]
    return len(lines), len(C_TOK.findall('\n'.join(lines)))

def atm_count(src):
    src = re.sub(r';; \[trace\].*?;; \[/trace\]', '', src, flags=re.S)
    # a block of C in a port (```:prelude ... ```) counts as C
    nl = nt = 0
    for m in re.finditer(r'```(?::prelude)?(.*?)```', src, flags=re.S):
        l, t = c_count(m.group(1))
        nl += l; nt += t
    src = re.sub(r'```.*?```', lambda m: '\n' * m.group(0).count('\n'), src, flags=re.S)
    src = re.sub(r'(;;;+)\n.*?\n\1', lambda m: '\n' * m.group(0).count('\n'), src, flags=re.S)
    src = re.sub(r';;[^\n]*', '', src)
    lines = [l for l in src.split('\n') if l.strip()]
    return len(lines) + nl, len(A_TOK.findall('\n'.join(lines))) + nt

L = T = 0
for f in sys.argv[1:]:
    src = open(f, encoding='latin-1').read()
    l, t = (atm_count if f.endswith('.atm') else c_count)(src)
    L += l; T += t
print(L, T)
