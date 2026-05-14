#!/usr/bin/env python3
"""
AI Git Commit Message Generator v1.0.0
Auto-generate conventional commit messages from git diff.
Supports English/Chinese and conventional commits format.

Author: AI Tools Workshop
Version: 1.0.0
License: MIT
"""

import os
import sys
import json
import argparse
import subprocess
from typing import Optional, List, Dict, Tuple

DEFAULT_LANG = "en"
DEFAULT_FORMAT = "conventional"
MAX_DIFF_LINES = 500

SUPPORTED_TYPES = {
    "feat": "A new feature",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "style": "Code formatting (no logic change)",
    "refactor": "Code refactoring (no new feature, no bug fix)",
    "perf": "Performance improvement",
    "test": "Adding or updating tests",
    "build": "Build system or dependency changes",
    "ci": "CI configuration changes",
    "chore": "Miscellaneous changes",
    "revert": "Revert a previous commit",
}

SUPPORTED_TYPES_ZH = {
    "feat": "新功能",
    "fix": "修复Bug",
    "docs": "文档变更",
    "style": "代码格式",
    "refactor": "重构",
    "perf": "性能优化",
    "test": "测试相关",
    "build": "构建系统",
    "ci": "CI配置",
    "chore": "杂项",
    "revert": "回退提交",
}


class DiffAnalyzer:
    """Analyze git diff to extract change information."""

    def __init__(self, diff_text: str):
        self.diff_text = diff_text
        self.files_changed: List[Dict] = []
        self.additions = 0
        self.deletions = 0
        self._parse()

    def _parse(self):
        current_file = None
        for line in self.diff_text.split("\n"):
            if line.startswith("diff --git"):
                if current_file:
                    self.files_changed.append(current_file)
                path = line.split(" b/")[-1] if " b/" in line else line.split()[-1]
                current_file = {"path": path, "additions": 0, "deletions": 0}
            elif line.startswith("+") and not line.startswith("+++"):
                if current_file:
                    current_file["additions"] += 1
                    self.additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                if current_file:
                    current_file["deletions"] += 1
                    self.deletions += 1
        if current_file:
            self.files_changed.append(current_file)

    def get_file_extensions(self) -> Dict[str, int]:
        exts = {}
        for f in self.files_changed:
            _, ext = os.path.splitext(f["path"])
            ext = ext.lower() if ext else "(no ext)"
            exts[ext] = exts.get(ext, 0) + 1
        return exts

    def get_changed_dirs(self) -> List[str]:
        dirs = set()
        for f in self.files_changed:
            d = os.path.dirname(f["path"])
            if d:
                dirs.add(d.split(os.sep)[0])
        return sorted(dirs)

    def summary(self) -> str:
        lines = [f"Files changed: {len(self.files_changed)}"]
        lines.append(f"+{self.additions} / -{self.deletions}")
        for f in self.files_changed[:20]:
            lines.append(f"  {f['path']} (+{f['additions']}/-{f['deletions']})")
        return "\n".join(lines)


