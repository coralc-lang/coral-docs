const escapeHtml = (value) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");

const SCRIPT_SRC = document.currentScript && document.currentScript.src;
const TREE_SITTER_BASE = SCRIPT_SRC ? new URL("../tree-sitter/", SCRIPT_SRC).href : null;

function captureClass(name) {
  if (name.startsWith("comment")) return "comment";
  if (name.startsWith("string")) return "string";
  if (name.startsWith("number")) return "number";
  if (name === "keyword" || name.startsWith("keyword.")) return "keyword";
  if (name === "type" || name.startsWith("type.")) return "type";
  if (name.startsWith("function")) return "function";
  if (name.startsWith("operator")) return "operator";
  return null;
}

function highlightWithTreeSitter(sitter, codeEls) {
  codeEls.forEach((code) => {
    const source = code.textContent || "";
    const tree = sitter.parser.parse(source);
    if (!tree) return;
    const spans = [];
    for (const capture of sitter.query.captures(tree.rootNode)) {
      const cls = captureClass(capture.name);
      if (!cls) continue;
      spans.push({ start: capture.node.startIndex, end: capture.node.endIndex, cls });
    }
    spans.sort((a, b) => a.start - b.start || b.end - a.end);
    let result = "";
    let cursor = 0;
    for (const span of spans) {
      if (span.start < cursor) continue;
      result += escapeHtml(source.slice(cursor, span.start));
      result += `<span class="token ${span.cls}">${escapeHtml(source.slice(span.start, span.end))}</span>`;
      cursor = span.end;
    }
    result += escapeHtml(source.slice(cursor));
    code.innerHTML = result;
  });
}

function loadTreeSitter() {
  if (!TREE_SITTER_BASE) return Promise.resolve(null);
  return new Promise((resolve) => {
    const runtime = document.createElement("script");
    runtime.src = `${TREE_SITTER_BASE}tree-sitter.js`;
    runtime.onload = () => resolve(window.TreeSitter || window.Parser || null);
    runtime.onerror = () => resolve(null);
    document.head.append(runtime);
  }).then(async (Parser) => {
    if (!Parser || typeof Parser.init !== "function") {
      console.warn("[coral] tree-sitter runtime could not be loaded");
      return null;
    }
    try {
      await Parser.init({ locateFile: (file) => `${TREE_SITTER_BASE}${file}` });
      const [wasm, scm] = await Promise.all([
        fetch(`${TREE_SITTER_BASE}coral.wasm`).then((r) => r.arrayBuffer()),
        fetch(`${TREE_SITTER_BASE}highlights.scm`).then((r) => r.text()),
      ]);
      const Coral = await Parser.Language.load(new Uint8Array(wasm));
      const parser = new Parser();
      parser.setLanguage(Coral);
      return { parser, query: Coral.query(scm) };
    } catch (error) {
      console.warn("[coral] tree-sitter highlighting failed", error);
      return null;
    }
  });
}

function bindCopyButtons() {
  document.querySelectorAll(".copy-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      const codeBlock = button.parentElement.querySelector("code");
      if (!codeBlock) return;

      const text = codeBlock.textContent || "";

      try {
        await navigator.clipboard.writeText(text);
        const original = button.textContent;
        button.textContent = "Copied";
        button.disabled = true;

        setTimeout(() => {
          button.textContent = original;
          button.disabled = false;
        }, 1200);
      } catch (error) {
        button.textContent = "Error";
        setTimeout(() => {
          button.textContent = "Copy";
        }, 1200);
      }
    });
  });
}

function bindSearch() {
  const searchInput = document.querySelector(".search-box input");
  if (!searchInput) return;

  const searchableLinks = document.querySelectorAll(".sidebar a, .topnav a, .toc a");

  searchInput.addEventListener("input", (event) => {
    const query = event.target.value.trim().toLowerCase();

    searchableLinks.forEach((link) => {
      const text = link.textContent.toLowerCase();
      const match = !query || text.includes(query);
      const item = link.closest("li");

      if (item) item.hidden = !match;
    });
  });
}

document.addEventListener("DOMContentLoaded", async () => {
  if (window.location.pathname.includes("/textbook/")) {
    const textbookRoot = `${window.location.pathname.split("/textbook/")[0]}/textbook/`;
    const dataScript = document.createElement("script");
    dataScript.src = `${textbookRoot}book-data.js`;
    dataScript.onload = () => {
      const navigationScript = document.createElement("script");
      navigationScript.src = `${textbookRoot}book-nav.js`;
      document.body.append(navigationScript);
    };
    document.body.append(dataScript);
  }

  const codeEls = document.querySelectorAll("code.language-coral");
  if (codeEls.length) {
    const sitter = await loadTreeSitter();
    if (sitter) highlightWithTreeSitter(sitter, codeEls);
  }
  bindCopyButtons();
  bindSearch();
});
