# MCP_INTEGRATION.md — 麦当劳 MCP 集成说明

本文件说明 McTrailer 实际使用的麦当劳 MCP Server、Tool、调用流程与业务价值。所有 schema 与字段均于 **2026-10-23** 对线上服务实测核对。

## 1. 使用的 MCP Server

- 名称：`mcd-mcp`（麦当劳中国 MCP Server）
- 接入地址：`https://mcp.mcd.cn`
- 协议：Streamable HTTP；鉴权：请求头 `Authorization: Bearer <MCD_MCP_TOKEN>`
- 官方仓库：https://github.com/M-China/mcd-mcp-server
- 客户端：`skills/mctrailer/scripts/mcd_client.py`（Python 标准库实现，Token 仅从环境变量读取，不落盘、不打印）

## 2. 实际调用的 Tool 与调用流程

到店自提场景（`beType=1, orderType=1`）的完整链路：

```
query-nearby-stores  ──► storeCode
        │
query-meals          ──► data.categories[].meals[].code   （菜单项仅含 code+tags，无名称/价格）
        │
query-meal-detail    ──► data.name / rounds[].choices[].name （餐品名称与组成）
        │
calculate-price      ──► data.price（单位：分，/100 转元）→ 官方试算价
```

可选：`campaign-calendar`（把当月真实活动主题编进海报台词）。

**关键参数规则（已核实，易错点）：**
- `query-meals` / `query-meal-detail` / `calculate-price` 必传 `storeCode`、`orderType`、`beType`。
- `beType=1`（到店自取）**不要传 `beCode`**（传了报错）；`beType=5/2/6` 才必传 `beCode`。
- `calculate-price.items[]` 商品字段是 `productCode`（非 `code`），`quantity ≥ 1`。
- 价格字段 `price/originalPrice/discount` 单位为**分**。

## 3. 脱敏的实时验证证据（2026-10-23）

一次真实 `generate.py --city 深圳市 --keyword 南山区` 运行结果（已脱敏，无 Token）：

- 门店：`麦当劳深圳南山餐厅`（`storeCode=1420009`，来自 `query-nearby-stores`）
- 餐品：`"我就喜欢"鸡薯双全盒`（`code=9900016076`，来自 `query-meal-detail`）
- 试算价：`¥15.90`（`calculate-price.price=1590` 分）
- 海报：`media/psf-requests-poster.svg`（标注"实时 MCP · 官方菜单"与查询时间）

MCP 握手返回：`serverInfo = {name: "mcd-mcp", version: "1.0.0"}`，`protocolVersion = 2024-11-05`。

## 4. 降级与真实性

- 无 `MCD_MCP_TOKEN` / 无城市 / 请求失败 / 无门店 / 无售价时：海报降级为"演示样例 · 非实时核价"或"尚未实时核价"，**不编造任何价格或餐品**。
- 演示网页（`web/`）浏览器无法持有 Token，恒为演示模式，界面明确标注。

## 5. 业务价值

把"我在哪 → 吃点啥 → 怎么省 → 多少钱"在一句话内走完：用真实门店与实时菜单推荐当日补给，直接给出官方试算价，降低点餐决策与操作摩擦；同时以电影海报形式承载程序员节日情绪，具备社区传播性。

## 6. 限流与错误码

- 每 Token 600 次/分钟，超限 `429`。
- `401`：Token 无效/过期/未提供。

## 7. 官方声明字节校验

`CONTEST_DECLARATION.md` 为官方原文逐字复制，未做任何编辑：

```
sha256: cd28101bcb29cc8fb24b372fe91ce6b42c4a1487a54e01f7ade0c8c6a84241b7
bytes:  1522
```
