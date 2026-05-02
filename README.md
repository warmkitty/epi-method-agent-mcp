# Epi-Method Agent MCP Server

> 真实世界研究 / 药物流行病学 / 因果推断 / 医保数据研究方法学专家 Agent

## 概述

Epi-Method Agent 是一个基于 MCP（Model Context Protocol）的流行病学方法学专家系统，提供 4 个核心技能：

1. **研究问题结构化** — 将客户/RFP 语言转化为研究语言（PICO/PECO）
2. **数据适用性评价** — 七维评价数据源对研究问题的支持能力
3. **Target Trial Emulation** — 将 RWE 研究设计得像 RCT
4. **偏倚诊断** — 系统检查 10 种偏倚，输出因果推断可信度评级

## 安装

### 前提

- Python ≥ 3.10
- [WorkBuddy](https://codebuddy.cn) IDE
- Git

### 步骤

#### 1. 克隆仓库

```bash
git clone <仓库URL> %USERPROFILE%\.workbuddy\mcp-servers\epi-method-agent
```

#### 2. 安装依赖

```bash
cd %USERPROFILE%\.workbuddy\mcp-servers\epi-method-agent
pip install mcp[cli]
```

#### 3. 配置 WorkBuddy

打开（或创建）`%USERPROFILE%\.workbuddy\mcp.json`，写入：

```json
{
  "mcpServers": {
    "epi-method-agent": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "C:\\Users\\<你的用户名>\\.workbuddy\\mcp-servers\\epi-method-agent"
    }
  }
}
```

> 将 `<你的用户名>` 替换为实际用户名。

#### 4. 重启 WorkBuddy

重启后即可在对话中使用。

## 使用方法

在 WorkBuddy 对话中直接说：

```
请调用 epi-method-agent 的 run_pipeline：
- 疾病：oHCM（梗阻性肥厚型心肌病）
- 药物：玛伐凯泰
- 数据源：北京医保数据
- 需求：评估真实世界使用模式、医疗资源消耗、潜在 BIA
- 用途：医保准入
```

AI 会自动调取 MCP 的 `run_pipeline` 工具，返回 4 个技能的完整分析 prompts。

### 可用工具

| 工具 | 说明 |
|------|------|
| `run_pipeline` | 一次调用执行全部 4 个 Skill，返回串联的 prompts |
| `run_single_skill` | 单独执行某个 Skill |
| `list_skills` | 列出所有可用 Skill |
| `get_knowledge_base` | 查询知识库文件内容 |
| `generate_proposal_synopsis` | 合并各 Skill 输出为 proposal 摘要 |

## 项目结构

```
epi-method-agent/
├── server.py                              # MCP Server 入口
├── pipeline.py                            # Pipeline 引擎
├── pyproject.toml                         # 依赖配置
├── knowledge_base/                        # 方法学知识库
│   ├── AGENTS.md                          # 总控规则
│   ├── terminology.md                     # 术语表
│   ├── bias_library.md                    # 偏倚类型库
│   ├── database_assumptions.md            # 数据能力边界
│   ├── method_library.md                  # 方法选择决策树
│   ├── reporting_guidelines.md            # 报告规范
│   ├── 01_question_structuring.md         # Skill 1 详细指引
│   ├── 02_fit_for_purpose.md              # Skill 2 详细指引
│   ├── 03_target_trial_emulation.md       # Skill 3 详细指引
│   └── 04_bias_diagnosis.md               # Skill 4 详细指引
└── outputs/                               # 输出目录
```

## 技能说明

### Skill 1：研究问题结构化
- **输入**：疾病、药物、客户需求、数据源、目标用途
- **输出**：PICO/PECO、研究类型、主要/次要目标、可答/不可答问题

### Skill 2：数据适用性评价
- **评价维度**：人群识别、暴露识别、结局捕捉、混杂变量、随访、成本、局限
- **输出**：七维评价表 + 可行性结论

### Skill 3：Target Trial Emulation
- **九要素框架**：Eligibility criteria、Treatment strategies、Assignment、Time zero、Follow-up、Outcome、Causal contrast、Analysis plan、RCT 偏离
- **输出**：TTE 九要素表 + Time Zero 检查

### Skill 4：偏倚诊断（最重要）
- **必查偏倚**：适应症混杂、不朽时间偏倚、选择偏倚、错分偏倚、知情删失、缺失数据、日历时间偏倚、竞争风险、易感者消耗、编码漂移
- **输出**：偏倚六列表 + 因果推断可信度评级

## 版本

v1.0 — 4 个核心 Skill，2026-05-02
