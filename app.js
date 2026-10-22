/* McTrailer web demo — renders a cinema poster on <canvas> and exports PNG.
 * Three entry modes so ANYONE can play (no GitHub needed):
 *   1) scene  — tap a genre card, instant poster
 *   2) text   — type one line, auto-classified into a genre
 *   3) repo   — paste a public GitHub repo URL (advanced)
 * Deterministic genre/script logic mirrors skills/mctrailer/scripts/*.py.
 * Browser cannot hold the MCP token, so this page is DEMO-ONLY and every
 * poster is labelled "演示样例 · 非实时核价". Live menu/price runs via the
 * local CLI / WorkBuddy Skill with MCD_MCP_TOKEN.
 */
(function () {
  "use strict";

  const GENRES = {
    fixing_a_bug: { genre_cn: "悬疑 · Fixing a Bug", film: "《{name}：第 37 次修复》", line: "“第 37 次修复，终于通过。”", palette: "noir", prop: "深夜的屏幕微光，是悬疑片最好的打光。" },
    release_day: { genre_cn: "动作 · Release Day", film: "《{name}：部署前 15 分钟》", line: "“倒计时开始，谁也别拦我上线。”", palette: "action", prop: "发布会前的最后 15 分钟，比动作片更刺激。" },
    refactor_marathon: { genre_cn: "科幻 · Refactor Marathon", film: "《{name}：重构纪元》", line: "“重构不是毁灭，而是新生。”", palette: "scifi", prop: "当旧架构化作星尘，新世界从 commit 里升起。" },
    side_project: { genre_cn: "公路 · Side Project", film: "《{name}：一个人的公路》", line: "“踩下油门，去向只有代码知道。”", palette: "road", prop: "没有 KPI 的周末，一个 side project 就是整条公路。" }
  };
  const KEYWORDS = {
    fixing_a_bug: ["bug", "fix", "patch", "debug", "hotfix", "regression", "crash", "panic", "traceback", "issue", "segfault", "leak", "半夜", "凌晨", "修"],
    release_day: ["release", "version", "deploy", "launch", "ship", "publish", "changelog", "tag", "v1", "v2", "v3", "stable", "beta", "上线", "发布", "发版"],
    refactor_marathon: ["refactor", "rewrite", "architecture", "migrate", "optimize", "performance", "overhaul", "cleanup", "monorepo", "重构", "优化", "迁移"],
    side_project: ["experiment", "toy", "playground", "weekend", "side", "personal", "learning", "demo", "template", "awesome", "hello", "starter", "boilerplate", "副业", "周末", "玩", "学习", "躺"]
  };
  const PRIORITY = ["fixing_a_bug", "release_day", "refactor_marathon", "side_project"];
  const PALETTES = {
    noir: { bg1: "#14141a", bg2: "#05050a", accent: "#e5c07b", chip: "#2a2a33" },
    action: { bg1: "#1e0f0d", bg2: "#0a0403", accent: "#ff5f45", chip: "#331a15" },
    scifi: { bg1: "#07202e", bg2: "#02080f", accent: "#4fd1ff", chip: "#0f3040" },
    road: { bg1: "#1e1608", bg2: "#0a0703", accent: "#ffb347", chip: "#33260f" }
  };
  const EMBEDDED = {
    demo_meals: [
      { name: "巨无霸", price: 24.5, components: ["双层牛肉饼", "芝士", "生菜"] },
      { name: "麦辣鸡腿堡套餐", price: 32.0, components: ["麦辣鸡腿堡", "薯条", "可乐"] },
      { name: "板烧鸡腿堡", price: 21.0, components: ["板烧鸡腿排", "生菜", "烧汁"] },
      { name: "“我就喜欢”鸡薯双全盒", price: 15.9, components: ["心形薯饼", "麦乐鸡", "风味酱"] }
    ],
    presets: [
      { repo_url: "https://github.com/psf/requests", label: "psf/requests", genre: "side_project", meal_index: 0 },
      { repo_url: "https://github.com/vuejs/vue", label: "vuejs/vue", genre: "refactor_marathon", meal_index: 1 },
      { repo_url: "https://github.com/facebook/react", label: "facebook/react", genre: "release_day", meal_index: 2 },
      { repo_url: "https://github.com/home-assistant/core", label: "home-assistant/core", genre: "fixing_a_bug", meal_index: 3 }
    ]
  };

  // ---- helpers -----------------------------------------------------------
  function classify(text) {
    const blob = (" " + (text || "") + " ").toLowerCase();
    const scores = {};
    for (const g of PRIORITY) scores[g] = KEYWORDS[g].reduce((n, k) => n + blob.split(k).length - 1, 0);
    const best = Math.max(...PRIORITY.map((g) => scores[g]));
    if (best <= 0) return "side_project";
    return PRIORITY.find((g) => scores[g] === best) || "side_project";
  }
  function parseRepo(url) {
    const m = /^https?:\/\/github\.com\/([^/\s]+)\/([^/\s#?]+)/.exec((url || "").trim());
    return m ? m[2].replace(/\.git$/, "") : (url || "unknown").split("/").pop() || "unknown";
  }
  // kind: 'scene' | 'text' | 'repo'
  function buildScript(kind, value, forcedGenre) {
    let name = "", text = value || "";
    if (kind === "repo") name = parseRepo(value);
    const genre = forcedGenre || classify(text || name);
    const t = GENRES[genre] || GENRES.side_project;
    let title = t.film;
    if (name) title = title.replace("{name}", name);
    else title = title.replace("《{name}：", "《").replace("{name}", "");
    return {
      film_title: title,
      opening_line: t.line,
      protagonist: "独立开发者",
      prop_line: t.prop,
      palette: t.palette,
      genre_cn: t.genre_cn,
      user_quote: (kind === "text" && value) ? String(value).slice(0, 42) : "",
      stats: (kind === "repo") ? { language: "未知语言", stars_phrase: "demo stars" } : null,
      repo_url: (kind === "repo") ? value : "",
      kind: kind
    };
  }
  function wrap(text, per) {
    text = String(text || "");
    const out = [];
    for (let i = 0; i < text.length; i += per) out.push(text.slice(i, i + per));
    return out.length ? out : [""];
  }
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  function hash(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return h; }

  // ---- poster render (720 x 1080) ---------------------------------------
  const W = 720, H = 1080;
  function renderPoster(script, meal, live) {
    const cv = document.getElementById("poster");
    const ctx = cv.getContext("2d");
    const p = PALETTES[script.palette] || PALETTES.road;
    ctx.clearRect(0, 0, W, H);

    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, p.bg1); g.addColorStop(1, p.bg2);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = p.accent; ctx.globalAlpha = 0.35; ctx.lineWidth = 2;
    roundRect(ctx, 28, 28, W - 56, H - 56, 10); ctx.stroke(); ctx.globalAlpha = 1;
    ctx.fillStyle = p.accent; roundRect(ctx, 28, 28, W - 56, 8, 4); ctx.fill();

    ctx.fillStyle = p.chip; roundRect(ctx, 56, 66, 250, 40, 20); ctx.fill();
    ctx.fillStyle = p.accent; ctx.font = "22px sans-serif"; ctx.textAlign = "left";
    ctx.fillText(script.genre_cn, 78, 92);
    ctx.fillStyle = live ? "#1f7a4d" : "#4a4a52";
    roundRect(ctx, W - 56 - 190, 66, 190, 40, 20); ctx.fill();
    ctx.fillStyle = "#fff"; ctx.font = "17px sans-serif";
    ctx.fillText(live ? "实时 MCP · 官方菜单" : "演示样例 · 非实时核价", W - 56 - 172, 92);

    ctx.fillStyle = p.accent; ctx.font = "20px sans-serif";
    ctx.fillText("McTrailer · 麦门导演局", 56, 152);

    let y = 250; ctx.fillStyle = "#fff"; ctx.font = "700 52px sans-serif";
    wrap(script.film_title, 9).forEach((ln, i) => { if (i > 0) y += 62; ctx.fillText(ln, 56, y); });

    y += 66; ctx.fillStyle = p.accent; ctx.font = "italic 26px sans-serif";
    wrap(script.opening_line, 16).forEach((ln) => { ctx.fillText(ln, 56, y); y += 36; });

    // user's own words (text mode) as a personal quote
    if (script.user_quote) {
      y += 6; ctx.fillStyle = "#8a8a9a"; ctx.font = "italic 18px sans-serif";
      wrap("— " + script.user_quote + " —", 20).forEach((ln) => { ctx.fillText(ln, 56, y); y += 26; });
    }

    y += 26; ctx.fillStyle = p.chip; ctx.strokeStyle = p.accent; ctx.globalAlpha = 0.9;
    roundRect(ctx, 56, y - 30, 320, 44, 22); ctx.fill(); ctx.globalAlpha = 1;
    ctx.fillStyle = "#fff"; ctx.font = "22px sans-serif";
    ctx.fillText("主角：" + script.protagonist, 78, y);

    y += 58; ctx.fillStyle = "#c9c9d2"; ctx.font = "20px sans-serif";
    wrap(script.prop_line, 18).forEach((ln) => { ctx.fillText(ln, 56, y); y += 30; });

    if (script.stats) {
      y += 20; ctx.fillStyle = "#9a9aa6"; ctx.font = "20px sans-serif";
      ctx.fillText("主语言 " + script.stats.language + " · " + script.stats.stars_phrase, 56, y);
    } else {
      y += 20; ctx.fillStyle = "#6f6f80"; ctx.font = "18px sans-serif";
      ctx.fillText("— 麦门导演局 · 今日放映 —", 56, y);
    }

    const cy = H - 300;
    ctx.fillStyle = "rgba(0,0,0,0.35)"; roundRect(ctx, 48, cy, W - 96, 200, 16); ctx.fill();
    ctx.strokeStyle = p.accent; ctx.globalAlpha = 0.5; roundRect(ctx, 48, cy, W - 96, 200, 16); ctx.stroke(); ctx.globalAlpha = 1;
    ctx.fillStyle = p.accent; ctx.font = "22px sans-serif"; ctx.fillText("今日补给 · 麦门套餐", 76, cy + 44);
    if (meal && meal.name) {
      ctx.fillStyle = "#fff"; ctx.font = "700 32px sans-serif";
      ctx.fillText(meal.name.slice(0, 12), 76, cy + 96);
      const price = (meal.price != null) ? "¥" + meal.price : "价格以门店实时为准";
      ctx.fillStyle = p.accent; ctx.font = "26px sans-serif"; ctx.fillText(price, 76, cy + 140);
      ctx.fillStyle = "#8a8a96"; ctx.font = "16px sans-serif";
      ctx.fillText((live ? "来源：麦当劳 MCP 实时" : "来源：演示样例数据"), 76, cy + 180);
    } else {
      ctx.fillStyle = "#d8d8e0"; ctx.font = "26px sans-serif"; ctx.fillText("补给餐品生成中…", 76, cy + 96);
      ctx.fillStyle = "#9a9aa6"; ctx.font = "18px sans-serif";
      ctx.fillText("尚未实时核价 · 配置 MCP Token 后显示真实菜单与价格", 76, cy + 140);
      ctx.fillStyle = "#8a8a96"; ctx.font = "16px sans-serif"; ctx.fillText("来源：麦当劳 MCP（未连接）", 76, cy + 180);
    }

    ctx.fillStyle = "#7a7a86"; ctx.font = "15px sans-serif";
    ctx.fillText((script.repo_url || "").slice(0, 66), 56, H - 50);
    ctx.textAlign = "right"; ctx.fillText("github.com/M-China/mcd-mcp-server", W - 56, H - 50); ctx.textAlign = "left";
  }

  // ---- ui ----------------------------------------------------------------
  let FIXTURES = EMBEDDED, currentMeal = null, currentScript = null;
  const $ = (id) => document.getElementById(id);
  function pickMeal(seed) { return FIXTURES.demo_meals[Math.abs(hash(seed)) % FIXTURES.demo_meals.length]; }
  function enableDownload() { $("dlBtn").disabled = false; }
  function setHint(html) { $("hint").innerHTML = html; }

  function show(kind, value, forcedGenre, seed) {
    const script = buildScript(kind, value, forcedGenre);
    const meal = pickMeal(seed || (kind + ":" + (value || forcedGenre || "")));
    currentScript = script; currentMeal = meal;
    renderPoster(script, meal, false);
    enableDownload();
    const label = kind === "repo" ? "GitHub 仓库" : kind === "text" ? "你的一句话" : "场景";
    setHint("已生成「" + script.genre_cn + "」海报（" + label + "）· <b>演示样例</b>，餐品价格非实时。");
  }

  function bindModes() {
    document.querySelectorAll(".mode-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".mode-tab").forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        const m = tab.dataset.mode;
        ["scene", "text", "repo"].forEach((k) => $("pane-" + k).classList.toggle("hidden", k !== m));
      });
    });
    document.querySelectorAll(".scene-card").forEach((card) => {
      card.addEventListener("click", () => show("scene", "", card.dataset.genre, card.dataset.genre));
    });
    $("textBtn").addEventListener("click", () => {
      const v = $("textInput").value.trim();
      if (!v) { setHint("先写一句话，比如「凌晨三点还在修 bug」。"); return; }
      show("text", v);
    });
    $("textInput").addEventListener("keydown", (e) => { if (e.key === "Enter") $("textBtn").click(); });
    $("genBtn").addEventListener("click", () => {
      const v = $("repoInput").value.trim();
      if (!v) { setHint("粘贴一个公开 GitHub 仓库地址，或切换到「选个场景 / 写一句话」。"); return; }
      show("repo", v);
    });
    $("repoInput").addEventListener("keydown", (e) => { if (e.key === "Enter") $("genBtn").click(); });
    $("dlBtn").addEventListener("click", download);
  }
  function download() {
    document.getElementById("poster").toBlob((blob) => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "mctrailer-poster.png";
      a.click(); URL.revokeObjectURL(a.href);
    }, "image/png");
  }
  function presetChips() {
    const box = $("presetChips");
    box.innerHTML = "";
    FIXTURES.presets.forEach((p) => {
      const b = document.createElement("button");
      b.className = "chip"; b.textContent = p.label;
      b.addEventListener("click", () => { $("repoInput").value = p.repo_url; show("repo", p.repo_url, p.genre, p.genre); });
      box.appendChild(b);
    });
  }

  bindModes();
  fetch("demo-fixtures.json").then((r) => r.ok ? r.json() : Promise.reject()).then((j) => { FIXTURES = j; presetChips(); }).catch(() => presetChips());
  // instant first paint: a ready-made scene poster so visitors see value in <1s
  show("scene", "", "side_project", "side_project");
  presetChips();
})();
