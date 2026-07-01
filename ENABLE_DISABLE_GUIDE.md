# Skill Manager - 快速启用/禁用指南

## 🚀 快速启用自动激活

### Windows
```bash
# 双击运行
%USERPROFILE%\.claude\skill-manager\enable-skill-auto.bat

# 或命令行
cd ~/.claude/skill-manager
enable-skill-auto.bat
```

### 手动配置
编辑 `~/.claude/skill-manager/data/config.json`:
```json
{
  "auto_activation_enabled": true,
  "default_choice": "always"
}
```

## 🔇 快速禁用自动激活

### Windows
```bash
# 双击运行
%USERPROFILE%\.claude\skill-manager\disable-skill-auto.bat

# 或命令行
cd ~/.claude/skill-manager
disable-skill-auto.bat
```

### 手动配置
编辑 `config.json`:
```json
{
  "auto_activation_enabled": false,
  "default_choice": "never"
}
```

## 📊 当前状态

查看当前配置：
```bash
cat ~/.claude/skill-manager/data/config.json
```

## 🔄 三种模式

| default_choice | auto_activation_enabled | 行为 |
|----------------|------------------------|------|
| **"always"** | true | 每次启动自动激活，显示推荐 |
| **"never"** | false | 每次启动静默运行，不激活 |
| **"ask"** | false | 启动时显示提示信息，不激活 |

## 💡 启用后的效果

### 会话启动
```
[Skill Manager] Auto-activation ENABLED (always)
  37 skills ready for activation
  Disable: Edit config.json or use CLI
```

### 输入提示词
```
用户: 女娲，蒸馏马斯克

[Skill Manager] Detected skills:
  - nuwa-skill (0.85, keyword, name)
  - github-code-review (0.72, semantic)

  Tip: Use skills by mentioning their triggers.
```

## 📂 文件位置

- 配置: `C:\Users\LENOVO\.claude\skill-manager\data\config.json`
- 启用脚本: `enable-skill-auto.bat`
- 禁用脚本: `disable-skill-auto.bat`

---
版本: v0.1.0
更新: 2026-07-01