# Skill Manager - 自动扫描全局和项目级技能

## ✅ 功能已实现

系统现在可以自动扫描 **全局** + **项目级** 所有可用 skill。

### 扫描范围

1. **全局技能** (Global)
   - 位置: `~/.claude/skills/`
   - 数量: 37 个
   - 示例: socrates, nuwa-skill, github-code-review

2. **项目级技能** (Project)
   - 位置: `<project>/.claude/skills/`
   - 数量: 0 个（当前无）
   - 用途: 项目专属技能配置

---

## 🚀 使用方法

### 方式 1: 使用 CLI（推荐）

```bash
cd ~/.claude/skill-manager
python skill_manager.py scan              # 扫描所有技能
python skill_manager.py list              # 列出所有技能
python skill_manager.py search nuwa       # 搜索技能
python skill_manager.py recommend "女娲"  # 推荐技能
```

### 方式 2: 手动添加项目技能

在项目的 `.claude/skills/` 目录放置 SKILL.md 文件：

```bash
# 在项目中创建
mkdir -p .claude/skills
echo '---
name: "My Project Skill"
description: "Custom project skill."
---' > .claude/skills/my-skill.md
```

然后运行：
```bash
python skill_manager.py scan
```

---

## 📊 查看统计信息

```bash
python skill_manager.py stats
```

输出示例：
```
Registry Statistics
  Total Skills: 37
  Global: 37
  Project: 0
  Enabled: 37
  Disabled: 0
  Categories: Agent编排(14), GitHub集成(5), ...
```

---

## 🔍 过滤和搜索

### 按类别过滤
```bash
python skill_manager.py list --category "思维方法"
```

### 按状态过滤
```bash
python skill_manager.py list --status enabled
```

### 按作用域过滤
```bash
python skill_manager.py list --scope global    # 仅全局
python skill_manager.py list --scope project  # 仅项目
```

### 搜索技能
```bash
python skill_manager.py search "nuwa"
python skill_manager.py search "审查"
```

---

## 💡 项目级技能示例

### 示例 1: 自定义业务规则

在项目根目录创建 `.claude/skills/business-rules/SKILL.md`:

```yaml
---
name: "Business Rules"
description: |
  Custom business rules for this project.
  Use when implementing business logic or workflows.
---
```

### 示例 2: 项目特定工具

在 `.claude/skills/project-tools/SKILL.md`:

```yaml
---
name: "Project Tools"
description: "Utilities specific to this project."
---
```

---

## 🔄 更新注册表

当添加新技能或修改现有技能后，需要重新扫描：

```bash
python skill_manager.py scan
```

这会：
- 重新读取所有 SKILL.md 文件
- 更新元数据（名称、描述、触发词等）
- 保存到 `data/registry.json`

---

## 📁 文件结构

```
~/.claude/skills/                    # 全局技能目录
├── socrates/
│   └── SKILL.md
├── nuwa-skill/
│   └── SKILL.md
└── ...

<project>/.claude/skills/            # 项目技能目录
├── my-custom-skill/
│   └── SKILL.md
└── ...

~/.claude/skill-manager/             # 管理系统
├── data/
│   └── registry.json               # 注册表数据库
├── hooks/
│   ├── on_session_start.py         # Session Hook
│   └ on_prompt_submit.py           # Prompt Hook
└── skill_manager.py                 # 主程序
```

---

## ✨ 优势

### 1. 统一管理
- 一个命令扫描所有技能
- 无需手动维护列表

### 2. 灵活配置
- 全局技能共享给所有项目
- 项目技能仅用于特定项目

### 3. 易于扩展
- 添加新技能只需放入目录
- 自动识别和注册

---

## ❓ 常见问题

### Q: 如何查看哪些技能被扫描？
A: 运行 `python skill_manager.py stats`

### Q: 项目技能和全局技能有什么区别？
A: 
- **全局**: 适用于所有项目
- **项目**: 仅适用于当前项目

### Q: 如何禁用某个技能？
A: 编辑 `data/registry.json`，将 `"status"` 改为 `"disabled"`

### Q: 可以同时使用两个吗？
A: 是的，系统会自动合并扫描所有技能

---

**版本**: v0.1.0  
**更新日期**: 2026-07-01  
**状态**: 自动扫描功能已完成 ✅