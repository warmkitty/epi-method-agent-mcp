"""
Epi-Method Agent - MCP Server

Exposes the pipeline engine as MCP tools for LLM integration.

Tools:
  - run_pipeline: Execute the full 4-skill pipeline in one call
  - run_single_skill: Execute a specific skill (1-4) with optional context
  - list_skills: List available skills and their descriptions
  - get_knowledge_base: Retrieve a specific knowledge base document
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from pipeline import (
    build_pipeline_prompts,
    build_single_skill_prompt,
    list_knowledge_base_files,
    _load_kb,
)

# ---------------------------------------------------------------------------
# Create MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "Epi-Method Agent",
    json_response=True,
)


# ---------------------------------------------------------------------------
# Tool: run_pipeline
# ---------------------------------------------------------------------------

@mcp.tool()
def run_pipeline(
    disease: str,
    intervention: str,
    client_need: str,
    data_source: str,
    target_use: str,
    skills: str = "1,2,3,4",
) -> str:
    """Run the full Epi-Method Agent pipeline (Skills 1→2→3→4 sequentially).

    This is the primary tool. Provide research inputs and get structured
    prompts for each skill in the pipeline. The caller (LLM) should execute
    each prompt sequentially, passing outputs forward as context.

    Args:
        disease: Disease area (e.g., "oHCM", "2型糖尿病", "非小细胞肺癌")
        intervention: Drug or intervention (e.g., "玛伐凯泰", "SGLT2抑制剂")
        client_need: Client requirement description
        data_source: Data source (e.g., "北京医保数据", "EMR", "Registry")
        target_use: Target use case, one of: "洞察", "论文", "医保准入", "BIA", "RWE证据", "安全性研究"
        skills: Comma-separated skill IDs to run. Default "1,2,3,4" for all.

    Returns:
        JSON string containing the pipeline prompts and execution instructions.
    """
    user_input = {
        "disease": disease,
        "intervention": intervention,
        "client_need": client_need,
        "data_source": data_source,
        "target_use": target_use,
    }

    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    pipeline = build_pipeline_prompts(user_input, skill_list)

    result = {
        "pipeline": [],
        "execution_instruction": (
            "请按以下顺序执行每个 skill 的 prompt，"
            "将上一个 skill 的输出作为 context 传给下一个 skill。"
            "最终将所有 skill 的输出合并为一份完整的分析报告。"
        ),
    }

    for step in pipeline:
        result["pipeline"].append({
            "skill_id": step["skill_id"],
            "skill_name": step["skill_name"],
            "depends_on": step["depends_on"],
            "prompt": step["prompt"],
        })

    return json.dumps(result, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool: run_single_skill
# ---------------------------------------------------------------------------

@mcp.tool()
def run_single_skill(
    skill_id: str,
    disease: str = "",
    intervention: str = "",
    client_need: str = "",
    data_source: str = "",
    target_use: str = "",
    context_json: str = "",
) -> str:
    """Execute a single Epi-Method Agent skill.

    Use this when you only need one specific skill, or want to manually
    control the pipeline execution.

    Args:
        skill_id: Skill to run: "1" (问题结构化), "2" (数据适用性), "3" (TTE), "4" (偏倚诊断)
        disease: Disease area (required for skill 1)
        intervention: Drug/intervention (required for skill 1)
        client_need: Client requirement (required for skill 1)
        data_source: Data source name
        target_use: Target use case
        context_json: JSON string of previous skill outputs. Keys: "skill_1_output", "skill_2_output", etc.

    Returns:
        The prompt string for the requested skill.
    """
    user_input = {
        "disease": disease,
        "intervention": intervention,
        "client_need": client_need,
        "data_source": data_source,
        "target_use": target_use,
    }

    context = {}
    if context_json:
        try:
            context = json.loads(context_json)
        except json.JSONDecodeError:
            return json.dumps({
                "error": "context_json 格式错误，请提供合法的 JSON 字符串。",
                "example": '{"skill_1_output": "...", "skill_2_output": "..."}'
            }, ensure_ascii=False, indent=2)

    try:
        prompt = build_single_skill_prompt(user_input, skill_id, context)
    except ValueError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)

    skill_names = {
        "1": "研究问题结构化",
        "2": "数据适用性评价",
        "3": "Target Trial Emulation",
        "4": "偏倚诊断",
    }

    return json.dumps({
        "skill_id": skill_id,
        "skill_name": skill_names.get(skill_id, "未知"),
        "prompt": prompt,
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool: list_skills
# ---------------------------------------------------------------------------

@mcp.tool()
def list_skills() -> str:
    """List all available Epi-Method Agent skills with descriptions.

    Returns:
        JSON string with skill metadata.
    """
    skills = [
        {
            "skill_id": "1",
            "name": "研究问题结构化",
            "description": "将客户需求语言转化为研究语言。判断研究类型，构建PICO/PECO，明确可回答和不可回答问题。",
            "depends_on": [],
            "output_format": "研究类型 + PICO/PECO + 主要/次要目标 + 可答/不可答问题",
        },
        {
            "skill_id": "2",
            "name": "数据适用性评价（Fit-for-Purpose）",
            "description": "评价指定数据源对研究问题的支持能力。七维评价（人群识别、暴露识别、结局捕捉、混杂变量、随访、成本、局限），输出可行性结论。",
            "depends_on": ["1"],
            "output_format": "七维评价表 + 可行性结论（可直接做/可探索做/需补充/不建议）",
        },
        {
            "skill_id": "3",
            "name": "Target Trial Emulation（目标试验模拟）",
            "description": "将RWE研究设计得像RCT。九要素框架：入组标准、治疗策略、分组、Time Zero、随访、结局、因果对比、分析方案、RCT偏离。",
            "depends_on": ["1", "2"],
            "output_format": "TTE九要素表格 + Time Zero专项检查",
        },
        {
            "skill_id": "4",
            "name": "偏倚诊断（Bias Diagnosis）",
            "description": "最重要的技能。检查10种偏倚：适应症混杂、不朽时间偏倚、选择偏倚、错分偏倚、知情删失、缺失数据、日历时间偏倚、竞争风险、易感者消耗、编码漂移。",
            "depends_on": ["1", "2", "3"],
            "output_format": "偏倚六列表 + 优先级排序 + 因果推断可信度评级",
        },
    ]

    return json.dumps(skills, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool: get_knowledge_base
# ---------------------------------------------------------------------------

@mcp.tool()
def get_knowledge_base(filename: str = "") -> str:
    """Retrieve a knowledge base document for reference.

    Args:
        filename: Name of the knowledge base file. Leave empty to list available files.

    Returns:
        The content of the requested knowledge base file, or a list of available files.
    """
    if not filename:
        files = list_knowledge_base_files()
        return json.dumps({
            "available_files": files,
            "usage": "使用 get_knowledge_base(filename='文件名') 获取内容",
        }, ensure_ascii=False, indent=2)

    content = _load_kb(filename)
    return json.dumps({
        "filename": filename,
        "content": content,
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Tool: generate_proposal_synopsis
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_proposal_synopsis(
    skill_1_output: str,
    skill_2_output: str = "",
    skill_3_output: str = "",
    skill_4_output: str = "",
) -> str:
    """Generate a one-page proposal synopsis from skill outputs.

    Merges the outputs from all completed skills into a structured
    proposal synopsis ready for client presentation.

    Args:
        skill_1_output: Output from Skill 1 (研究问题结构化)
        skill_2_output: Output from Skill 2 (数据适用性评价), optional
        skill_3_output: Output from Skill 3 (Target Trial), optional
        skill_4_output: Output from Skill 4 (偏倚诊断), optional

    Returns:
        Markdown-formatted proposal synopsis.
    """
    sections = []

    sections.append("# 研究方案摘要（Protocol Synopsis）\n")
    sections.append("## 1. 研究问题结构化\n")
    sections.append(skill_1_output)

    if skill_2_output:
        sections.append("\n## 2. 数据适用性评价\n")
        sections.append(skill_2_output)

    if skill_3_output:
        sections.append("\n## 3. Target Trial Emulation\n")
        sections.append(skill_3_output)

    if skill_4_output:
        sections.append("\n## 4. 偏倚诊断\n")
        sections.append(skill_4_output)

    synopsis = "\n".join(sections)

    return json.dumps({
        "format": "markdown",
        "synopsis": synopsis,
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
