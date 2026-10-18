const escapeHtml = (value) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");

function tokenizeCode(raw) {
  const patterns = [
    ["comment", /\/\/[^\n]*|\/\*[\s\S]*?\*\//],
    ["string", /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/],
    ["number", /\b(?:0x[0-9a-fA-F]+|\d+\.\d+|\d+)\b/],
    [
      "keyword",
      /\b(?:var|struct|enum|variant|extend|pub|static|return|fn|import|mod|new|if|else|while|for|loop|switch|def|defer|break|continue|true|false|null|println|printf|self|const|extern|trait|union|volatile|comptime|any|where|match|case)\b/,
    ],
    [
      "type",
      /\b(?:i8|i16|i32|i64|i128|u8|u16|u32|u64|u128|f32|f64|bool|void|usize|isize|str|char|rawptr|String|Vec|Option|Result)\b/,
    ],
    ["function", /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/],
    ["operator", /->|::|\.\.\.|[+\-*/%=<>!&|^~?:@#]/],
    ["punctuation", /[{}()\[\];,.]/],
  ];

  const master = new RegExp(
    patterns.map(([, re]) => `(${re.source})`).join("|"),
    "gm"
  );

  let result = "";
  let last = 0;
  let match;
  while ((match = master.exec(raw)) !== null) {
    if (match.index > last) result += escapeHtml(raw.slice(last, match.index));
    const idx = match.slice(1).findIndex((value) => value !== undefined);
    const cls = idx >= 0 ? patterns[idx][0] : "plain";
    result += `<span class="token ${cls}">${escapeHtml(match[0])}</span>`;
    last = match.index + match[0].length;
    if (match[0].length === 0) master.lastIndex += 1;
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

  highlightCodeBlocks();
  bindCopyButtons();
  bindSearch();
});
