const escapeHtml = (value) =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");

function tokenizeCode(raw) {
  const tokenPatterns = [
    { regex: /\/\/.*$|\/\*[\s\S]*?\*\//gm, cls: "comment" },
    { regex: /"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, cls: "string" },
    { regex: /\b(?:0x[0-9a-fA-F]+|\d+\.\d+|\d+)\b/g, cls: "number" },
    {
      regex: /\b(?:var|struct|enum|variant|extend|pub|static|return|fn|import|mod|new|if|else|while|for|loop|switch|defer|break|continue|true|false|null|main|println|printf|as|self|const|extern|trait|union|typedef|volatile|comptime)\b/g,
      cls: "keyword",
    },
    {
      regex: /\b(?:i8|i16|i32|i64|u8|u16|u32|u64|u128|i128|f32|f64|bool|void|usize|isize|str|char|rawptr|T|U|Color|Option|Some|None)\b/g,
      cls: "type",
    },
    {
      regex: /(?:\+\+|--|->|::|&&|\|\||<<|>>|==|!=|<=|>=|\+=|-=|\*=|\/=|%=|=|\+|-|\*|\/|%|<|>|!|~|:|;|,|\.|&|\^|\||\?|@|#)/g,
      cls: "operator",
    },
    { regex: /\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?=\()/g, cls: "function" },
  ];

  const combined = new RegExp(
    tokenPatterns.map(({ regex }) => `(${regex.source})`).join("|"),
    "g"
  );

  let result = "";
  let lastIndex = 0;

  for (const match of raw.matchAll(combined)) {
    const start = match.index;
    const end = start + match[0].length;

    if (start > lastIndex) {
      result += escapeHtml(raw.slice(lastIndex, start));
    }

    const matchedGroupIndex = match.slice(1).findIndex((value) => value !== undefined);
    const tokenClass = tokenPatterns[matchedGroupIndex]?.cls || "plain";
    result += `<span class="token ${tokenClass}">${escapeHtml(match[0])}</span>`;

    lastIndex = end;
  }

  if (lastIndex < raw.length) {
    result += escapeHtml(raw.slice(lastIndex));
  }

  return result;
}

function highlightCodeBlocks() {
  document.querySelectorAll("code.language-coral").forEach((code) => {
    const original = code.textContent || "";
    code.innerHTML = tokenizeCode(original);
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

document.addEventListener("DOMContentLoaded", () => {
  highlightCodeBlocks();
  bindCopyButtons();
  bindSearch();
});
