# Coral editor / language-server API

The contract between an editor and `coralc --serve`, plus the browser
tree-sitter artifacts for rendering Coral on this site.

Source of truth: `coralc/coral-docs/PROTOCOL.md` and
`coralc/coral-docs/LSP-SERVER-TODO.md`. This page is the site-facing summary.

---

## `coral.wasm` — Coral grammar for the browser

A tree-sitter language module for use with
[`web-tree-sitter`](https://github.com/tree-sitter/tree-sitter/tree/master/lib/binding_web).

| | |
| --- | --- |
| ABI | **14** |
| Export | `tree_sitter_coral` |
| Size | ~295 KB |
| Root node | `source_file` |
| Metadata | `coral.node-types.json` (185 KB) |

### Do not use the Zed build

The `coral.wasm` shipped in the Zed extension is **ABI 15** and is rejected by
web-tree-sitter:

```
Incompatible language version 15. Compatibility range 13 through 14.
```

Both files are side modules and look structurally identical — the difference is
only the generated parser ABI. Regenerate with:

```sh
/home/cerie/Documents/coral-zed/build-web.sh ./coral.wasm
```

That runs `tree-sitter generate --abi 14` into a temp directory, so the ABI 15
parser used by Zed is never touched. No downloads: `tree-sitter`, `clang` and
`wasm-ld` are all local.

### Loading it

web-tree-sitter must be initialised before any language module loads, and
`tree-sitter.wasm` (the runtime) has to be served alongside it.

The site vendors the whole set under `assets/tree-sitter/`:
`coral.wasm` (ABI 14), `tree-sitter.wasm` and `tree-sitter.js`
(web-tree-sitter **0.23.2**, the last line that accepts ABI 14), plus
`highlights.scm`. `assets/js/script.js` initialises it with
`locateFile` pointed at that directory and falls back to the regex
highlighter if the wasm fails to load.

```js
const Parser = window.TreeSitter;                     // vendored UMD build

await Parser.init({ locateFile: (f) => `./tree-sitter/${f}` });
const Coral = await Parser.Language.load(
  await (await fetch('./coral.wasm')).arrayBuffer()   // or new Uint8Array(buf)
);


const parser = new Parser();
parser.setLanguage(Coral);
const tree = parser.parse(source);
tree.rootNode.toString();                             // S-expression
```

`parser.parse()` returns `null` on timeout; guard for it if you want cancel
support.

### What the tree looks like

Nodes follow `coral.node-types.json`. Coral is **type-first**, so declarations
carry the type before the name:

```
(struct_declaration
  name: (identifier)
  (generic_params (generic_param (identifier)))
  body: (field_declaration_list …))
```

A few node names worth knowing, because they do not match Rust or C:

| Node | Meaning |
| --- | --- |
| `struct_declaration`, `union_declaration`, `variant_declaration`, `enum_declaration` | the type declarations |
| `trait_declaration`, `extend_declaration` | traits and extensions |
| `c_string` | a `C"…"` literal — distinct from `string_literal` |
| `base_type` wrapping `primitive_type` | `u32`, `bool`, … |
| `asm_statement` → `asm_template` / `asm_section` / `asm_operand` | inline assembly, broken out of the template strings and `:`-separated operand lists |
| `call_expression`, `path_expression`, `cast_expression` | ordinary calls, paths, casts |
| `attribute` | `#[[…]]` |
| `tuple_type` | `struct(A, B)` |

There is **no `fn` keyword** — functions are declared type-first, e.g.
`usize count() { return N; }` inside a struct body.

### Highlighting

`highlights.scm` from the Coral extension is a valid tree-sitter query and runs
in the browser, with one edit: the ABI-14 grammar has no `doc_comment` node, so
that single capture line is dropped from the vendored copy (the general
`comment` capture covers documentation comments instead).

```js
const query = new Parser.Query(Coral, highlightsScm);
for (const m of query.captures(tree.rootNode)) {
  // m.name, m.node.startIndex, m.node.endIndex
}
```

Capture names are the usual TextMate-style ones (`keyword`, `type`,
`function.method`, `string.special`, `punctuation.special`, …).

> **Ordering matters.** In this grammar the generic fallbacks — identifiers
> coloured by leading capitalisation, e.g. `^[A-Z]` → `@type` — must come
> **first** in the query file. Tree-sitter returns overlapping captures and the
> consumer keeps the last one, so a catch-all placed last swallows every
> specific rule. This is the single most common way a highlights query silently
> collapses to one colour.

### Known limitation

The grammar parses **384 of 406** real `.crl` files in the compiler tree
(94%). The remainder are concentrated in `wallvm` and involve qualified casts
such as `(a::B*)x` and multi-declarator `const` lists. It will not throw on
them — `rootNode.hasError` will be `true` — but do not assume a clean parse for
arbitrary Coral source yet.

---

## `coralc --serve` — the language server

JSON-RPC 2.0 over stdio with **standard LSP `Content-Length` framing** (not
newline-delimited). One object per frame, length in **bytes**.

```js
{ "Content-Length": 143 }\r\n
\r\n
{"jsonrpc":"2.0","id":1,"result":{…}}
```

Full protocol: `coralc/coral-docs/PROTOCOL.md`.

### Current state

Verified against the installed compiler.

| | |
| --- | --- |
| Capabilities | `textDocumentSync`, `hoverProvider`, `definitionProvider` |
| Working | diagnostics, hover, definition, `-32601` for the rest |
| Not implemented | `documentSymbol`, `semanticTokens`, `inlayHint`, `foldingRange`, `completion`, `signatureHelp`, `references` |

### Known gap worth knowing about

The language server does **not** currently surface errors that the CLI does.
Same file, same build, same session:

| file | error | `coralc FILE` | over LSP |
| --- | --- | --- | --- |
| parse error | `fn broken( {` | `P0001` | clean |
| semantic error | undeclared identifier | `T0001` | clean |

Reproduce:

```sh
printf 'fn broken( {\n}\n' > /tmp/only.crl
coralc /tmp/only.crl -o /tmp/x              # -> [P0001]
python3 .../tools/lsp-diagnostics.py /tmp/only.crl   # -> clean
```

If you are building anything that depends on server diagnostics for this site,
drive the compiler directly instead.

### Tooling

All in `/home/cerie/Documents/coral-vscode/tools/`:

| Command | Purpose |
| --- | --- |
| `node tools/lsp-probe.js FILE --method textDocument/hover` | probe any LSP method per position |
| `node tools/lsp-probe.js --list` | methods it can drive |
| `node tools/vscode-diagnostics.js FILE` | what VS Code renders |
| `python3 tools/lsp-diagnostics.py FILE` | raw wire payload |

```sh
cd /home/cerie/Documents/coral-vscode
node tools/lsp-probe.js /path/to/file.crl --method textDocument/hover
node tools/vscode-diagnostics.js /path/to/file.crl
python3 tools/lsp-diagnostics.py /path/to/file.crl
```

`lsp-probe.js` prints resolved positions then the unresolved tokens, which is
the fastest way to find out what a given build actually understands.

---

## Building it yourself

```sh
# browser wasm (ABI 14)
/home/cerie/Documents/coral-zed/build-web.sh ./coral.wasm

# Zed extension, which also regenerates the ABI 15 wasm
cd /home/cerie/Documents/coral-zed && ./build.sh
```