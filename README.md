# AI Git Commit Message Generator

> Auto-generate conventional commit messages from git diff. Zero dependencies, single file Python script.

[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)]()

## Features

- **Smart Type Detection**: Automatically detects feat/fix/docs/refactor/perf/test/ci/build/chore
- **Conventional Commits**: Follows the [Conventional Commits](https://www.conventionalcommits.org/) specification
- **Bilingual**: Supports English and Chinese commit messages (`--lang en/zh`)
- **Interactive Mode**: Choose from multiple generated suggestions (`-i`)
- **Scope Detection**: Auto-detects scope from directory structure and file types
- **JSON Output**: Structured output for CI/CD integration (`--json`)
- **Zero Dependencies**: Pure Python, no pip install needed
- **Single File**: Just download and run

## Quick Start

```bash
# Download
curl -O https://raw.githubusercontent.com/wynn2025/ai-git-commit-generator/main/ai_git_commit_generator.py

# Make some changes, then stage them
git add .

# Generate commit message
python3 ai_git_commit_generator.py --staged

# Output:
# feat(src): add user authentication module
#
# Changed 3 file(s)
# +45 additions, -12 deletions
#   src/auth.py (+30/-5)
#   src/models.py (+10/-2)
#   src/routes.py (+5/-5)
```

## Usage

```bash
# Basic - analyze unstaged changes
python3 ai_git_commit_generator.py

# Analyze staged changes
python3 ai_git_commit_generator.py --staged

# Chinese commit messages
python3 ai_git_commit_generator.py --staged --lang zh

# Interactive mode - choose from 3 suggestions
python3 ai_git_commit_generator.py --staged -i

# Generate and commit
python3 ai_git_commit_generator.py --staged --commit

# JSON output for scripts
python3 ai_git_commit_generator.py --staged --json

# Analyze a saved diff file
python3 ai_git_commit_generator.py --diff-file changes.diff
```

## Commit Type Detection Rules

| Type | Trigger |
|------|---------|
| `feat` | New files, mostly additions in source code |
| `fix` | Diff contains "fix", "bug", "issue" keywords |
| `docs` | Only .md/.rst/.txt files changed |
| `style` | Only CSS/SCSS files changed |
| `refactor` | More deletions than additions, or pure deletions |
| `perf` | Diff contains "performance", "optimize", "speed up" |
| `test` | Only test/spec files changed |
| `ci` | CI config files changed |
| `build` | Build files changed (Makefile, package.json, Dockerfile) |
| `revert` | Diff contains "revert" keyword |

## Output Formats

### Conventional Commits (default)
```
feat(auth): add JWT token validation

Changed 2 file(s)
+15 additions, -3 deletions
  auth/validator.py (+12/-1)
  auth/middleware.py (+3/-2)
```

### Chinese
```
feat(auth): 新功能: auth
```

## GitHub Actions Integration

```yaml
name: Auto Commit Message
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  suggest-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Generate commit message
        run: |
          python3 ai_git_commit_generator.py --staged --json > commit_msg.json
```

## Why This Tool?

- `git commit -m "fix stuff"` -> **bad**
- `git commit -m "fix(api): resolve null pointer in user endpoint"` -> **good**
- This tool generates the **good** version automatically

---

## 💰 商品信息

| 项目 | 内容 |
|------|------|
| **闲鱼售价** | **¥19.9**（原价¥49，限时特惠） |
| **一句话卖点** | git diff一键生成Conventional Commits规范提交信息——程序员每日提效神器 |
| **交付形式** | 完整Python源码(392行) + 详细README文档 + MIT开源协议(可商用) |
| **运行环境** | Python 3.6+，零依赖，无需API Key |
| **适合人群** | 程序员 / 技术团队负责人 / 开源项目维护者 / DevOps工程师 |
| **上架状态** | ✅ 可上架 |

> 📦 购买即获：源码 + 文档 + 永久使用 + 持续更新

## License

MIT License - see [LICENSE](LICENSE)