class CommitMessageGenerator:
    """Generate conventional commit messages from diff analysis."""

    def __init__(self, lang: str = DEFAULT_LANG, format_type: str = DEFAULT_FORMAT):
        self.lang = lang
        self.format_type = format_type
        self.types = SUPPORTED_TYPES_ZH if lang == "zh" else SUPPORTED_TYPES

    def detect_type(self, analyzer: DiffAnalyzer) -> str:
        paths = [f["path"].lower() for f in analyzer.files_changed]

        if all("test" in p or "spec" in p for p in paths) and paths:
            return "test"

        if any(p.startswith(".github/workflows") or "Jenkinsfile" in p or ".gitlab-ci" in p for p in paths):
            return "ci"

        build_kw = ["Makefile", "package.json", "pom.xml", "requirements.txt", "Dockerfile", "docker-compose"]
        if any(any(bk in p for bk in build_kw) for p in paths):
            if analyzer.additions > analyzer.deletions:
                return "build"

        if all(p.endswith((".md", ".rst", ".txt")) or "README" in p or "LICENSE" in p for p in paths):
            return "docs"

        if all(p.endswith((".css", ".scss", ".less")) for p in paths) and paths:
            return "style"

        if analyzer.additions == 0 and analyzer.deletions > 0:
            return "refactor"

        diff_lower = analyzer.diff_text.lower()
        if "performance" in diff_lower or "optimize" in diff_lower or "speed up" in diff_lower:
            return "perf"
        if "fix" in diff_lower or "bug" in diff_lower or "issue" in diff_lower:
            return "fix"
        if "revert" in diff_lower:
            return "revert"

        src_exts = {".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".rb", ".php"}
        src_count = sum(1 for f in analyzer.files_changed if os.path.splitext(f["path"])[1] in src_exts)
        if src_count > 0 and analyzer.additions > analyzer.deletions:
            return "feat"

        if analyzer.deletions > analyzer.additions:
            return "refactor"

        return "feat"

    def detect_scope(self, analyzer: DiffAnalyzer) -> Optional[str]:
        dirs = analyzer.get_changed_dirs()
        if len(dirs) == 1:
            return dirs[0]
        exts = analyzer.get_file_extensions()
        if len(exts) == 1:
            ext = list(exts.keys())[0].replace(".", "")
            return ext if ext else None
        return None

    def generate_description(self, analyzer: DiffAnalyzer, commit_type: str) -> str:
        if self.lang == "zh":
            return self._desc_zh(analyzer, commit_type)
        return self._desc_en(analyzer, commit_type)

    def _desc_en(self, analyzer: DiffAnalyzer, commit_type: str) -> str:
        files = analyzer.files_changed
        n = len(files)
        if commit_type == "feat":
            if n == 1:
                return f"add {os.path.basename(files[0]['path'])}"
            exts = analyzer.get_file_extensions()
            if len(exts) == 1:
                return f"add {list(exts.keys())[0].replace('.', '')} support"
            return f"add feature for {', '.join(analyzer.get_changed_dirs()[:3])}"
        if commit_type == "fix":
            return f"fix issue in {', '.join(analyzer.get_changed_dirs()[:3])}"
        if commit_type == "docs":
            if n == 1:
                return f"update {os.path.basename(files[0]['path'])}"
            return "update documentation"
        if commit_type == "refactor":
            return f"refactor {', '.join(analyzer.get_changed_dirs()[:3])}"
        if commit_type == "perf":
            return f"optimize {', '.join(analyzer.get_changed_dirs()[:3])}"
        if commit_type == "test":
            return f"add tests for {', '.join(analyzer.get_changed_dirs()[:3])}"
        if commit_type == "ci":
            return "update CI configuration"
        if commit_type == "build":
            return "update build configuration"
        if commit_type == "style":
            return "format code"
        return f"update {', '.join(analyzer.get_changed_dirs()[:3])}"

    def _desc_zh(self, analyzer: DiffAnalyzer, commit_type: str) -> str:
        files = analyzer.files_changed
        n = len(files)
        dirs = analyzer.get_changed_dirs()[:3]
        type_desc = self.types.get(commit_type, "更新")
        if n == 1:
            return f"{type_desc}: {os.path.basename(files[0]['path'])}"
        if dirs:
            return f"{type_desc}: {' '.join(dirs)}"
        return f"{type_desc}: {n}个文件"

    def generate_body(self, analyzer: DiffAnalyzer) -> str:
        lines = []
        if self.lang == "zh":
            lines.append(f"变更文件: {len(analyzer.files_changed)}个")
            lines.append(f"新增: +{analyzer.additions}行, 删除: -{analyzer.deletions}行")
        else:
            lines.append(f"Changed {len(analyzer.files_changed)} file(s)")
            lines.append(f"+{analyzer.additions} additions, -{analyzer.deletions} deletions")
        for f in analyzer.files_changed[:10]:
            lines.append(f"  {f['path']} (+{f['additions']}/-{f['deletions']})")
        if len(analyzer.files_changed) > 10:
            lines.append(f"  ... and {len(analyzer.files_changed) - 10} more")
        return "\n".join(lines)

    def generate(self, analyzer: DiffAnalyzer) -> str:
        commit_type = self.detect_type(analyzer)
        scope = self.detect_scope(analyzer)
        description = self.generate_description(analyzer, commit_type)
        body = self.generate_body(analyzer)
        if self.format_type == "conventional":
            scope_str = f"({scope})" if scope else ""
            return f"{commit_type}{scope_str}: {description}\n\n{body}"
        elif self.format_type == "simple":
            return description
        else:
            return f"[{commit_type}] {description}\n\n{body}"

    def generate_multiple(self, analyzer: DiffAnalyzer) -> List[str]:
        messages = []
        orig_lang, orig_fmt = self.lang, self.format_type
        self.lang, self.format_type = "en", "conventional"
        messages.append(self.generate(analyzer))
        self.format_type = "simple"
        messages.append(self.generate(analyzer))
        self.lang, self.format_type = "zh", "conventional"
        messages.append(self.generate(analyzer))
        self.lang, self.format_type = orig_lang, orig_fmt
        return messages


def run_git(args: List[str], cwd: str = None) -> Tuple[int, str, str]:
    try:
        r = subprocess.run(["git"] + args, capture_output=True, text=True,
                           cwd=cwd, timeout=30, encoding="utf-8", errors="replace")
        return r.returncode, r.stdout, r.stderr
    except FileNotFoundError:
        print("Error: git not found in PATH", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: git command timed out", file=sys.stderr)
        sys.exit(1)


def get_diff(staged: bool = False, cwd: str = None) -> str:
    args = ["diff", "--cached"] if staged else ["diff"]
    code, out, err = run_git(args, cwd=cwd)
    return out


def commit_with_message(message: str, cwd: str = None) -> bool:
    code, out, err = run_git(["commit", "-m", message], cwd=cwd)
    if code == 0:
        print(out.strip())
        return True
    print(f"Commit failed: {err.strip()}", file=sys.stderr)
    return False


def interactive_select(messages: List[str]) -> str:
    print("\n" + "=" * 60)
    print("  Generated commit messages:")
    print("=" * 60)
    for i, msg in enumerate(messages, 1):
        print(f"\n  [{i}]")
        for line in msg.split("\n"):
            print(f"      {line}")
    print(f"\n  [e] Edit manually")
    print(f"  [q] Quit")
    while True:
        choice = input("\nChoice [1/2/3/e/q]: ").strip().lower()
        if choice in ("1", "2", "3") and int(choice) <= len(messages):
            return messages[int(choice) - 1]
        elif choice == "e":
            return input("Enter commit message: ").strip()
        elif choice == "q":
            print("Cancelled.")
            sys.exit(0)
        print("Invalid choice.")


def main():
    parser = argparse.ArgumentParser(
        description="AI Git Commit Message Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s                     Analyze unstaged changes\n"
               "  %(prog)s --staged            Analyze staged changes\n"
               "  %(prog)s --commit            Generate and auto-commit\n"
               "  %(prog)s --lang zh           Chinese commit messages\n"
               "  %(prog)s -i                  Interactive mode\n"
               "  %(prog)s --diff-file x.diff  Analyze a diff file\n"
               "  %(prog)s --json              Output as JSON\n")
    parser.add_argument("--staged", action="store_true", help="Analyze staged changes")
    parser.add_argument("--commit", action="store_true", help="Auto-commit with message")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--lang", choices=["en", "zh"], default="en", help="Language")
    parser.add_argument("--format", choices=["conventional", "simple"], default="conventional")
    parser.add_argument("--diff-file", help="Read diff from file")
    parser.add_argument("--cwd", help="Git repo path")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--dry-run", action="store_true", help="Show without committing")
    parser.add_argument("--version", action="version", version="v1.0.0")
    args = parser.parse_args()

    if args.diff_file:
        try:
            with open(args.diff_file, "r", encoding="utf-8") as f:
                diff_text = f.read()
        except FileNotFoundError:
            print(f"Error: {args.diff_file} not found", file=sys.stderr)
            sys.exit(1)
    else:
        if args.staged:
            diff_text = get_diff(staged=True, cwd=args.cwd)
        else:
            staged = get_diff(staged=True, cwd=args.cwd)
            unstaged = get_diff(staged=False, cwd=args.cwd)
            diff_text = staged if staged else unstaged
            if not diff_text:
                print("No changes detected. Working tree clean.")
                sys.exit(0)

    if not diff_text.strip():
        print("Empty diff.")
        sys.exit(0)

    lines = diff_text.split("\n")
    if len(lines) > MAX_DIFF_LINES:
        diff_text = "\n".join(lines[:MAX_DIFF_LINES])
        diff_text += f"\n... (truncated, {MAX_DIFF_LINES}/{len(lines)} lines)"

    analyzer = DiffAnalyzer(diff_text)
    gen = CommitMessageGenerator(lang=args.lang, format_type=args.format)

    if args.json:
        msg = gen.generate(analyzer)
        result = {
            "type": gen.detect_type(analyzer),
            "scope": gen.detect_scope(analyzer),
            "message": msg,
            "stats": {
                "files": len(analyzer.files_changed),
                "additions": analyzer.additions,
                "deletions": analyzer.deletions
            },
            "files": [{"path": f["path"], "+": f["additions"], "-": f["deletions"]}
                      for f in analyzer.files_changed]
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.interactive:
        messages = gen.generate_multiple(analyzer)
        selected = interactive_select(messages)
    else:
        selected = gen.generate(analyzer)
        print()
        print(selected)
        print()

    if args.commit and not args.dry_run:
        confirmed = input("Commit with this message? [Y/n]: ").strip().lower()
        if confirmed in ("", "y", "yes"):
            if commit_with_message(selected, cwd=args.cwd):
                print("Done!")
        else:
            print("Cancelled.")
    elif args.dry_run:
        print("(dry-run)")


if __name__ == "__main__":
    main()
# test comment
