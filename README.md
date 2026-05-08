# Epi-Method Agent v1.0

> 顶级流行病学与RWE方法学专家Agent。独立运行，支持单次和批量处理。

## 功能

自动执行 4 个核心 Skill，串联输出完整的方法学分析：

| Skill | 名称 | 输出 |
|-------|------|------|
| 1 | 研究问题结构化 | PICO/PECO + 研究类型 + 可答/不可答问题 |
| 2 | 数据适用性评价 | 七维评价表 + 可行性结论 |
| 3 | Target Trial Emulation | TTE 九要素框架 |
| 4 | 偏倚诊断 | 10种偏倚六列表 + 因果推断可信度评级 |

最终自动合并为 **Proposal Synopsis**。

---

## 安装

```bash
# 克隆
git clone https://github.com/warmkitty/epi-method-agent-mcp.git
cd epi-method-agent-mcp

# 安装依赖
pip install openai mcp[cli]
```

## 配置 LLM API Key

根据你使用的 LLM 提供商设置环境变量：

```bash
# OpenAI (默认)
set OPENAI_API_KEY=sk-xxxxx

# 阿里通义 (DashScope)
set DASHSCOPE_API_KEY=sk-xxxxx

# DeepSeek
set DEEPSEEK_API_KEY=sk-xxxxx

# 如果用 Azure OpenAI 或代理，额外设置：
set OPENAI_BASE_URL=https://your-endpoint/v1
```

---

## 使用方法

### 方式一：命令行直接输入

```bash
python agent.py ^
  --disease "oHCM" ^
  --drug "玛伐凯泰" ^
  --source "北京医保数据" ^
  --need "评估真实世界治疗模式和医疗资源消耗" ^
  --use "医保准入"
```

### 方式二：JSON 文件输入

```bash
python agent.py --input examples/rfp_example.json
```

JSON 格式：
```json
{
  "disease": "梗阻性肥厚型心肌病(oHCM)",
  "intervention": "玛伐凯泰(mavacamten)",
  "client_need": "评估真实世界治疗模式和医疗资源消耗",
  "data_source": "北京医保数据",
  "target_use": "医保准入"
}
```

### 方式三：批量处理（CSV）

```bash
python agent.py --batch examples/batch_example.csv --output ./results/
```

CSV 格式（必须包含以下列）：

| label | disease | intervention | client_need | data_source | target_use |
|-------|---------|-------------|-------------|-------------|------------|
| oHCM-玛伐凯泰 | oHCM | 玛伐凯泰 | 评估治疗模式 | 北京医保 | 医保准入 |

### 方式四：指定 LLM 和模型

```bash
# DeepSeek
python agent.py --input rfp.json --provider deepseek --model deepseek-chat

# 通义千问
python agent.py --input rfp.json --provider dashscope --model qwen-max

# 自定义 OpenAI 兼容接口
set OPENAI_BASE_URL=https://your-proxy/v1
python agent.py --input rfp.json --provider openai --model your-model
```

### 方式五：只跑部分 Skill

```bash
# 只跑 Skill 1 和 Skill 4
python agent.py --input rfp.json --skills 1,4
```

### 方式六：指定输出目录

```bash
python agent.py --input rfp.json --output ./my_analysis/
```

---

## 输出结构

```
outputs/
└── 20260508_232100/                    # 时间戳目录
    ├── 01_研究问题结构化.md
    ├── 02_数据适用性评价.md
    ├── 03_Target_Trial_Emulation.md
    ├── 04_偏倚诊断.md
    └── proposal_synopsis.md            # 自动合并的完整摘要
```

批量模式：
```
results/
├── oHCM-玛伐凯泰/
│   ├── 01_研究问题结构化.md
│   ├── ...
│   └── proposal_synopsis.md
├── T2D-SGLT2i/
│   ├── ...
│   └── proposal_synopsis.md
└── NSCLC-IO/
    └── ...
```

---

## 知识库

`knowledge_base/` 目录包含 10 个参考文件，每个 Skill 会自动加载相关知识：

- `terminology.md` — 术语表
- `database_assumptions.md` — 医保/EMR 数据能力边界
- `bias_library.md` — 13 种偏倚完整库
- `method_library.md` — 方法选择决策树
- `reporting_guidelines.md` — STROBE/RECORD/ISPOR/FDA 报告规范
- `01_question_structuring.md` ~ `04_bias_diagnosis.md` — 各 Skill 详细指引
- `AGENTS.md` — 总控规则

---

## MCP Server 模式（可选）

如果你使用 WorkBuddy，也可以把本仓库部署为 MCP Server：

```bash
# 配置 ~/.workbuddy/mcp.json
{
  "mcpServers": {
    "epi-method-agent": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "C:\\Users\\<用户名>\\.workbuddy\\mcp-servers\\epi-method-agent"
    }
  }
}
```

---

## 项目结构

```
epi-method-agent-mcp/
├── agent.py              # 独立运行入口（CLI + LLM + 批量）
├── pipeline.py           # Pipeline 引擎（Prompt 构建）
├── server.py             # MCP Server 入口（可选）
├── pyproject.toml        # 依赖配置
├── README.md             # 本文件
├── knowledge_base/       # 知识库（10 个 md）
├── examples/             # 示例文件
│   ├── rfp_example.json
│   └── batch_example.csv
└── outputs/              # 输出目录（自动创建）
```

---

## License

MIT
