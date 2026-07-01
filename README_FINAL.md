# Skill Manager System v0.1.0

## ✅ 已安装完成

### 核心功能
- **37 个技能** 自动扫描注册
- **8 个 CLI 命令** 完整可用
- **4 级激活策略** 智能匹配
- **Session Hook** 会话启动集成

### 自动激活功能
- ✅ Hook 已集成到 settings.json
- ✅ 配置文件已创建
- ✅ 启用/禁用脚本已创建

---

## 🚀 快速开始

### 方式 1: 启用自动激活（推荐）

**Windows**:
```bash
# 双击运行
C:\Users\LENOVO\.claude\skill-manager\enable-skill-auto.bat
```

重启 Claude Code 后生效。

### 方式 2: 手动管理

```bash
cd ~/.claude/skill-manager
python skill_manager.py scan              # 扫描技能
python skill_manager.py list              # 列出所有技能
python skill_manager.py search nuwa       # 搜索技能
python skill_manager.py recommend "女娲"  # 推荐技能
python skill_manager.py metrics           # 查看指标
```

---

## 📊 三种运行模式

| 模式 | 配置 | 行为 |
|------|------|------|
| **始终启用** | `"default_choice": "always"` | 每次启动自动激活 |
| **始终禁用** | `"default_choice": "never"` | 静默运行，不激活 |
| **询问模式** | `"default_choice": "ask"` | 显示提示，不激活 |

**当前模式**: ask（默认）

---

## 🔧 配置文件

位置: `C:\Users\LENOVO\.claude\skill-manager\data\config.json`

```json
{
  "auto_activation_enabled": false,
  "default_choice": "ask",
  "session_count": 1
}
```

### 修改配置

**启用**:
```json
{
  "auto_activation_enabled": true,
  "default_choice": "always"
}
```

**禁用**:
```json
{
  "auto_activation_enabled": false,
  "default_choice": "never"
}
```

---

## 📁 文件清单

### 核心程序
- `skill_manager.py` - 主程序 (16.8 KB)
- `skill.bat` - Windows 快捷脚本
- `skill.sh` - Unix/Linux/Mac 脚本

### 启用/禁用脚本
- `enable-skill-auto.bat` - 启用自动激活
- `disable-skill-auto.bat` - 禁用自动激活

### Hooks
- `hooks/on_session_start.py` - 会话启动 Hook
- `hooks/on_prompt_submit.py` - 提示词分析 Hook (未启用)

### 数据文件
- `data/config.json` - 配置文件
- `data/registry.json` - 技能注册表 (37 个)
- `data/activation_history.json` - 激活历史

### 文档
- `README_FINAL.md` - 本文件
- `ENABLE_DISABLE_GUIDE.md` - 启用/禁用指南
- `QUICKREF.md` - CLI 快速参考
- `AUTO_ACTIVATION_GUIDE.md` - 自动激活详细指南

---

## 💡 使用示例

### 示例 1: 蒸馏人物思维
```bash
$ python skill_manager.py recommend "女娲，蒸馏马斯克"

Skill Recommendations

  huashu-nuwa          (confidence: 0.85, levels: keyword, name)
```

### 示例 2: 代码审查
```bash
$ python skill_manager.py recommend "review 这个PR"

Skill Recommendations

  github-code-review   (confidence: 0.72, levels: semantic)
  verification-quality (confidence: 0.68, levels: semantic)
```

### 示例 3: 查看技能详情
```bash
$ python skill_manager.py info nuwa-skill --metrics

Skill: huashu-nuwa

ID: nuwa-skill
Category: 思维方法
Status: enabled

Metrics:
  Invocations: 0
  Success Rate: 0.0%
```

---

## 🔄 工作流程

### 当前流程（ask 模式）
```
Claude 启动
  ↓
Session Hook 运行
  ↓
显示提示信息
  ↓
用户手动使用 CLI 或编辑配置
```

### 启用后流程（always 模式）
```
Claude 启动
  ↓
Session Hook 运行
  ↓
显示 "Auto-activation ENABLED"
  ↓
用户输入提示词
  ↓
Prompt Hook 分析并推荐技能
```

---

## 📝 注意事项

### UserPromptSubmit Hook 未启用
当前仅 Session Hook 已集成。

如需自动提示词分析，需在 `settings.json` 添加：
```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python C:\Users\LENOVO\.claude\skill-manager\hooks\on_prompt_submit.py",
        "timeout": 3000
      }
    ]
  }
]
```

### Windows 编码
部分 Windows 环境可能显示乱码，功能正常。

---

## 🐛 故障排查

### Hook 未运行
检查：
1. `settings.json` 是否包含 hook 配置
2. Python 路径是否正确
3. 文件是否存在

### 技能未检测
运行：
```bash
python skill_manager.py scan
```

### 配置不生效
检查：
```bash
cat ~/.claude/skill-manager/data/config.json
```

---

## 📚 相关文档

- `ENABLE_DISABLE_GUIDE.md` - 启用/禁用详细指南
- `QUICKREF.md` - CLI 命令快速参考
- `AUTO_ACTIVATION_GUIDE.md` - 自动激活完整指南
- `PHASE1_REPORT.md` - Phase 1 技术报告

---

## 🎯 下一步

1. **启用自动激活**:
   - 双击 `enable-skill-auto.bat`
   - 或编辑 `config.json` 设置 `"default_choice": "always"`

2. **重启 Claude Code** 使配置生效

3. **测试功能**:
   - 输入提示词观察推荐
   - 使用 CLI 手动管理

---

**版本**: v0.1.0
**状态**: Phase 1 完成 + Hooks 集成
**更新**: 2026-07-01
**开发者**: Claude Code
