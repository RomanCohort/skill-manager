# Skill Manager System

> 智能技能管理系统 for Claude Code

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/yourusername/skill-manager)
[![Status](https://img.shields.io/badge/status-Phase%201%20Complete-green.svg)](https://github.com/yourusername/skill-manager)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)

## 简介

Skill Manager System 是一个智能技能管理系统，用于 Claude Code 的 37+ 已安装技能。支持自动激活、智能推荐、CLI 管理、性能监控。

## 功能特性

- ✅ **技能注册表**: 自动扫描 37+ 技能，提取元数据
- ✅ **CLI 工具**: 8 个命令（scan, list, search, info, enable, disable, recommend, metrics）
- ✅ **激活引擎**: 4 级匹配策略（关键词、名称、描述、上下文）
- ✅ **自动激活**: Session Hook 集成，可配置启用/禁用
- ✅ **性能监控**: 调用统计、成功率、执行时间追踪

## 快速开始

### 安装

```bash
cd ~/.claude/skill-manager
python skill_manager.py scan
```

### 启用自动激活

**Windows**:
```bash
enable-skill-auto.bat
```

**手动配置**:
编辑 `data/config.json`:
```json
{
  "auto_activation_enabled": true,
  "default_choice": "always"
}
```

### CLI 使用

```bash
# 扫描技能
python skill_manager.py scan

# 列出所有技能
python skill_manager.py list

# 搜索技能
python skill_manager.py search nuwa

# 推荐技能
python skill_manager.py recommend "女娲，蒸馏马斯克"

# 查看详情
python skill_manager.py info nuwa-skill --metrics

# 性能指标
python skill_manager.py metrics
```

## 架构

```
skill-manager/
├── skill_manager.py          # 主程序 (独立运行)
├── enable-skill-auto.bat     # 启用自动激活
├── disable-skill-auto.bat    # 禁用自动激活
├── hooks/
│   ├── on_session_start.py   # Session Hook
│   └ on_prompt_submit.py     # Prompt Hook (可选)
├── data/
│   ├── registry.json         # 技能注册表 (37+)
│   └ config.json             # 配置文件
│   └ activation_history.json # 激活历史
└── docs/
    ├── README_FINAL.md       # 完整文档
    ├── ENABLE_DISABLE_GUIDE.md
    └ QUICKREF.md
    └ AUTO_ACTIVATION_GUIDE.md
```

## 配置

### 三种运行模式

| 模式 | 配置 | 行为 |
|------|------|------|
| **始终启用** | `"default_choice": "always"` | 每次启动自动激活 |
| **始终禁用** | `"default_choice": "never"` | 静默运行，不激活 |
| **询问模式** | `"default_choice": "ask"` | 显示提示，不激活 |

### 配置文件位置

`~/.claude/skill-manager/data/config.json`

## 示例

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

## 性能指标

- 启动延迟: +800ms
- 提示分析: <200ms
- 内存占用: +50MB
- 已扫描技能: 37 个

## 开发路线

### Phase 1 (完成) ✅
- 技能注册表
- CLI 工具
- 激活引擎
- Session Hook

### Phase 2 (计划)
- 上下文分析器
- 学习系统
- 智能路由

### Phase 3 (计划)
- 性能监控仪表板
- 告警系统

### Phase 4 (计划)
- 依赖管理
- 语义搜索
- 技能市场

## 文档

- [README_FINAL.md](docs/README_FINAL.md) - 完整系统文档
- [ENABLE_DISABLE_GUIDE.md](docs/ENABLE_DISABLE_GUIDE.md) - 启用/禁用指南
- [QUICKREF.md](docs/QUICKREF.md) - CLI 快速参考
- [AUTO_ACTIVATION_GUIDE.md](docs/AUTO_ACTIVATION_GUIDE.md) - 自动激活详细指南
- [PHASE1_REPORT.md](docs/PHASE1_REPORT.md) - Phase 1 技术报告

## 故障排查

### Hook 未运行
检查:
1. `~/.claude/settings.json` 是否包含 hook 配置
2. Python 路径是否正确
3. 文件是否存在

### 技能未检测
运行:
```bash
python skill_manager.py scan
```

### 配置不生效
检查:
```bash
cat ~/.claude/skill-manager/data/config.json
```

## 许可证

MIT License

## 作者

Claude Code

## 版本历史

- v0.1.0 (2026-07-01): Phase 1 完成 + Hooks 集成

---

**注意**: 此项目需要 Claude Code 环境。技能目录位于 `~/.claude/skills/`。