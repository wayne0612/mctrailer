# 麦当劳 MCP（mcd-mcp）工具参考

> 以下 schema 与字段均于 2026-10-23 对线上 `https://mcp.mcd.cn` 实测核对，非臆造。
> 接入地址：`https://mcp.mcd.cn`；协议 Streamable HTTP；鉴权 `Authorization: Bearer <MCD_MCP_TOKEN>`。
> 完整官方列表见 https://github.com/M-China/mcd-mcp-server

## McTrailer 实际调用链（到店自取场景）
1. `query-nearby-stores` → 拿到 `storeCode`
2. `query-meals` → 拿到餐品 `code`（`data.categories[].meals[]`，仅 code+tags，无名称/价格）
3. `query-meal-detail` → 拿到餐品 `name` 与组成
4. `calculate-price` → 拿到官方试算价（`price` 单位为**分**，需 /100 转元）

## 关键入参规则（易错）
- `beType`：`1` 到店取餐，`2` 麦乐送，`5` 得来速(DT)，`6` 企业团餐。
- `orderType`：`1` 到店（含到店自取+得来速），`2` 外送。**query-meals / query-meal-detail / calculate-price 必传。**
- `beCode`：`beType=5/2/6` 时必传（取自门店/地址返回）；**`beType=1` 到店自取时不要传，传了报错**。
- `query-nearby-stores`：`searchType=2` 按位置搜索（需 city/keyword），`searchType=1` 搜收藏餐厅。
- `calculate-price.items[]`：商品字段是 `productCode`（不是 `code`），且 `quantity` 必填 ≥1。

## 返回结构（已核实）
| 工具 | data 结构 |
|------|-----------|
| query-nearby-stores | `[{storeCode, beCode, storeName, address, distance, reservation}]` |
| query-meals | `{categories:[{name, meals:[{code, tags[]}]}]}` |
| query-meal-detail | `{code, name, image, rounds:[{name, choices:[{name, diffPrice}]}]}` |
| calculate-price | `{price(分), originalPrice(分), discount(分), productList:[{productCode, productName, subtotal}], takeWayList}` |

## 可选增强
- `campaign-calendar`：当月营销活动日历，可把真实活动主题编进海报台词。
- `list-nutrition-foods`：餐品营养（仅作展示，不给健康建议）。

## 限流与错误码
- 每 Token **600 次/分钟**，超限返回 `429`。
- `401`：Token 无效/过期/未提供——检查 `Authorization` 头。
- 查询失败/无门店/无售价时：降级为演示海报，**不得伪造价格**。
