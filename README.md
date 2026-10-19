# Coral Docs Site

Static website for Coral's current documentation and the separate Coral Textbook
project. The site landing page is the generated root `index.html`; the book landing
page is `textbook/index.html`, and individual lessons live in numbered chapter
folders. The site is published as plain static files (see `.nojekyll`), not rendered
by Jekyll.

## Install the compiler

The compiler is `coralc`, installed with one command per platform.

Linux — needs `git`, `make`, and a C compiler (`cc`):

```sh
curl -fsSL https://raw.githubusercontent.com/coralc-lang/coralc/main/install.sh | sh
```

Windows (PowerShell) — needs `git` and `gcc` (w64devkit or mingw-w64); `make` is
used when present:

```powershell
irm https://raw.githubusercontent.com/coralc-lang/coralc/main/install.ps1 | iex
```

Both install to `~/.coral/bin` + `~/.coral/lib` (`%USERPROFILE%\.coral\bin` on
Windows) and add `bin` to `PATH`; restart the shell afterwards. Override with
`CORAL_HOME=...` / `--prefix` (or `-Prefix`). The site page is
`coral-docs/getting-started/index.html`.

## Folder map

```text
docs-site/
|-- textbook/
|   |-- index.html                Book contents and getting-started guide
|   |-- book-nav.js               Shared chapter navigation
|   |-- book.css                  Book layout and chapter styles
|   `-- 01-.../ through 10-.../   Individual chapter pages
|-- coral-docs/                   Language and tooling documentation pages
|-- templates/
|   `-- base.html                 Reusable page shell
|-- assets/
|   |-- css/                      Base and prototype stylesheets
|   |-- js/                       Base and prototype behavior
|   `-- tree-sitter/              Coral parser artifacts for browser highlighting
`-- reference/
    `-- tooling/                  Editor API and language-server protocol notes
```

The content sources remain in the repository's separate `coral-docs/` and
`textbook/` directories. Coral Docs is topic-based and miscellaneous; the textbook
is a sequential book draft and is substantially outdated. The future site should
keep them as separate navigation areas and show content status clearly.

## Tree-sitter browser highlighting

The browser parser artifacts are now present:

- `assets/tree-sitter/coral.wasm`: Coral grammar module, ABI 14, for `web-tree-sitter`.
- `assets/tree-sitter/coral.node-types.json`: generated grammar node metadata.
- [`reference/tooling/EDITOR-API.md`](reference/tooling/EDITOR-API.md): loading,
  grammar shape, captures, limitations, and language-server status.

The artifacts are not yet wired into the page. Remaining work is to vendor or
otherwise serve a compatible `web-tree-sitter` runtime and `tree-sitter.wasm`, load
the grammar, and apply the Coral highlights query to code blocks. Use the ABI-14
browser build described in the editor API notes; the Zed extension's ABI-15 parser
is incompatible with the browser runtime described there.

## Current prototype

Open `textbook/index.html` directly, or serve the repository root and visit
`/docs-site/textbook/`. The shared shell in `templates/base.html` uses template
blocks and is a blueprint, not standalone rendered HTML. The textbook chapter pages
are real HTML content; their source manuscript remains in the repository's separate
`textbook/` directory for editorial reference.
