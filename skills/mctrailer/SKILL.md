---
name: mctrailer
description: >-
  把一个公开的 GitHub 仓库变成一部「麦门程序员补给电影」海报。输入仓库地址（可选城市/区域），
  先用确定性规则判定电影类型（悬疑/动作/科幻/公路），再通过麦当劳官方 MCP 拉取附近门店、
  实时菜单与试算价格，推荐当日补给餐品，生成可分享的 SVG/PNG 海报。
  Triggers: 麦门导演局, McTrailer, GitHub 仓库变电影海报, 程序员电影海报, 麦门补给,
  把我的项目拍成电影, repo to movie poster, McDonald's movie poster。
---

# McTrailer · 麦门导演局

把任意**公开** GitHub 仓库变成一部 15 秒的「麦门程序员补给电影」，并用**麦当劳官方 MCP 的真实
菜单与价格**推荐当日补给餐品，生成一张可分享的电影海报。

## 这个 Skill 做什么
1. 读取仓库的**公开**元数据（描述、语言、topics、最近提交信息）——只读、不克隆、不执行。
2. 用**确定性**规则把仓库映射到一种电影类型（纯娱乐分类，不评价程序员水平）。
3. 通过麦当劳 MCP 查询附近门店 → 实时菜单 → 餐品详情 → 官方试算价。
4. 生成电影海报（SVG；浏览器内可导出 PNG），标注数据来源与查询时间。

## 何时使用
- 用户给出一个 GitHub 仓库地址，想要"电影海报 / 麦门主角 / 补给推荐"。
- 用户想体验麦当劳 MCP 的点餐/菜单/价格能力。

## 运行方式（唯一入口）
所有逻辑都在 `scripts/`，主入口是 `generate.py`。**不要**凭记忆拼 MCP 字段或价格——一律走脚本，
让脚本用真实 schema 调用。

```bash
# 演示模式（无 Token，明确标注为演示样例）
python3 scripts/generate.py --repo https://github.com/psf/requests --demo

# 实时模式（需要 MCD_MCP_TOKEN；--city 提供城市以查附近门店）
MCD_MCP_TOKEN=xxx python3 scripts/generate.py \
    --repo https://github.com/psf/requests --city 深圳市 --keyword 南山区
```

环境变量：
- `MCD_MCP_TOKEN`：麦当劳 MCP Token（见 `mcp-config.example.json`）。缺失则自动降级为演示海报。
- `GITHUB_TOKEN`（可选）：提高 GitHub API 限额（未认证仅 60 次/小时）。

返回一段 JSON 摘要（类型/片名/主角/餐品/是否实时/海报路径）+ 生成的海报文件。

## 边界（不可越过）
- 只读**公开** GitHub 元数据；绝不接触私有仓库、邮箱、电话、地址或账户历史订单。
- 餐品、价格、券规则**只能来自 MCP 响应**；查不到时显示"尚未实时核价"，**严禁编造价格**。
- 电影类型纯娱乐，不给健康/营养建议。
- 默认**不创建订单**、不支付、不同步账户；若未来支持，必须让用户明确二次确认。
- MCP Token 只从环境变量读取，**绝不打印、入库或写进公开仓库**。
- 演示数据必须在界面/海报上明确标注"演示样例 · 非实时核价"。

## 输入参数
- `--repo`（必填）：公开 GitHub 仓库 URL。
- `--city` / `--keyword`（实时查门店用）：城市 / 区域关键词。
- `--be-type`：`1` 到店自提（默认），`5` 得来速车道取餐。
- `--demo`：强制演示模式，不调用 MCP。

## 详细参考
- `references/mcp-tools.md`：已核实的麦当劳 MCP 工具、schema、参数与限流/错误码。
- `references/safety.md`：安全与合规红线。
- `../..` 目录：参赛文件（README / MCP_INTEGRATION / mcp-config.example.json / CONTEST_DECLARATION.md）。
