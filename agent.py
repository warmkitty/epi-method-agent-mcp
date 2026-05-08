"""
Epi-Method Agent - Standalone Runner

Usage:
    # Single RFP
    python agent.py --disease "oHCM" --drug "玛伐凯泰" --source "北京医保" --need "评估真实世界治疗模式和医疗资源消耗" --use "医保准入"

    # From JSON file
    python agent.py --input rfp.json

    # Batch mode (CSV)
    python agent.py --batch rfps.csv --output ./results/

    # Specific skills only
    python agent.py --input rfp.json --skills 1,2

    # Use specific LLM
    python agent.py --input rfp.json --provider openai --model gpt-4o

Environment:
    OPENAI_API_KEY        - Required if provider=openai
    OPENAI_BASE_URL       - Optional, for custom endpoints (e.g. Azure, proxy)
    DASHSCOPE_API_KEY     - Required if provider=dashscope
    DEEPSEEK_API_KEY      - Required if provider=deepseek
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# LLM Provider Abstraction
# ---------------------------------------------------------------------------

class LLMProvider:
    """Base class for LLM providers."""

    def __init__(self, model: str):
        self.model = model

    def call(self, system: str, user: str, temperature: float = 0.3) -> str:
        raise NotImplementedError

    @classmethod
    def create(cls, provider: str, model: str | None = None) -> LLMProvider:
        if provider == "openai":
            return OpenAIProvider(model or "gpt-4o")
        elif provider == "dashscope":
            return DashScopeProvider(model or "qwen-max")
        elif provider == "deepseek":
            return DeepSeekProvider(model or "deepseek-chat")
        else:
            raise ValueError(f"Unknown provider: {provider}. Use openai/dashscope/deepseek.")


class OpenAIProvider(LLMProvider):
    """OpenAI / Azure OpenAI / compatible API."""

    def call(self, system: str, user: str, temperature: float = 0.3) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            print("[ERROR] openai package not installed. Run: pip install openai")
            sys.exit(1)

        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_BASE_URL", None),
        )
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""


class DashScopeProvider(LLMProvider):
    """Aliyun DashScope (Qwen)."""

    def call(self, system: str, user: str, temperature: float = 0.3) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            print("[ERROR] openai package not installed. Run: pip install openai")
            sys.exit(1)

        api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        if not api_key:
            print("[ERROR] DASHSCOPE_API_KEY not set")
            sys.exit(1)

        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""


class DeepSeekProvider(LLMProvider):
    """DeepSeek API."""

    def call(self, system: str, user: str, temperature: float = 0.3) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            print("[ERROR] openai package not installed. Run: pip install openai")
            sys.exit(1)

        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            print("[ERROR] DEEPSEEK_API_KEY not set")
            sys.exit(1)

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Agent Core
# ---------------------------------------------------------------------------

from pipeline import build_single_skill_prompt, build_pipeline_prompts, list_knowledge_base_files

SKILL_NAMES = {
    "1": "01_研究问题结构化",
    "2": "02_数据适用性评价",
    "3": "03_Target_Trial_Emulation",
    "4": "04_偏倚诊断",
}


def run_pipeline(
    user_input: dict,
    provider: LLMProvider,
    skills: list[str] | None = None,
    output_dir: Path | None = None,
    verbose: bool = True,
) -> dict[str, str]:
    """
    Execute the full pipeline: build prompts -> call LLM -> save outputs.

    Returns:
        Dict mapping skill_id to its output text.
    """
    if skills is None:
        skills = ["1", "2", "3", "4"]

    pipeline = build_pipeline_prompts(user_input, skills)
    results: dict[str, str] = {}

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    total = len(pipeline)
    for i, step in enumerate(pipeline, 1):
        skill_id = step["skill_id"]
        skill_name = step["skill_name"]
        prompt = step["prompt"]

        # Resolve template placeholders with previous outputs
        for prev_id, prev_output in results.items():
            placeholder = f"{{{{skill_{prev_id}_output}}}}"
            prompt = prompt.replace(placeholder, prev_output)

        if verbose:
            print(f"\n{'='*60}")
            print(f"[{i}/{total}] Skill {skill_id}: {skill_name}")
            print(f"{'='*60}")

        # Call LLM
        start = time.time()
        output = provider.call(
            system="你是一个顶级流行病学与RWE方法学专家。请严格按要求输出结构化内容。",
            user=prompt,
        )
        elapsed = time.time() - start

        if verbose:
            print(f"[OK] Completed in {elapsed:.1f}s")
            # Preview first 200 chars
            preview = output[:200].replace("\n", " ")
            print(f"[Preview] {preview}...")

        results[skill_id] = output

        # Save to file
        if output_dir:
            filename = f"{SKILL_NAMES.get(skill_id, f'skill_{skill_id}')}.md"
            filepath = output_dir / filename
            filepath.write_text(output, encoding="utf-8")
            if verbose:
                print(f"[Saved] {filepath}")

    # Generate proposal synopsis
    if output_dir and len(results) > 1:
        synopsis = _build_synopsis(results)
        synopsis_path = output_dir / "proposal_synopsis.md"
        synopsis_path.write_text(synopsis, encoding="utf-8")
        if verbose:
            print(f"\n[Synopsis] {synopsis_path}")

    return results


def _build_synopsis(results: dict[str, str]) -> str:
    """Merge all skill outputs into a proposal synopsis."""
    sections = [
        "# 研究方案摘要（Protocol Synopsis）",
        f"\n> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\n> Epi-Method Agent v1.0 — 4-Skill Pipeline Output\n",
    ]
    for skill_id in sorted(results.keys(), key=int):
        name = SKILL_NAMES.get(skill_id, f"Skill {skill_id}")
        sections.append(f"\n---\n\n## {name}\n")
        sections.append(results[skill_id])
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Batch Processing
# ---------------------------------------------------------------------------

def run_batch(
    csv_path: str,
    provider: LLMProvider,
    output_base: Path,
    skills: list[str] | None = None,
    verbose: bool = True,
):
    """Process multiple RFPs from a CSV file."""
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("[ERROR] CSV file is empty or has no data rows.")
        sys.exit(1)

    # Validate columns
    required = ["disease", "intervention", "client_need", "data_source", "target_use"]
    headers = list(rows[0].keys())
    missing = [c for c in required if c not in headers]
    if missing:
        print(f"[ERROR] CSV missing required columns: {missing}")
        print(f"  Found columns: {headers}")
        print(f"  Required columns: {required}")
        sys.exit(1)

    total = len(rows)
    for i, row in enumerate(rows, 1):
        user_input = {k: row[k] for k in required}
        # Use a label column if available, otherwise generate one
        label = row.get("label", row.get("name", f"RFP_{i:03d}"))

        print(f"\n{'#'*60}")
        print(f"# [{i}/{total}] Processing: {label}")
        print(f"{'#'*60}")

        out_dir = output_base / _safe_filename(label)
        try:
            run_pipeline(user_input, provider, skills, out_dir, verbose)
        except Exception as e:
            print(f"[ERROR] Failed to process '{label}': {e}")
            # Write error log
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "ERROR.log").write_text(str(e), encoding="utf-8")


def _safe_filename(name: str) -> str:
    """Convert a label to a safe directory name."""
    import re
    safe = re.sub(r'[\\/:*?"<>|\s]+', "_", name.strip())
    return safe[:80] if safe else "unnamed"


# ---------------------------------------------------------------------------
# Input Parsing
# ---------------------------------------------------------------------------

def parse_input_file(path: str) -> dict:
    """Parse a JSON input file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    required = ["disease", "intervention", "client_need", "data_source", "target_use"]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"[ERROR] Input JSON missing required keys: {missing}")
        sys.exit(1)
    return data


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Epi-Method Agent v1.0 - Standalone RWE Methodology Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py --disease "oHCM" --drug "玛伐凯泰" --source "北京医保" --need "评估真实世界治疗模式" --use "医保准入"
  python agent.py --input rfp.json
  python agent.py --batch rfps.csv --output ./results/
  python agent.py --input rfp.json --provider deepseek --model deepseek-chat
  python agent.py --input rfp.json --skills 1,4 --output ./partial/
        """,
    )

    # Input modes
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", "-i", help="Path to a JSON input file")
    input_group.add_argument("--batch", "-b", help="Path to a CSV file for batch processing")

    # Direct input (when not using --input or --batch)
    parser.add_argument("--disease", "-d", help="Disease area")
    parser.add_argument("--drug", help="Drug/intervention name")
    parser.add_argument("--source", "-s", help="Data source")
    parser.add_argument("--need", "-n", help="Client requirement description")
    parser.add_argument("--use", "-u", help="Target use case", choices=["洞察", "论文", "医保准入", "BIA", "RWE证据", "安全性研究"])

    # Output
    parser.add_argument("--output", "-o", help="Output directory (default: ./outputs/<timestamp>)")

    # Pipeline config
    parser.add_argument("--skills", help="Comma-separated skill IDs to run (default: 1,2,3,4)")
    parser.add_argument("--provider", "-p", help="LLM provider", choices=["openai", "dashscope", "deepseek"], default="openai")
    parser.add_argument("--model", "-m", help="Model name (default: provider-dependent)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    # Build user_input from args if --input not provided
    if args.input:
        user_input = parse_input_file(args.input)
    elif args.batch:
        pass  # batch mode handles its own input
    else:
        if not all([args.disease, args.drug, args.source, args.need, args.use]):
            parser.error("When not using --input or --batch, all of --disease, --drug, --source, --need, --use are required.")
        user_input = {
            "disease": args.disease,
            "intervention": args.drug,
            "client_need": args.need,
            "data_source": args.source,
            "target_use": args.use,
        }

    # Skills
    skills = None
    if args.skills:
        skills = [s.strip() for s in args.skills.split(",") if s.strip()]

    # Output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent / "outputs" / ts

    # Provider
    verbose = not args.quiet
    provider = LLMProvider.create(args.provider, args.model)

    if verbose:
        print(f"Epi-Method Agent v1.0")
        print(f"Provider: {args.provider} / {provider.model}")
        print(f"Skills: {skills or ['1','2','3','4']}")
        print(f"Output: {output_dir.resolve()}")

    # Execute
    if args.batch:
        run_batch(args.batch, provider, output_dir, skills, verbose)
    else:
        results = run_pipeline(user_input, provider, skills, output_dir, verbose)
        if verbose:
            print(f"\n{'='*60}")
            print(f"[DONE] {len(results)} skill(s) completed.")
            print(f"Output: {output_dir.resolve()}")
            print(f"{'='*60}")


if __name__ == "__main__":
    main()
