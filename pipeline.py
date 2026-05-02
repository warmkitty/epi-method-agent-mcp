"""
Epi-Method Agent - Pipeline Engine

Routes LLM calls through structured prompts with knowledge base context.
Each skill produces structured output; the pipeline chains them sequentially.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Resolve paths relative to this file
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"


def _load_kb(filename: str) -> str:
    """Load a knowledge base markdown file. Returns empty string if not found."""
    path = KNOWLEDGE_BASE_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"[知识库文件 {filename} 未找到]"


# ---------------------------------------------------------------------------
# Skill 1: Research Question Structuring
# ---------------------------------------------------------------------------

def skill_1_prompt(user_input: dict) -> str:
    """
    Build the system prompt for Skill 1: Research Question Structuring.
    The user_input dict should contain: disease, drug/intervention, 
    client_need, data_source, target_use.
    """
    kb_terminology = _load_kb("terminology.md")

    return f"""你是一个顶级流行病学与RWE方法学专家。请执行以下任务：

## 任务：研究问题结构化

### 输入信息
- 疾病领域：{user_input.get('disease', '未指定')}
- 药物/干预：{user_input.get('intervention', '未指定')}
- 客户需求：{user_input.get('client_need', '未指定')}
- 数据源：{user_input.get('data_source', '未指定')}
- 目标用途：{user_input.get('target_use', '未指定')}

### 要求
1. 判断研究类型：描述性 / 比较有效性 / 安全性 / 经济负担 / BIA / 预测模型
2. 构建 PICO/PECO 框架
3. 列出主要和次要研究目标
4. 明确可回答问题和不适合回答的问题

### 输出格式（严格按此格式）

【研究问题结构化结果】

**研究类型**：[类型名称]

**PICO/PECO框架**：
- P（Population）：...
- I/E（Intervention/Exposure）：...
- C（Comparator）：...
- O（Outcome）：...
- T（Time）：...

**主要研究目标**：
1. ...

**次要研究目标**：
1. ...

**可回答问题**：
- ...

**不适合回答问题**：
- ...

### 核心原则
- 先定义问题，再选方法
- 每个结论需要说明依据或逻辑
- 不输出空泛表述

### 术语参考
{kb_terminology[:3000]}
"""


# ---------------------------------------------------------------------------
# Skill 2: Fit-for-Purpose Data Assessment
# ---------------------------------------------------------------------------

def skill_2_prompt(user_input: dict, skill_1_output: str) -> str:
    """Build system prompt for Skill 2: Fit-for-Purpose Data Assessment."""
    kb_database = _load_kb("database_assumptions.md")

    return f"""你是一个顶级流行病学与RWE方法学专家。请执行以下任务：

## 任务：数据适用性评价（Fit-for-Purpose）

### 研究背景（来自研究问题结构化）
{skill_1_output}

### 数据源信息
- 数据源：{user_input.get('data_source', '未指定')}

### 要求
从以下7个维度评价数据适用性：

1. 人群识别能力
2. 暴露/治疗识别能力
3. 结局捕捉能力
4. 混杂变量支持能力
5. 随访完整性
6. 成本/资源利用分析能力
7. 主要局限

### 输出格式（严格按此格式）

【数据适用性评价】

| 评价维度 | 支持程度 | 说明 |
|---------|---------|------|
| 1. 人群识别能力 | 高/中/低/不支持 | ... |
| 2. 暴露/治疗识别能力 | 高/中/低/不支持 | ... |
| 3. 结局捕捉能力 | 高/中/低/不支持 | ... |
| 4. 混杂变量支持能力 | 高/中/低/不支持 | ... |
| 5. 随访完整性 | 高/中/低/不支持 | ... |
| 6. 成本/资源利用分析能力 | 高/中/低/不支持 | ... |
| 7. 主要局限 | — | ... |

**可行性结论**：[可直接做 | 可探索做 | 需外部数据补充 | 不建议做]

**依据**：...

### 数据能力参考
{kb_database[:4000]}
"""


# ---------------------------------------------------------------------------
# Skill 3: Target Trial Emulation
# ---------------------------------------------------------------------------

def skill_3_prompt(user_input: dict, skill_1_output: str, skill_2_output: str) -> str:
    """Build system prompt for Skill 3: Target Trial Emulation."""
    kb_terminology = _load_kb("terminology.md")

    return f"""你是一个顶级流行病学与RWE方法学专家。请执行以下任务：

## 任务：Target Trial Emulation（目标试验模拟）

### 研究背景
{skill_1_output}

### 数据适用性评价
{skill_2_output}

### 要求
如果研究类型为描述性（无对照组），输出"本研究为描述性研究，无需 Target Trial Emulation"并结束。
如果为比较性研究，按以下9要素构建 TTE 框架：

### 输出格式（严格按此格式）

【Target Trial Emulation 框架】

1. **Eligibility criteria（入组标准）**
   - 治疗组：...
   - 对照组：...

2. **Treatment strategies（治疗策略定义）**
   - 治疗组：...
   - 对照组：...

3. **Assignment（分组时刻）**
   - ...

4. **Time zero（起点定义）⚠️ 关键**
   - 治疗组 Time Zero：...
   - 对照组 Time Zero：...
   - Time Zero 不一致检查：...

5. **Follow-up（随访起点与终点）**
   - 起点：...
   - 终点：...
   - 允许间隔：...

6. **Outcome（结局定义）**
   - 主要结局：...
   - 次要结局：...

