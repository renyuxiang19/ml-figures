---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

画一个 Vision Transformer (ViT) 的架构图：图像切成 patch，线性投影成 patch embedding，加上 class token 和位置编码，送入 L 层 Transformer encoder（每层是 LayerNorm → Multi-Head Attention → 残差，再 LayerNorm → MLP → 残差），最后用 class token 经过 MLP head 输出类别。
