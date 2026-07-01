# Skill Manager Quick Reference

## 已安装的命令别名

创建以下别名以便快速使用：

### Windows (CMD/PowerShell)
```powershell
# 添加到 PowerShell profile
function skill { python ~/.claude/skill-manager/skill_manager.py @args }
```

或使用批处理文件：
```cmd
%USERPROFILE%\.claude\skill-manager\skill.bat <command>
```

### Unix/Linux/Mac (Bash/Zsh)
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias skill='python ~/.claude/skill-manager/skill_manager.py'
```

或使用脚本：
```bash
~/.claude/skill-manager/skill.sh <command>
```

## 常用命令示例

### 技能管理

```bash
# 扫描并重建注册表
skill scan

# 列出所有技能
skill list

# 搜索技能
skill search "女娲"
skill search "代码审查"

# 查看技能详情
skill info nuwa-skill
skill info socrates --metrics

# 启用/禁用技能
skill enable nuwa-skill
skill disable verification-quality
```

### 自动激活

```bash
# 基于提示词推荐技能
skill recommend "女娲，蒸馏马斯克"
skill recommend "review 这个PR"
skill recommend "我想提升决策质量"

# 查看性能指标
skill metrics
skill metrics nuwa-skill
```

## 当前状态

- **版本**: 0.1.0 (Phase 1 完成)
- **已扫描技能**: 37 个
- **核心功能**:
  - ✓ 技能注册表
  - ✓ CLI 工具
  - ✓ 基础激活引擎
  - ✓ 搜索和推荐

## 下一步计划 (Phase 2)

- Hooks 集成（自动激活）
- 上下文分析器
- 智能路由
- 学习系统

## 文件位置

- 注册表: `~/.claude/skill-manager/data/registry.json`
- 激活历史: `~/.claude/skill-manager/data/activation_history.json`
- 主程序: `~/.claude/skill-manager/skill_manager.py`