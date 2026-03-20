---
name: create-project-skill
description: "为任意项目生成配套的 Claude Code Skill 文件。包含两个文件：commands/ 下的精简执行指令（Claude 用）和 skills/ 下的完整用户文档（SKILL.md）。当用户说'帮我生成一个项目的 Skill'或'为这个项目创建 Skill'时使用。"
argument-hint: "[项目名称或项目路径]"
allowed-tools: Bash, Read, Write, Glob
---

# Project Skill Generator

为现有项目生成标准化的 Claude Code Skill 文件，采用双文件结构：精简执行指令 + 完整用户文档。

## Workflow

**Step 1 · 理解项目**

如果用户没有提供项目路径，询问：
- 项目目录在哪里？
- 这个项目的核心功能是什么？
- 用户触发这个 skill 时，期望 Claude 做什么？

读取项目目录下的关键文件来理解项目：
```bash
ls {项目目录}
cat {项目目录}/README.md 2>/dev/null || true
```

重点理解：
- 项目做什么（功能）
- 如何运行（命令、脚本）
- 输入是什么、输出是什么
- 有哪些使用场景

**Step 2 · 生成 commands/ 文件**

在 `{项目目录}/.claude/commands/{skill-name}.md` 创建精简执行指令文件。

**这个文件是给 Claude 看的**，要求：
- 简洁，控制在 50-80 行
- 用 Workflow / Step 结构描述执行步骤
- 包含关键技术原则和注意事项
- 不需要介绍背景，直接讲怎么做

模板结构：
```markdown
---
name: {skill-name}
description: "{一句话描述，包含触发场景}"
argument-hint: "[可选参数说明]"
allowed-tools: Bash, Read, Write, Edit, Glob
---

# {Skill 标题}

{一句话说明 skill 的职责}

## Workflow

**Step 1 · {步骤名}**
{具体操作描述}

**Step 2 · {步骤名}**
{具体操作描述}

## Key Principles

- {关键原则1}
- {关键原则2}
```

**Step 3 · 生成 skills/SKILL.md 文件**

在 `{项目目录}/skills/{skill-name}/SKILL.md` 创建完整用户文档。

**这个文件是给用户看的**，要求：
- 详细，包含所有必要信息
- 用标准七段结构（见下方）
- 提供 2-3 个真实使用示例
- 语气面向用户，解释能做什么，而非告诉 Claude 怎么做

标准七段结构：
```markdown
---
name: {skill-name}
description: "{详细描述，含英文关键词便于触发}"
---

# {Skill 标题}

## Purpose
{2-3句话说明用途和价值}

## How It Works
### Step 1: {步骤名}
### Step 2: {步骤名}
...

## Usage Examples
**示例 1：{场景}**
**示例 2：{场景}**
**示例 3：{场景}**

## Key Capabilities
- **{能力名}**：{说明}

## Tips for Best Results
1. {建议1}
2. {建议2}

## Output Format
{描述用户最终会得到什么}

### Related
- [链接名](URL)
```

**Step 4 · 同步到全局 commands**

将 commands 文件同步到 `~/.claude/commands/`，让该 skill 在所有项目中都可触发：

```bash
cp {项目目录}/.claude/commands/{skill-name}.md ~/.claude/commands/{skill-name}.md
```

**Step 5 · 提交推送**

```bash
cd {项目目录}
git add .claude/ skills/
git commit -m "Add {skill-name} skill (commands + SKILL.md)"
git push
```

输出两个文件的 GitHub 链接。

## Key Principles

- commands/ 文件：精简、执行导向，Claude 的操作手册
- SKILL.md 文件：详细、用户导向，人类的使用说明书
- description 字段同时写中英文，提高 Claude 自动触发准确率
- 使用示例要用真实场景，不要用假数据
- allowed-tools 按实际需要填写，不要全部开放
