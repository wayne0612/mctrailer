# 传播文案（McTrailer 麦门导演局）

> 先展示作品价值，再邀 Star；**不刷 Star、不互刷、不群发骚扰、不暗示官方背书**。各社区遵守分区规则。

## 一句话卖点
把你的 GitHub 项目，拍成一部麦当劳「程序员补给电影」——只要粘贴仓库地址。

---

## 版本 A · 掘金 / CSDN（技术向，带实现与踩坑）

**标题备选：**
- 我把 GitHub 仓库拍成了麦当劳「电影海报」（接官方 MCP 拉真实菜单/价格）
- 1024 程序员节参赛：用麦当劳 MCP 把任意仓库变成电影海报

**正文：**

> 你的 GitHub 项目，除了 commit 记录，还能是什么？一部电影。
>
> **McTrailer · 麦门导演局**：粘贴一个公开仓库地址，它先按确定性规则把你的项目判成「悬疑/动作/科幻/公路」四种剧情之一，再通过**麦当劳官方 MCP** 拉取附近门店、实时菜单和官方试算价，推荐当日补给餐品，最后生成一张可分享的电影海报（PNG）。
>
> 🚀 在线体验（无需 Token）：https://wayne0612.github.io/mctrailer/
> ⭐ 开源仓库：https://github.com/wayne0612/mctrailer
>
> **几个真实踩坑（接麦当劳 MCP 才知道的）：**
> 1. `query-meals` 返回的菜单项**只有 code，没有名称和价格**——餐品名要再调 `query-meal-detail`。
> 2. 价格字段 `price/originalPrice/discount` 单位是**分**，要 /100。
> 3. `query-meals`/`query-meal-detail`/`calculate-price` 都必传 `orderType`；`beType=1`（到店自取）**不能传 `beCode`**，传了直接报错。
> 4. `calculate-price` 的商品字段是 `productCode`，不是 `code`。
>
> 无 Token 时优雅降级为「演示样例」，绝不编造价格。纯 Python 标准库 + 原生 Canvas，无重依赖。
>
> 麦当劳程序员节创意开发大赛参赛作品，非官方产品。觉得有趣欢迎 Star，想交流 MCP 实战欢迎评论。

---

## 版本 B · V2EX / 技术社群（短平快）

> 做了个小玩具：粘贴任意公开 GitHub 仓库，给你拍成一张麦当劳「程序员补给电影」海报，餐品和价格是接麦当劳官方 MCP 的真实数据。
> 在线玩：https://wayne0612.github.io/mctrailer/
> 源码：https://github.com/wayne0612/mctrailer
> （1024 麦当劳 MCP 创意大赛参赛，非官方产品。喜欢就给个 Star ⭐）

---

## 版本 C · 小红书 / 视频号（视觉向，配视频/海报）

> 把 GitHub 项目拍成电影海报是什么体验？🍔
> 粘贴仓库地址 → 判定剧情 → 麦当劳真实菜单推荐补给 → 出图
> 我的项目今天是「公路片」主角，配了一份 ¥15.9 的鸡薯双全盒😂
> 在线玩 👉 https://wayne0612.github.io/mctrailer/
> #程序员 #1024程序员节 #麦当劳 #AI #开源

---

## 发布节奏建议
- 10-24：掘金/CSDN 技术帖 + V2EX（分享实现与踩坑，最容易拿真实 Star）。
- 10-25：小红书/B 站发 20 秒视频（视觉传播），引导到仓库。
- 每次发布只带**一次**链接，避免被判 spam；积极回复评论。
