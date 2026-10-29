#!/usr/bin/env python3
from pathlib import Path
import html, re, sys
root = Path(__file__).resolve().parents[2]
source_files = list((root / 'Sources').glob('*/EditorInput.swift'))
if len(source_files) != 1:
    raise SystemExit(f'Expected one EditorInput.swift source, found {len(source_files)}')
source = source_files[0].read_text()
docs_path = Path(__file__).resolve().parents[1] / 'docs/index.html'
docs = docs_path.read_text()

def block(start, end):
    return source.split(start, 1)[1].split(end, 1)[0]

def pairs(text):
    return dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', text))

function_names = set(re.findall(r'"([A-Za-z0-9]+)"', block('public static let functionNames:', ']')))
function_help = pairs(block('private static let functionHelp:', 'private static func unitHelp'))
unit_help = pairs(block('let names: [String: String] = [', ']\n        return names'))
missing_functions = sorted(function_names - function_help.keys())
if missing_functions:
    raise SystemExit('Missing function help: ' + ', '.join(missing_functions))

function_rows = ''.join(
    f'<tr data-symbol="{html.escape(name)}"><td><code>{html.escape(name)}()</code></td><td>{html.escape(function_help[name])}</td></tr>'
    for name in sorted(function_names)
)
unit_rows = ''.join(
    f'<tr data-symbol="{html.escape(name)}"><td><code>{html.escape(name)}</code></td><td>{html.escape(description)}</td></tr>'
    for name, description in sorted(unit_help.items(), key=lambda item: item[0].casefold())
)

def replace_generated(text, marker, rows):
    pattern = rf'(<!-- GENERATED_{marker}_START -->).*?(<!-- GENERATED_{marker}_END -->)'
    return re.sub(pattern, rf'\1{rows}\2', text, flags=re.S)

docs = replace_generated(docs, 'FUNCTION_REFERENCE', function_rows)
docs = replace_generated(docs, 'UNIT_REFERENCE', unit_rows)
docs_path.write_text(docs)

# Coverage is machine-readable and intentionally checks the shipped page, not a separate manifest.
rendered = docs_path.read_text()
missing = [f'function {name}' for name in sorted(function_names) if f'data-symbol="{name}"' not in rendered]
missing += [f'unit {name}' for name in unit_help if f'data-symbol="{html.escape(name)}"' not in rendered]
if missing:
    raise SystemExit('Documentation coverage missing: ' + ', '.join(missing))
print(f'Documented {len(function_names)} functions and {len(unit_help)} unit symbols.')
