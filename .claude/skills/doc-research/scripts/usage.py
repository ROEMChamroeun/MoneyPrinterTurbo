#!/usr/bin/env python3
"""Print what each subagent of a Claude Code session cost, to compare research runs.

  python3 .claude/skills/doc-research/scripts/usage.py [session-id] [--match research]

Reads ~/.claude/projects/*/<session-id>/subagents/; without an id, the newest session of the project in
the current directory. "page chars" is the text that web tools and shell commands put into an agent's
context; every later turn re-reads it, which is what "cache read" counts.
"""

import argparse
import collections
import json
from pathlib import Path

WEB = ("WebSearch", "WebFetch", "Bash")


def agent_usage(log: Path) -> tuple[collections.Counter, collections.Counter, collections.Counter, str]:
    tokens, calls, chars = collections.Counter(), collections.Counter(), collections.Counter()
    seen, names, model = set(), {}, ""
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = entry.get("message") or {}
        content = msg.get("content") if isinstance(msg.get("content"), list) else []
        if entry.get("type") == "assistant":
            model = msg.get("model") or model
            if msg.get("id") not in seen and msg.get("usage"):
                seen.add(msg.get("id"))
                for key in ("cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
                    tokens[key] += msg["usage"].get(key) or 0
            for c in content:
                if c.get("type") == "tool_use":
                    calls[c["name"]] += 1
                    names[c["id"]] = c["name"]
        for c in content:
            if c.get("type") == "tool_result" and names.get(c.get("tool_use_id")) in WEB:
                result = c.get("content")
                chars[names[c["tool_use_id"]]] += len(result if isinstance(result, str) else json.dumps(result))
    return tokens, calls, chars, model


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("session", nargs="?", help="default: the newest session with subagents")
    parser.add_argument("--match", default="", help="only agents whose description contains this text")
    args = parser.parse_args()

    projects = Path.home() / ".claude" / "projects"
    if args.session:
        dirs = list(projects.glob(f"*/{args.session}/subagents"))
    else:
        here = projects / str(Path.cwd()).replace("/", "-")
        dirs = sorted(here.glob("*/subagents"), key=lambda d: d.stat().st_mtime, reverse=True)[:1]
    if not dirs:
        raise SystemExit(f"no subagents found for session {args.session or '(newest)'}")
    print(f"session {dirs[0].parent.name}")
    total = collections.Counter()
    for meta_path in sorted(dirs[0].glob("agent-*.meta.json")):
        meta = json.loads(meta_path.read_text())
        description = meta.get("description", "")
        if args.match.lower() not in description.lower():
            continue
        tokens, calls, chars, model = agent_usage(meta_path.with_name(meta_path.name.replace(".meta.json", ".jsonl")))
        total.update(tokens)
        total["tool calls"] += sum(calls.values())
        total["page chars"] += sum(chars.values())
        print(f"{description[:45]:45} {model.removeprefix('claude-'):14} calls {sum(calls.values()):4}  "
              f"page chars {sum(chars.values()):>9,}  cache read {tokens['cache_read_input_tokens']:>12,}  "
              f"out {tokens['output_tokens']:>7,}")
    print(f"TOTAL  tool calls {total['tool calls']:,}  page chars {total['page chars']:,}  "
          f"cache write {total['cache_creation_input_tokens']:,}  cache read {total['cache_read_input_tokens']:,}  "
          f"out {total['output_tokens']:,}")


if __name__ == "__main__":
    main()
