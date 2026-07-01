# Skill Manager - 自动激活使用指南

## 功能说明

**每次使用 Claude 时询问是否启用自动激活**

系统会在会话启动时询问您的选择：
- **Y (Yes)** - 本次会话启用
- **N (No)** - 本次会话禁用
- **A (Always)** - 所有会话启用（不再询问）
- **S (Skip)** - 所有会话禁用（不再询问）
- **I (Info)** - 查看详细信息

## 工作流程

### 1. 会话启动时

```
============================================================
  Skill Manager - Auto-Activation
============================================================

  Do you want to enable automatic skill activation?
  This will analyze your prompts and recommend relevant skills.

  Options:
    [Y] Yes - Enable for this session
    [N] No  - Disable for this session
    [A] Always - Enable for all future sessions
    [S] Skip - Don't ask again (disable)
    [I] Info - Show more information

============================================================
  Your choice [Y/N/A/S/I]:
```

### 2. 输入提示时（如果启用）

当您输入提示词时，系统会自动分析并推荐相关技能：

```
[Skill Manager] Detected skills:
  - nuwa-skill (0.85, keyword, name)
  - github-code-review (0.72, semantic)
  - humanizer (0.65, keyword)

  Tip: Use skills by mentioning their triggers in your prompt.
  Disable: Edit ~/.claude/skill-manager/data/config.json
```

## 配置文件

位置: `~/.claude/skill-manager/data/config.json`

```json
{
  "auto_activation_enabled": false,
  "default_choice": "ask",
  "session_count": 0
}
```

### 手动配置

- **始终启用**: 设置 `"default_choice": "always"`
- **始终禁用**: 设置 `"default_choice": "never"`
- **每次询问**: 设置 `"default_choice": "ask"`

## 已集成的 Hooks

1. **SessionStart Hook** - 启动时询问
   - 文件: `hooks/on_session_start.py`
   - 触发: Claude 会话开始

2. **UserPromptSubmit Hook** - 分析提示词
   - 文件: `hooks/on_prompt_submit.py`
   - 触发: 用户提交提示词时
   - 条件: 仅在启用时运行

## 使用示例

### 示例 1: 蒸馏人物思维

```
用户输入: 女娲，蒸馏马斯克的思维方式

系统检测:
  - nuwa-skill (置信度 0.85)
  - 匹配层级: keyword, name

推荐: 自动激活女娲技能
```

### 示例 2: 代码审查

```
用户输入: review 这个PR的代码质量

系统检测:
  - github-code-review (置信度 0.72)
  - verification-quality (置信度 0.68)

推荐: 代码审查技能组合
```

### 示例 3: 学术写作

```
用户输入: 我想润色这篇医学论文

系统检测:
  - humanizer_academic (置信度 0.78)
  - confluencia (置信度 0.65)

推荐: 学术润色技能
```

## 性能影响

- **启动延迟**: +800ms（询问界面）
- **提示分析**: <200ms（自动激活）
- **内存占用**: +50MB（注册表 + 历史）
- **总体影响**: 最小，可随时禁用

## 禁用方法

1. **临时禁用**: 会话启动时选择 N
2. **永久禁用**: 会话启动时选择 S
3. **手动禁用**: 编辑 config.json 设置 `"default_choice": "never"`

## 故障排查

### 问题 1: Hook 未运行

**检查**:
- `~/.claude/settings.json` 中是否添加了 hooks
- Python 是否可执行（`python --version`）
- 文件路径是否正确

### 问题 2: 技能未检测

**检查**:
- 运行 `skill_manager.py scan` 重建注册表
- 检查 `data/registry.json` 是否存在
- 确认技能有 SKILL.md 文件

### 问题 3: 编码问题

**解决**:
- Windows 可能显示乱码（GBK 编码）
- 功能正常，仅显示问题
- 可编辑脚本添加 UTF-8 强制输出

## 下一步计划

- Phase 2: 上下文分析器
- Phase 3: 学习系统（用户偏好）
- Phase 4: 智能路由（意图分类）

## 版本信息

- **当前版本**: 0.1.0
- **状态**: Phase 1 完成 + Hooks 集成
- **最后更新**: 2026-07-01

---

**相关文档**:
- `README.md` - 完整系统文档
- `QUICKREF.md` - CLI 快速参考
- `PHASE1_REPORT.md` - Phase 1 完成报告