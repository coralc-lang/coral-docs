const bookRoot = new URL("./", document.currentScript.src);
const bookData = window.CORAL_BOOK || { parts: [] };
const parts = bookData.parts;

const sidebar = document.createElement("aside");
sidebar.className = "book-sidebar";
sidebar.setAttribute("aria-label", "Documentation navigation");

const group = (label, links) => {
  const section = document.createElement("section");
  section.className = "sidebar-section";
  const heading = document.createElement("div");
  heading.className = "section-label";
  heading.textContent = label;
  const list = document.createElement("ul");

  links.forEach(({ href, text, prefix, topics }) => {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = new URL(href, bookRoot).href;
    link.textContent = text;
    const currentPath = window.location.pathname.replace(/\/$/, "");
    const chapterPath = new URL(href, bookRoot).pathname.replace(/\/$/, "");
    const isChapterPage = currentPath === chapterPath;
    const isChapterSection = currentPath.startsWith(chapterPath.replace(/\/index\.html$/, "/sections/"));
    if (prefix && (isChapterPage || isChapterSection)) {
      link.classList.add("active");
      link.setAttribute("aria-current", isChapterPage ? "page" : "location");
    }
    item.append(link);
    if (topics && topics.length) {
      const details = document.createElement("details");
      details.className = "book-subtopics-wrap";
      const summary = document.createElement("summary");
      summary.textContent = "Topics";
      const list = document.createElement("ul");
      list.className = "book-subtopics";
      topics.forEach((topic) => {
        const subItem = document.createElement("li");
        if (typeof topic === "string") {
          subItem.textContent = topic;
        } else {
          const subLink = document.createElement("a");
          subLink.href = new URL(topic.href || `${href}#${topic.id}`, bookRoot).href;
          subLink.textContent = topic.title;
          if (topic.href && currentPath === new URL(topic.href, bookRoot).pathname.replace(/\/$/, "")) {
            subLink.classList.add("active");
            subLink.setAttribute("aria-current", "page");
            details.open = true;
          }
          subItem.append(subLink);
        }
        list.append(subItem);
      });
      details.append(summary, list);
      if (link.classList.contains("active")) {
        details.open = true;
      }
      item.append(details);
    }
    list.append(item);
  });

  section.append(heading, list);
  return section;
};

sidebar.append(
  group("Start here", [
    { href: "index.html", text: "Book contents", prefix: "/textbook/index.html" },
    { href: "../coral-docs/index.html", text: "Coral Docs home" },
  ]),
  ...parts.map((part) =>
    group(
      part.title,
      part.chapters.map(({ href, number, title, topics }) => ({
        href,
        text: number ? `${number} · ${title}` : title,
        prefix: `/textbook/${href}`,
        topics,
      }))
    )
  ),
  group("Coral Docs · Language", [
    { href: "../coral-docs/language/index.html", text: "Language notes" },
  ]),
  group("Coral Docs · Tooling", [
    { href: "../coral-docs/tooling/index.html", text: "Tooling overview" },
    { href: "../reference/tooling/EDITOR-API/index.html", text: "Editor API and Tree-sitter" },
    { href: "../reference/tooling/PROTOCOL/index.html", text: "Language-server protocol" },
  ])
);

document.body.classList.add("book-page");
document.body.prepend(sidebar);

const topbar = document.querySelector(".topbar");
if (topbar) {
  const menuButton = document.createElement("button");
  menuButton.className = "book-menu-button";
  menuButton.type = "button";
  menuButton.textContent = "Chapters";
  menuButton.setAttribute("aria-expanded", "false");
  menuButton.setAttribute("aria-controls", "book-navigation");
  sidebar.id = "book-navigation";
  topbar.prepend(menuButton);

  const backdrop = document.createElement("button");
  backdrop.className = "book-nav-backdrop";
  backdrop.type = "button";
  backdrop.setAttribute("aria-label", "Close chapter navigation");
  document.body.append(backdrop);

  const setOpen = (open) => {
    document.body.classList.toggle("book-nav-open", open);
    menuButton.setAttribute("aria-expanded", String(open));
    sidebar.style.transform = open ? "translateX(0)" : "";
    backdrop.style.opacity = open ? "1" : "";
    backdrop.style.pointerEvents = open ? "auto" : "";
    if (open) {
      sidebar.querySelector("a")?.focus();
    } else if (window.matchMedia("(max-width: 760px)").matches) {
      menuButton.focus();
    }
  };

  menuButton.addEventListener("click", () => {
    setOpen(!document.body.classList.contains("book-nav-open"));
  });
  backdrop.addEventListener("click", () => setOpen(false));
  sidebar.addEventListener("click", (event) => {
    if (event.target.closest("a")) setOpen(false);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
    if (event.key === "Tab" && document.body.classList.contains("book-nav-open")) {
      const focusable = [...sidebar.querySelectorAll("a, button, summary, [tabindex]:not([tabindex='-1'])")]
        .filter((element) => element.getClientRects().length > 0);
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first?.focus();
      }
    }
  });

  const contentsButton = document.createElement("button");
  contentsButton.className = "book-contents-button";
  contentsButton.type = "button";
  contentsButton.textContent = "Contents";
  contentsButton.setAttribute("aria-controls", "book-navigation");
  contentsButton.setAttribute("aria-expanded", "true");
  contentsButton.addEventListener("click", () => {
    if (window.matchMedia("(max-width: 760px)").matches) {
      setOpen(!document.body.classList.contains("book-nav-open"));
    } else {
      const collapsed = document.body.classList.toggle("book-nav-collapsed");
      contentsButton.setAttribute("aria-expanded", String(!collapsed));
    }
  });
  document.body.append(contentsButton);
}
