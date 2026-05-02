# 流行病学与RWE方法学术语表

> 版本：v1.0 | 维护：按项目经验持续更新

---

## 一、核心因果推断概念

| 术语 | 定义 | 使用场景 |
|------|------|----------|
| **Estimand** | 研究要估计的目标量，由ICH E9(R1)定义，包括人群、变量、汇总统计量和处理插补策略 | 所有RCT和RWE设计 |
| **ATE** | Average Treatment Effect，全人群平均治疗效应：E[Y(1)] - E[Y(0)] | 政策评估、医保准入 |
| **ATT** | Average Treatment Effect on the Treated，实际接受治疗人群的平均效应 | IPTW/OW分析 |
| **ATC** | Average Treatment Effect on the Controls | 反事实推断 |
| **LATE** | Local Average Treatment Effect，仅适用于依从者（IV估计目标） | 工具变量分析 |
| **Potential outcomes** | Rubin因果框架：Y(1), Y(0)，每人有两个潜在结局，只能观察其中一个 | 因果推断理论基础 |
| **Exchangeability** | 条件可交换性：P(Y(a)|A=1,L) = P(Y(a)|A=0,L)，即条件独立假设（无未测混杂） | 观察性研究核心假设 |
| **Positivity** | 正值性：P(A=a|L=l) > 0，每个协变量层都有足够的处理/对照人数 | 倾向评分分析 |
| **Consistency** | 一致性：观测结局等于潜在结局，即干预定义明确 | SUTVA的一部分 |
| **SUTVA** | Stable Unit Treatment Value Assumption：无干扰假设 + 一致性 | 所有因果推断 |

---

## 二、研究设计框架

| 术语 | 定义 | 备注 |
|------|------|------|
| **Target Trial** | 理想随机对照试验的假设设计，用于指导RWE设计 | Hernán & Robins框架 |
| **TTE** | Target Trial Emulation，模拟目标试验 | RWE因果推断标准路径 |
| **New user design** | 只纳入首次开始治疗的患者，避免活跃使用者偏倚 | 比较有效性研究必选 |
| **Active comparator** | 用同类药物作为对照，而非空白对照 | 控制适应症混杂 |
| **ACNU design** | Active Comparator + New User design 的组合 | RWE黄金标准设计 |
| **Prevalent user bias** | 纳入已用药患者导致的偏倚，脱落偏倚的一种 | New user design解决 |
| **Immortal time bias** | 从队列进入到首次暴露之间的时间段被错误算入暴露组 | 时间零点定义错误导致 |
| **Time zero** | 随访开始的时间点，必须与治疗分配同步 | TTE核心要素 |
| **Index date** | 患者进入队列的日期（通常=time zero） | 数据清洗关键变量 |

---

## 三、统计方法术语

| 术语 | 全称 | 适用场景 |
|------|------|----------|
| **IPTW** | Inverse Probability of Treatment Weighting | 混杂控制，估计ATE |
| **OW** | Overlap Weighting，重叠权重 | 倾向评分极端值问题，估计ATO |
| **ATO** | Average Treatment Effect in the Overlap Population | OW估计目标 |
| **PS** | Propensity Score，倾向评分 = P(A=1\|L) | IPTW/匹配/分层 |
| **SMD** | Standardized Mean Difference，标准化均数差 | 协变量平衡检验（<0.1为平衡） |
| **G-formula** | G-computation formula，标准化直接计算法 | 时变混杂、复杂干预 |
| **TMLE** | Targeted Maximum Likelihood Estimation | 双重稳健估计，高维数据 |
| **DiD** | Difference-in-Differences，双重差分 | 准自然实验，政策评估 |
| **IV** | Instrumental Variable，工具变量 | 未测混杂存在时 |
| **RD** | Risk Difference，风险差 | 二元结局绝对效应 |
| **RR** | Risk Ratio/Relative Risk | 二元结局相对效应 |
| **OR** | Odds Ratio | 病例对照、logistic回归 |
| **HR** | Hazard Ratio，风险比 | Cox比例风险模型 |
| **SHR** | Sub-distribution Hazard Ratio | Fine-Gray竞争风险模型 |
| **CIF** | Cumulative Incidence Function | 竞争风险存在时的发生率 |
| **MPR** | Medication Possession Ratio，药物拥有率 | 依从性指标 |
| **PDC** | Proportion of Days Covered，覆盖天数比例 | 依从性指标（更推荐） |

---

## 四、研究目标与结局术语

| 术语 | 定义 | 数据来源 |
|------|------|----------|
| **PICO** | Population/Intervention/Comparator/Outcome | 干预研究框架 |
| **PECO** | Population/Exposure/Comparator/Outcome | 观察性研究框架 |
| **Primary outcome** | 主要结局，研究假设直接针对的结局 | 预注册时需明确 |
| **Composite endpoint** | 复合终点，多个结局合并为一个（如MACE） | 提高事件率，但解释复杂 |
| **Hard endpoint** | 硬终点：死亡、住院等客观事件 | 医保数据可捕捉 |
| **Surrogate endpoint** | 替代终点：如HbA1c、LDL | 需验证与硬终点相关性 |
| **MACE** | Major Adverse Cardiovascular Events | 心血管安全性研究 |
| **LOT** | Line of Therapy，治疗线次 | 肿瘤学研究核心变量 |
| **TTD** | Time to Discontinuation | 持续性研究结局 |
| **TTP** | Time to Progression | 肿瘤学进展结局 |
| **OS** | Overall Survival | 全因死亡 |

---

## 五、数据类型术语

| 术语 | 定义 |
|------|------|
| **RWD** | Real-World Data，真实世界数据 |
| **RWE** | Real-World Evidence，真实世界证据 |
| **Claims data** | 理赔数据/医保结算数据（中国语境=医保数据） |
| **EMR/EHR** | Electronic Medical/Health Records，电子病历 |
| **Registry** | 注册数据库，通常有主动随访和标准化数据收集 |
| **Linked data** | 多源数据链接（如医保+EMR+死亡登记） |
| **Wash-out period** | 冲洗期，排除既往用药者的观察窗口 | 
| **Look-back period** | 回顾期，在index date前的数据窗口（用于定义纳排标准） |
| **Follow-up period** | 随访期，index date后观察结局的时间窗口 |

---

## 六、报告和监管框架

| 缩写 | 全称 | 用途 |
|------|------|------|
| **STROBE** | Strengthening the Reporting of Observational Studies in Epidemiology | 观察性研究报告规范 |
| **RECORD** | Reporting of studies Conducted using Observational Routinely-collected health Data | 常规数据研究报告规范 |
| **ISPOR** | International Society for Pharmacoeconomics and Outcomes Research | 卫生经济学/RWE方法标准 |
| **GRACE** | Good Research for Comparative Effectiveness | 比较有效性研究质量标准 |
| **ROBINS-I** | Risk Of Bias In Non-randomized Studies of Interventions | 非随机研究偏倚评估工具 |
| **E-value** | 未测混杂的最小效应量（sensitivity analysis工具） | 因果推断敏感性分析 |
| **BIA** | Budget Impact Analysis，预算影响分析 | 医保准入 |
| **CEA** | Cost-Effectiveness Analysis，成本效果分析 | HTA评估 |
| **ICER** | Incremental Cost-Effectiveness Ratio，增量成本效果比 | 准入阈值判断 |
