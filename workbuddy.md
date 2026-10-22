# workbuddy.md — 使用 WorkBuddy 开发的真实记录

本文件记录 McTrailer 在 **WorkBuddy** 中的真实开发上下文，用于大赛 WorkBuddy 联动奖励核验。以下均为本次会话中真实发生的操作与结果（时间均为北京时间）。

## 1. 环境与连接器（真实）
- 在 WorkBuddy 中把麦当劳官方 MCP（`mcd-mcp`，`https://mcp.mcd.cn`，Streamable HTTP）配置为自定义连接器，Token 写入本地 `~/.workbuddy/mcp.json`（未进入本仓库）。
- 已点「信任 / 启用」连接器；并用标准 MCP `initialize` 握手验证：返回 `serverInfo = mcd-mcp v1.0.0`、`protocolVersion 2024-11-05`、HTTP 200。

## 2. 开发过程中真实验证过的能力（脱敏）
- `tools/list`：核对 `query-nearby-stores` / `query-meals` / `query-meal-detail` / `calculate-price` / `campaign-calendar` / `list-nutrition-foods` 的真实 schema 与必填入参（`orderType` 必传、`beType=1` 不传 `beCode`、`calculate-price` 用 `productCode`、价格单位为分）。
- `generate.py` 真·端到端 LIVE 运行（`--city 深圳市 --keyword 南山区`）：
  - 门店：麦当劳深圳南山餐厅（storeCode 1420009）
  - 餐品："我就喜欢"鸡薯双全盒（code 9900016076）
  - 试算价：¥15.90（calculate-price.price=1590 分）
  - 产物：`media/psf-requests-poster.svg`，标注"实时 MCP · 官方菜单"
- 冒烟测试 11/11 通过（类型映射确定性、海报演示不含虚构价格、实时海报正确显示价格）。

## 3. 在 WorkBuddy 中完成的工程产出
- Skill：`skills/mctrailer/`（SKILL.md + scripts + references）
- 核心脚本：`mcd_client.py`、`repo_profile.py`、`script_engine.py`、`normalize_mcp.py`、`poster.py`、`generate.py`、`smoke_test.py`
- Web 演示：`web/`（canvas 海报、PNG 导出、demo-fixtures.json）
- 参赛文件与质量门禁：README、MCP_INTEGRATION、mcp-config.example.json、CONTEST_DECLARATION.md（官方原文）、LICENSE、.gitignore、CI（含密钥扫描与声明字节校验）、tests、docs/TASKS.md

## 4. 安全与合规（真实遵守）
- Token 只从环境变量读取，未打印、未提交、未写入本仓库；CI 含密钥扫描。
- 只读公开 GitHub 元数据；不接触私有数据；不创建订单、不支付。
- 无 Token / 查询失败一律降级为"演示样例 · 非实时核价"，不编造价格。

> 说明：本文件为开发过程真实摘要，非官方产品；餐品与价格以麦当劳官方渠道实时结果为准。
