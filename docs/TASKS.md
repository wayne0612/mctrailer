# TASKS.md — McTrailer 2026-10-23 P0 拆解

> 目标：2026-10-25 23:59（北京时间）前完成开源、报名。以下为 10-23 当日 P0，每项 ≤2h。

| # | 任务 | 输入 → 输出 | 验收 | 负责 | 状态 |
|---|------|------------|------|------|------|
| 1 | 读取官方规则 + 拉取官方声明 | 大赛仓库 → CONTEST_DECLARATION.md | sha256 字节一致 | 工程 | ✅ |
| 2 | 麦当劳 MCP 接入 + 列 tools/list + 核对 schema | Token → 可用工具清单 | 握手 200、schema 已核实（query-meals/meal-detail/price/nearby） | 工程 | ✅ |
| 3 | 项目骨架 + 配置示例 + .gitignore + LICENSE | 计划 → 目录树 | 5 个必交文件齐备 | 工程 | ✅ |
| 4 | repo_profile（公开元数据 + 确定性类型映射） | repo URL → profile{genre} | 10 固定样例输出一致；离线可跑 | 工程 | ✅ |
| 5 | script_engine（4 剧情模板，确定性） | profile → script | 同输入同输出 | 工程 | ✅ |
| 6 | normalize_mcp（菜单/详情/价格归一化，分转元） | MCP 响应 → 结构化 | 不臆造字段；无数据显示降级 | 工程 | ✅ |
| 7 | poster（SVG 海报，真实/演示两种标注） | script+meal → SVG | 演示不含虚构价格；实时显示价格+时间戳 | 工程 | ✅ |
| 8 | generate.py 垂直闭环 | repo URL(+city) → JSON+海报 | 真·端到端 LIVE 跑通（深圳南山：¥15.90） | 工程 | ✅ |
| 9 | smoke_test + 单元测试 | — | 11/11 通过；CI 可跑 | 工程 | ✅ |
| 10 | Web 演示（canvas 海报 + PNG 导出 + fixtures） | — | 无 Token 可体验；明确标注演示样例 | 工程 | ✅ |
| 11 | SKILL.md + references | — | WorkBuddy 可调用；含 schema/安全红线 | 工程 | ✅ |
| 12 | CI（编译/测试/密钥扫描/声明字节校验） | — | workflow 就绪 | 工程 | ✅ |

## 待办（10-24 / 10-25，由产品负责人审核执行）
- [ ] 建个人公共仓库、推送、开启 GitHub Pages（`<USERNAME>.github.io/mctrailer/`）
- [ ] 补 20 秒演示视频 + 首屏 GIF（`media/`）
- [ ] 10 位目标用户冒烟（≥8/10 无指导完成）
- [ ] **最迟 10-24 提交报名 Issue**，确认机器人回复成功
- [ ] 10-25 传播 + 每 4-6h 看榜 + 冻结代码复查（无 Token、声明字节一致、链接正确）

## 明确不做
支付闭环、账户同步、代下单、刷 Star。
