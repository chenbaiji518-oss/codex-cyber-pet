---
name: codex-cyber-pet
description: Use when a user wants to turn one or more pet photos into a custom Codex animated pet, cyber pet, mascot, v2 spritesheet, or needs to install, validate, repair, resize, or troubleshoot a Codex desktop pet that is unchanged, clipped, transparent incorrectly, or still shows the default robot.
---

# Codex 赛博萌宠养成计划

## 核心原则

把照片中的宠物身份特征转成可验证的 Codex v2 动画资产。不要把“看起来像”当作完成；最终交付必须同时通过角色一致性、动作语义、图集结构、透明度、安全边距和实际加载验证。

## 必需能力

- **REQUIRED SUB-SKILL:** 使用 `imagegen` 生成主形象、动作行和环视方向。
- 若已安装 `hatch-pet`，优先使用它的完整生成、注册和盲测流程。
- 使用本 Skill 的脚本完成独立验证、安全边距修复与本地安装。
- 涉及位图生成时不要用 SVG、CSS 或程序绘图替代宠物画面。

## 工作流

1. 收集 1–3 张清晰照片，至少包含正脸与完整身体。确认宠物名称、称呼主人方式、画风和可保留特征。
2. 阅读 [references/workflow.md](references/workflow.md)，建立角色锁定描述与生成清单。
3. 阅读 [references/atlas-contract.md](references/atlas-contract.md)，生成 9 个标准动作行和 16 个顺时针环视方向。
4. 使用确定性工具组装 `1536×2288`、`192×208` 单元格的 8×11 WebP/PNG 图集。不要让图像模型直接生成最终整张图集。
5. 运行：

   ```bash
   python scripts/validate_atlas.py spritesheet.webp --manifest pet.json
   ```

6. 若脚部、尾巴或跳跃动作贴边，运行：

   ```bash
   python scripts/normalize_safe_margins.py spritesheet.webp spritesheet-safe.webp
   python scripts/validate_atlas.py spritesheet-safe.webp --manifest pet.json
   ```

7. 视觉检查完整联系表、9 个动作循环和 16 个方向。四个主方向必须明确：000 上、090 屏幕右、180 下、270 屏幕左。
8. 安装：

   ```bash
   python scripts/install_pet.py --pet-dir ./my-pet --select
   ```

9. 完全退出并重新打开 Codex。仅关闭窗口不会清除宠物缓存。
10. 如果未变化或显示异常，阅读 [references/troubleshooting.md](references/troubleshooting.md) 并沿“选择配置 → 清单 → 图集 → 缓存”顺序排查。

## 不可跳过的验收

- `pet.json` 声明 `spriteVersionNumber: 2`，`spritesheetPath` 指向同目录文件。
- 图集必须是 `1536×2288`、RGBA、8 列 × 11 行。
- 前 9 行状态与帧数严格符合契约；未使用单元格全透明。
- 第 9–10 行包含固定顺序的 16 个环视方向。
- 所有有效帧身份一致，无文字、阴影、场景、漂浮特效或邻格重叠。
- 全透明像素的隐藏 RGB 必须为零，不得残留色键边缘。
- 默认显示帧建议保留至少 18 px 顶边和 24 px 底边。
- 安装后实际显示完整，并触发至少待机、移动、等待和环视动作。

## 安全规则

- 首次安装不要静默覆盖同名宠物；安装脚本必须先备份。
- 不要直接修改 Codex 应用包。
- 不要通过删除缓存目录解决加载问题；先完全退出应用并核对配置时间。
- 不要把某个成功的单帧拼进另一组生成的环视行；方向行必须作为连续动作族整体生成。
- 验证失败时停止安装，修复最小失败动作行后重新组装。

## 交付内容

向用户报告宠物名称、安装路径、图集版本/尺寸、验证结果、联系表路径，以及是否需要 `Command+Q` 后重启。用户要发布或分享时，同时提供仓库安装命令与许可证说明。