7. **Causal contrast（因果对比）**
   - ...

8. **Analysis plan（分析方案）**
   - ...

9. **Key deviations from ideal RCT（与理想RCT的主要偏离）**
   - ...

### 术语参考
{kb_terminology[:2000]}
"""


# ---------------------------------------------------------------------------
# Skill 4: Bias Diagnosis
# ---------------------------------------------------------------------------

def skill_4_prompt(user_input: dict, skill_1_output: str, skill_2_output: str, skill_3_output: str) -> str:
    """Build system prompt for Skill 4: Bias Diagnosis."""
    kb_bias = _load_kb("bias_library.md")

    return f"""你是一个顶级流行病学与RWE方法学专家。请执行以下任务：

## 任务：偏倚诊断（Bias Diagnosis）⚠️ 最重要的技能

### 研究背景
{skill_1_output}

### 数据适用性
{skill_2_output}

### Target Trial 框架
{skill_3_output}

### 要求
必须逐项检查以下偏倚清单。对于**不适用**的偏倚，说明不适用原因。

**必须检查的偏倚清单**：
1. Confounding by indication（适应症混杂）
2. Immortal time bias（不朽时间偏倚）— 优先级最高
3. Selection bias（选择偏倚）
4. Misclassification（错分偏倚）
5. Informative censoring（知情删失）
6. Missing data（缺失数据）
7. Calendar-time bias（日历时间偏倚）
8. Competing risk（竞争风险）
9. Depletion of susceptibles（易感者消耗）
10. Coding drift / upcoding（编码漂移/升级编码）

### 输出格式（严格按此格式）

【偏倚诊断结果】

| 偏倚类型 | 发生机制 | 对结果方向的可能影响 | 诊断方法 | 应对策略 | 残余风险 |
|---------|---------|-------------------|---------|---------|---------|
| ... | ... | 高估/低估/未知 | ... | ... | 高/中/低 |

**偏倚优先级排序（高→低）**：
1. ...
2. ...

**因果推断可信度评级**：[高 | 中 | 低 | 不可靠]
**依据**：...

### 偏倚知识库参考
{kb_bias[:5000]}
"""


# ---------------------------------------------------------------------------
# Pipeline: Full execution
# ---------------------------------------------------------------------------

def build_pipeline_prompts(user_input: dict, skills: list[str] | None = None) -> list[dict]:
    """
    Build the full pipeline of prompts for sequential execution.

    Args:
        user_input: Dict with keys: disease, intervention, client_need, data_source, target_use
        skills: List of skill IDs to run, e.g. ["1","2","3","4"].
                Defaults to all 4 skills.

    Returns:
        List of dicts: [{"skill_id": str, "prompt": str, "depends_on": list[str]}]
    """
    if skills is None:
        skills = ["1", "2", "3", "4"]

    pipeline = []

    if "1" in skills:
        pipeline.append({
            "skill_id": "1",
            "skill_name": "研究问题结构化",
            "prompt": skill_1_prompt(user_input),
            "depends_on": [],
        })

    if "2" in skills:
        pipeline.append({
            "skill_id": "2",
            "skill_name": "数据适用性评价",
            "prompt": skill_2_prompt(user_input, "{{skill_1_output}}"),
            "depends_on": ["1"],
        })

    if "3" in skills:
        pipeline.append({
            "skill_id": "3",
            "skill_name": "Target Trial Emulation",
            "prompt": skill_3_prompt(user_input, "{{skill_1_output}}", "{{skill_2_output}}"),
            "depends_on": ["1", "2"],
        })

    if "4" in skills:
        pipeline.append({
            "skill_id": "4",
            "skill_name": "偏倚诊断",
            "prompt": skill_4_prompt(
                user_input, "{{skill_1_output}}", "{{skill_2_output}}", "{{skill_3_output}}"
            ),
            "depends_on": ["1", "2", "3"],
        })

    return pipeline


def build_single_skill_prompt(user_input: dict, skill_id: str, context: dict[str, str] | None = None) -> str:
    """
    Build a prompt for a single skill execution.

    Args:
        user_input: User input dict
        skill_id: "1", "2", "3", or "4"
        context: Dict mapping "skill_1_output", "skill_2_output", etc. to their outputs.
                 Only needed for skills with dependencies.

    Returns:
        The prompt string ready to send to LLM.
    """
    ctx = context or {}

    if skill_id == "1":
        return skill_1_prompt(user_input)
    elif skill_id == "2":
        return skill_2_prompt(user_input, ctx.get("skill_1_output", "[前序输出缺失]"))
    elif skill_id == "3":
        return skill_3_prompt(
            user_input,
            ctx.get("skill_1_output", "[前序输出缺失]"),
            ctx.get("skill_2_output", "[前序输出缺失]"),
        )
    elif skill_id == "4":
        return skill_4_prompt(
            user_input,
            ctx.get("skill_1_output", "[前序输出缺失]"),
            ctx.get("skill_2_output", "[前序输出缺失]"),
            ctx.get("skill_3_output", "[前序输出缺失]"),
        )
    else:
        raise ValueError(f"Unknown skill_id: {skill_id}. Must be 1, 2, 3, or 4.")


def list_knowledge_base_files() -> list[str]:
    """List available knowledge base files."""
    if KNOWLEDGE_BASE_DIR.exists():
        return [f.name for f in KNOWLEDGE_BASE_DIR.iterdir() if f.suffix == ".md"]
    return []
