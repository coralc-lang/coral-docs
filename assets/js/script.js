const escapeHtml = (value) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");

const CORAL_KEYWORDS = new Set([
  "var", "struct", "enum", "variant", "extend", "pub", "static", "return",
  "fn", "import", "mod", "new", "if", "else", "while", "for", "loop",
  "switch", "defer", "break", "continue", "true", "false", "null", "self",
  "const", "extern", "trait", "union", "volatile", "comptime", "any",
  "where", "match", "case", "default", "typeof",
]);

const CORAL_TYPES = new Set([
  "i8", "i16", "i32", "i64", "i128", "u8", "u16", "u32", "u64", "u128",
  "usize", "isize", "f32", "f64", "bool", "void", "str", "char", "rawptr",
]);

const CORAL_ATOM =
  /\/\/[^\n]*|\/\*[\s\S]*?\*\/|#\[\[[\s\S]*?\]\]|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|0[xX][0-9a-fA-F][0-9a-fA-F_]*|0[bB][01][01_]*|\d[\d_]*(?:\.[\d_]+)?(?:[eE][+-]?\d+)?|@[A-Za-z_]\w*|[A-Za-z_]\w*|->|::|\.\.\.|\+\+|--|&&|\|\||[=!<>]=|[+\-*/%=<>!&|^~?:@#]|[{}()\[\];,.]/g;

function classifyToken(raw, text, after) {
  if (text.startsWith("//") || text.startsWith("/*")) return "comment";
  if (text.startsWith("#[[")) return "attribute";
  if (text[0] === '"' || text[0] === "'") return "string";
  if (text[0] >= "0" && text[0] <= "9") return "number";
  if (text[0] === "@") return "builtin";
  if (/[A-Za-z_]/.test(text[0])) {
    if (CORAL_KEYWORDS.has(text)) return "keyword";
    if (CORAL_TYPES.has(text)) return "type";
    if (/^[A-Z]/.test(text)) return "type";
    return /^\s*\(/.test(after) ? "function" : "";
  }
  if (/[{}()\[\];,.]/.test(text)) return "punctuation";
  return "operator";
}

function tokenizeCode(raw) {
  const scanner = new RegExp(CORAL_ATOM.source, "g");
  let result = "";
  let last = 0;
  let match;
  while ((match = scanner.exec(raw)) !== null) {
    const text = match[0];
    if (match.index > last) result += escapeHtml(raw.slice(last, match.index));
    const cls = classifyToken(raw, text, raw.slice(scanner.lastIndex));
    result += cls
      ? `<span class="token ${cls}">${escapeHtml(text)}</span>`
      : escapeHtml(text);
    last = scanner.lastIndex;
    if (text.length === 0) scanner.lastIndex += 1;
  }
  if (last < raw.length) result += escapeHtml(raw.slice(last));
  return result;
}

function highlightCodeBlocks() {
  document.querySelectorAll("code.language-coral").forEach((code) => {
    code.innerHTML = tokenizeCode(code.textContent || "");
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
  if (window.location.pathname.includes("/lengthy/")) {
    const textbookRoot = `${window.location.pathname.split("/lengthy/")[0]}/lengthy/`;
    const dataScript = document.createElement("script");
    dataScript.src = `${textbookRoot}book-data.js`;
    dataScript.onload = () => {
      const navigationScript = document.createElement("script");
      navigationScript.src = `${textbookRoot}book-nav.js`;
      document.body.append(navigationScript);
    };
    document.body.append(dataScript);
  }

  highlightCodeBlocks();
  bindCopyButtons();
  bindSearch();
});
