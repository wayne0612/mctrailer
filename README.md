# McTrailer · 麦门导演局

> **把你的项目拍成一部 15 秒的麦门程序员补给电影——不用 GitHub 也能玩。**
> Turn any public GitHub repo into a McDonald's "programmer supply" movie poster — powered by the official McDonald's MCP.
>
> 🍔 粘贴一个公开仓库地址 → 判定电影类型 → 用麦当劳 MCP 的真实菜单/价格推荐补给 → 生成可分享海报。

### 🚀 [立即体验在线演示](https://wayne0612.github.io/mctrailer/) ｜ ⭐ 欢迎 Star

无需 Token，**选个场景 / 写一句话 / 粘贴公开 GitHub 仓库**，3 秒生成一张麦门电影海报；本地配置 `MCD_MCP_TOKEN` 可拉取**真实门店 / 菜单 / 官方试算价**。

**3 秒看懂**：`选场景 / 写一句话 / 粘仓库` → `判定剧情(悬疑/动作/科幻/公路)` → `麦当劳 MCP 真实菜单+价格` → `导出 PNG 海报`。

参赛项目：**麦当劳程序员节创意开发大赛（1024 Programmers' Day）**。本项目由参赛者独立开发，**非麦当劳官方产品**。

---

## ✨ 它能做什么

- **确定性电影类型判定**：读取仓库公开元数据（描述 / 语言 / topics / 最近提交），映射到悬疑 / 动作 / 科幻 / 公路四种剧情（纯娱乐，不评价程序员水平）。
- **麦当劳 MCP 实时链路**：附近门店 → 实时菜单 → 餐品详情 → 官方试算价（到店自提 / 得来速）。
- **可分享海报**：电影片名、台词、主角、补给餐品、数据来源与时间戳；浏览器内一键导出 PNG。
- **安全降级**：无 Token 或查询失败时，明确标注"演示样例 · 非实时核价"，**绝不编造价格**。

## 🚀 快速开始

### 网页演示（无需 Token，体验排版）
```bash
# 任选其一：直接用浏览器打开 web/index.html，或部署到 GitHub Pages
cd web && python3 -m http.server 8080
# 打开 http://localhost:8080
```

### 本地实时模式（真实门店 / 菜单 / 试算价）
```bash
# 1) 配置 MCP Token（从 https://open.mcd.cn/mcp 申请），见 mcp-config.example.json
export MCD_MCP_TOKEN="你的Token"
export GITHUB_TOKEN="可选，提高 GitHub API 限额"

# 2) 生成海报（三种入口任选其一）
python3 skills/mctrailer/scripts/generate.py --scene release_day --city 深圳市 --keyword 南山区
python3 skills/mctrailer/scripts/generate.py --text "凌晨三点还在修 bug" --city 深圳市 --keyword 南山区
python3 skills/mctrailer/scripts/generate.py --repo https://github.com/psf/requests --city 深圳市 --keyword 南山区
```
输出一段 JSON 摘要 + 一张海报（`media/*-poster.svg`）。无 Token 时自动降级为演示海报。

### 作为 WorkBuddy Skill 使用
见 [`skills/mctrailer/SKILL.md`](skills/mctrailer/SKILL.md)。在 WorkBuddy 中启用 `mcd-mcp` 连接器后，直接说
"用 McTrailer 把 https://github.com/psf/requests 拍成电影海报"即可。

## 🧩 项目结构

```text
mctrailer/
├── README.md  MCP_INTEGRATION.md  CONTEST_DECLARATION.md  mcp-config.example.json  workbuddy.md  LICENSE
├── skills/mctrailer/            # WorkBuddy Skill
│   ├── SKILL.md
│   ├── scripts/                 # repo_profile / script_engine / normalize_mcp / mcd_client / poster / generate / smoke_test
│   └── references/              # mcp-tools.md（已核实 schema）/ safety.md
├── web/                         # GitHub Pages 演示（canvas 海报 + PNG 导出）
├── tests/  media/  docs/  .github/workflows/ci.yml
```

## 🔌 麦当劳 MCP 集成

- 接入地址 `https://mcp.mcd.cn`（Streamable HTTP，`Authorization: Bearer <token>`）。
- 实际调用：`query-nearby-stores` → `query-meals` → `query-meal-detail` → `calculate-price`（+ 可选 `campaign-calendar`）。
- 字段、参数与限流均**线上实测核对**，详见 [`MCP_INTEGRATION.md`](MCP_INTEGRATION.md) 与 [`skills/mctrailer/references/mcp-tools.md`](skills/mctrailer/references/mcp-tools.md)。

## 🎬 演示与传播

- 在线演示：https://wayne0612.github.io/mctrailer/
- 海报样例：`media/psf-requests-poster.svg`
- 20 秒演示视频 / 首屏 GIF：见 `media/`（赛事传播日补充）

## 📁 参赛必备文件

`README.md`、`CONTEST_DECLARATION.md`（官方原文，逐字未改，sha256 见 MCP_INTEGRATION.md）、`MCP_INTEGRATION.md`、源代码；申请 WorkBuddy 联动积分另附 `workbuddy.md`。

## ⚖️ 免责与边界

作品为非官方参赛项目；餐品、价格与供应状态以麦当劳官方渠道实时结果为准。只读公开 GitHub 元数据，不接触私有数据；不创建订单、不支付。详见 [`skills/mctrailer/references/safety.md`](skills/mctrailer/references/safety.md)。

## 📄 License

MIT，见 [LICENSE](LICENSE)。麦当劳 MCP 的使用须遵守麦当劳中国《使用条款》及《麦当劳 MCP 服务规则》。
