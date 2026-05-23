# ModWeaver（织模者）产品需求文档 V2.0

| 文档版本 | 修订日期   | 修订人   | 修订说明                                                     |
| :------- | :--------- | :------- | :----------------------------------------------------------- |
| V2.0     | 2026-05-22 | 产品团队 | 基于V1.1 MVP，进行战略与架构级升级，确立Agent Runtime核心方向 |
| V1.1     | 2026-05-22 | 产品团队 | 初始MVP版本，详见历史文档                                    |

**目标发布：2027年Q4**
**文档状态：草稿**
**许可协议：MIT 开源**

---

## 一、产品战略定位

### 1.1 产品重新定位

ModWeaver V2.0不再是单纯的“Minecraft模组管理器”，而是升级为：

> **一个 AI Agent 驱动的 Minecraft Runtime Orchestration Platform (运行时编排平台)**

它本质上是：
- **Agent Runtime**: 支持长生命周期、状态化AI Agent的执行环境。
- **Tool Orchestration**: 复杂工具链（搜索、依赖、下载、诊断等）的编排中心。
- **Execution Harness**: AI行为的沙箱、测试与验证平台。
- **Observable AI System**: 全过程、可观测、可调试的AI系统实验场。

### 1.2 产品愿景(V2)

成为开源社区中，用于探索和实践 **“可观测、可恢复、可回放的Agent Runtime System”** 的真实复杂环境实验平台。

### 1.3 核心升级理念

V1是“AI + Minecraft Tool”，V2升级为 **Runtime Engineering** 平台，重点从Prompt转向基础设施。

| 核心能力     | V1.0 MVP                   | V2.0 Runtime Focus                             |
| :----------- | :------------------------- | :--------------------------------------------- |
| **架构核心** | 功能导向的AI应用           | 长生命周期的Agent Runtime                      |
| **执行方式** | 线性函数调用 `agent.run()` | 工作流驱动、可恢复执行 `runtime.execute(task)` |
| **可观测性** | 基础日志                   | 全过程Execution Timeline、Trace、Metrics       |
| **持久化**   | 无/少量                    | 全状态持久化（Session/Memory/Execution）       |
| **可恢复性** | 崩溃后手动重试             | 自动Recovery、Replayable Execution             |
| **核心资产** | Minecraft模组组合          | Agent执行轨迹、内存、经验                      |

---

## 二、项目范围

### 2.1 范围内 (In Scope) - V2.0核心

- **Agent Runtime Core**：自研的Agent执行环境，管理状态、编排工具。
- **Execution Timeline**：提供Agent思考与执行全过程的可视化时间线。
- **Agent Memory System**：构建Session、Persistent、Execution、Failure四级记忆体系。
- **Replayable Execution**：支持全量、部分、确定性三种模式的执行回放。
- **Workflow Engine**：支持DAG（有向无环图）的工作流，具备重试、超时、并行能力。
- **Crash Diagnosis Pipeline**：结构化的崩溃日志分析与智能修复建议。
- **Tool Execution Layer**：定义并实现Mod Search, Dependency, Launch, Diagnose等核心工具。
- **Minecraft Runtime Layer**：作为Agent的沙箱环境，提供进程管理、日志流。

### 2.2 范围外 (Out of Scope) - 明确删减

为避免过度工程，V2.0 **不包含** 以下特性（部分可能在后续版本考虑）：
- mDNS服务自动发现与防火墙自动配置。
- 客户端-服务端差分增量同步。
- Java Agent级别的深度诊断模组（复杂度爆炸）。
- 云端协作、多用户共享执行环境。
- 图形化的、拖拽式的工作流编辑器（MVP阶段用代码/配置定义）。

---

## 三、用户角色与核心场景(V2)

### 3.1 目标用户（新增）

- **AI Agent工程师/研究者**：需要一个复杂、真实的环境来测试Runtime、Recovery、Memory等概念。
- **高级模组包开发者**：利用Replay和Timeline功能深度调试模组兼容性问题。
- **开源贡献者**：参与Runtime、Workflow、Diagnosis Pipeline等核心基础设施的建设。

### 3.2 核心场景（升级）

| 场景              | 用户       | 用户故事                                                     | V2价值体现                          |
| :---------------- | :--------- | :----------------------------------------------------------- | :---------------------------------- |
| **调试失败构建**  | 高级开发者 | “我的整合包构建到‘冲突检测’步骤失败了，我想看看Agent当时的具体输入、输出了什么，并从那里开始恢复执行。” | **Replay + Timeline**               |
| **优化Agent行为** | AI工程师   | “我想知道为什么Agent总推荐Forge而不是Fabric，我需要查看它的记忆和决策过程，并调整其记忆策略。” | **Memory Inspector + Trace Viewer** |
| **学习最佳实践**  | 研究者     | “我想回放一个成功构建‘科技空岛包’的完整Agent执行过程，来学习其工具调用和修复策略。” | **Full Replay**                     |
| **贡献冲突规则**  | 社区贡献者 | “我发现了一个新的模组冲突，系统应该能记录这个失败组合，并最终融入Failure Memory。” | **Failure Memory**                  |

---

## 四、功能需求详述 (V2.0)

### 4.1 核心模块1：Execution Timeline (可观测性)

**需求描述**：提供一个类LangSmith/Devin的界面，让用户“看到”Agent的每一步思考与执行，实现全过程可观测。

**功能点**：
- **实时事件流**：通过WebSocket推送`ExecutionEvent`，前端以时间线形式展示。
- **事件类型支持**：必须包括 `PLAN_GENERATED`, `TOOL_STARTED/COMPLETED/FAILED`, `RETRY_TRIGGERED`, `MEMORY_READ/WRITE`, `CRASH_DETECTED` 等。
- **详情下钻**：点击任意事件（如 `TOOL_FAILED`），能展示该工具调用的输入参数、输出结果、相关日志。
- **状态标识**：用颜色/图标清晰标识 `运行中`、`成功`、`失败`、`重试中` 等状态。

**技术提示**：
- 后端实现 `EventBus` 集中管理事件。
- 前端使用虚拟列表渲染海量Timeline事件。

### 4.2 核心模块2：Agent Memory System (持久化)

**需求描述**：构建分层记忆体系，使Agent具备长期上下文学习与自我进化能力，而非每次任务“失忆”。

**功能点**：
- **Session Memory**：存储单次任务执行过程中的上下文、模组组合、当前错误等，任务结束后可清理。
- **Persistent Memory**：长期存储用户偏好（如“偏好Fabric加载器”、“避免大型整合包”）。
- **Execution Memory**：存储历史成功/失败执行的摘要信息（如“Create + Flywheel + MC 1.20.1 成功”）。
- **Failure Memory**：存储已知的失败模组组合与崩溃模式，作为自我学习的基础。
- **Memory API**：提供 `memory.remember()`, `recall()`, `search()`, `record_failure()` 等编程接口。
- **UI管理界面**：允许高级用户查看、编辑或删除Persistent/Failure Memory条目。

**技术选型**：
- **SQLite**: 存储结构化记忆（Session, Persistent）。
- **ChromaDB**: 对Execution和Failure Memory进行语义检索。
- **In-memory dict**: 作为高频访问的缓存。

### 4.3 核心模块3：Replayable Execution (可回放)

**需求描述**：实现对任何历史Agent执行过程的完全或部分回放，用于调试、复现与分析。

**功能点**：
- **Execution Snapshot**：在执行流的每一个关键节点后，自动保存全状态快照（State, Input, Output, Memory）。
- **Replay Dashboard UI**：
  - 展示历史执行列表，支持搜索。
  - 进入详情后，显示完整Timeline，并提供 **`Replay`**、**`Pause`**、**`Step`**（单步执行）、**`Restart from Here`** 控件。
- **三种Replay模式**：
  1.  **Full Replay**: 从头重新执行整个任务。
  2.  **Partial Replay**: 从选中的Snapshot开始恢复执行。
  3.  **Deterministic Replay**: 在回放时，强制使用历史记录中的Tool Output，忽略真实调用结果，用于隔离外部变量，调试Agent逻辑。
- **存储方案**：使用SQLite存储执行元数据，用JSON Snapshot存储完整的快照数据（MVP阶段避免引入Event Sourcing的复杂性）。

### 4.4 核心模块4：Workflow Engine (编排)

**需求描述**：将线性的Agent逻辑升级为可定义的DAG工作流，实现复杂的编排、并行与容错。

**功能点**：
- **Workflow Definition**：支持以代码或声明式配置（如JSON/YAML）定义工作流节点及其依赖。
  - 示例工作流：`Requirement Analysis -> Mod Search -> (Parallel) Dependency Resolution & Conflict Detection -> ...`
- **Node Model**：每个节点包含 `id`, `type` (Tool/Decision), `status`, `dependencies`, `retry_policy`。
- **Engine Capabilities**：
  - **自动重试**：失败节点可按策略重试。
  - **超时控制**：节点执行超过设定时间则标记失败。
  - **部分恢复**：工作流中某分支失败，不影响其他分支。
  - **并行执行**：无依赖关系的节点自动并行。
- **状态持久化**：工作流执行状态必须持久化，支持进程崩溃后恢复。

### 4.5 核心模块5：Crash Diagnosis Pipeline (诊断)

**需求描述**：从原始的Minecraft崩溃日志，到输出一个明确的修复策略的结构化流程。

**处理流程**：
1.  **Parser**: 提取日志中的异常类型、堆栈、相关模组。
2.  **Classification**: 将崩溃分类（如 `Mixin Conflict`, `Missing Dependency`, `Java Version Error`, `OOM`）。
3.  **Suspicion Ranking**: 基于堆栈和分类，列出最可能导致崩溃的模组列表。
4.  **Knowledge Retrieval**: 查询本地 `Failure Memory` 或社区知识库，匹配已知解决方案。
5.  **LLM Reasoning**: 将以上信息作为上下文，交由LLM生成最终可执行的 `RepairStrategy`。
6.  **Output**: 输出一个结构化的修复建议（如“将模组A从v1.2降级到v1.1”）。

---

## 五、非功能需求

| 类别         | 需求描述                                                     | 目标/约束 |
| :----------- | :----------------------------------------------------------- | :-------- |
| **性能**     | 执行Timeline事件从发生到前端展示延迟                         | < 500ms   |
| **性能**     | 单个Execution Snapshot保存与恢复时间                         | < 2s      |
| **可观测性** | Runtime自身必须暴露健康检查、关键Metrics（队列长度、活跃工作流数）接口 | 必须      |
| **可靠性**   | 核心Agent Runtime进程崩溃后，应能自动重启并恢复未完成的工作流 | 必须      |
| **可扩展性** | 工具层（Tool Execution Layer）定义清晰接口，新增工具无需修改Runtime核心代码 | 必须      |
| **资源占用** | 空闲状态下，ModWeaver后台进程内存占用                        | < 150MB   |

---

## 六、技术架构（摘要）

### 6.1 架构图（同用户提供）
*（保持用户原图风格）*

### 6.2 技术栈

| 层级              | 技术选型                       | 理由                                        |
| :---------------- | :----------------------------- | :------------------------------------------ |
| **桌面壳**        | Electron + React + TypeScript  | 跨平台，丰富前端生态                        |
| **后端核心**      | FastAPI (Python)               | 高性能异步，生态成熟                        |
| **Agent Runtime** | **自研** (不依赖LangChain)     | 完全控制State、Recovery、Replay逻辑         |
| **Workflow引擎**  | **自研DAG Engine**             | 轻量，满足定制化Recovery需求                |
| **记忆系统**      | SQLite + ChromaDB              | 结构化数据+语义检索，轻量嵌入式             |
| **事件总线**      | `asyncio` Event Bus            | 满足单体应用内事件驱动需求                  |
| **状态与快照**    | Pydantic + JSON                | 强类型校验，易于序列化存储                  |
| **实时通信**      | WebSocket                      | Timelines事件与Replay控制                   |
| **工具层**        | LangChain (仅作为Tool Adapter) | 复用社区丰富的工具集成，Runtime之上轻量封装 |

---

## 七、风险与应对

| 风险                                  | 概率 | 影响 | 应对策略                                                     |
| :------------------------------------ | :--- | :--- | :----------------------------------------------------------- |
| **自研Runtime复杂度超预期**           | 高   | 高   | 严格遵循“迭代”原则，第一优先级实现 `Serializable State + Manual Replay`，再逐步增加自动Recovery。 |
| **Replay机制在复杂工具调用下失效**    | 中   | 高   | 确保所有Tool调用是纯函数或可Mock的。Deterministic Replay模式下，强制从Snapshot注入输出。 |
| **Failure Memory知识库初期为空**      | 高   | 中   | V2.0此功能作为辅助，主要依赖LLM推理。同时提供便捷的社区贡献机制，积累数据。 |
| **Electron + Python通信成为性能瓶颈** | 低   | 中   | 大量高频数据（如实时日志）通过WebSocket直连Python后端，避免经过Electron主进程中转。 |

---

## 八、开发生命周期与路线图

### Phase 1: Runtime & Observable 骨架 (2027.Q2, 8周)
- 搭建Electron + FastAPI基础通信。
- **实现 `AgentRuntime` 核心调度器**。
- 实现 `EventBus` 与 `ExecutionTimeline` UI 框架。
- 实现基础的 `Session Memory`。
- **目标**：跑通一个“需求->工具调用->事件展示”的最简闭环。

### Phase 2: Durable & Replayable (2027.Q3, 8周)
- 实现 `Workflow Engine` (DAG) 基础版本。
- 实现 `State Manager` 与 `Execution Snapshot`。
- 实现 `Replay Engine` 与 `Replay Dashboard` UI。
- 实现 `Persistent` 和 `Failure` Memory。
- **目标**：可以对一次执行进行完整记录、存储和全量回放。

### Phase 3: Intelligence & Recovery (2027.Q4, 8周)
- 集成 `Crash Diagnosis Pipeline`。
- 实现 `Partial` 和 `Deterministic Replay`。
- 实现基础的自动恢复机制（失败节点自动重试）。
- 实现`Memory Inspector` UI。
- **目标**：完成V2.0所有核心功能，形成“执行-崩溃-诊断-修复-回放”的闭环。

### Phase 4: 打磨与开源发布 (2028.Q1, 6周)
- 性能优化、全面测试、文档完善。
- 代码开源，发布社区贡献指南。
- 准备示例Demo（如“回放一个成功构建科技包的Agent过程”）。

---

## 九、成功指标 (KPIs)

| 指标类别       | 指标名称                                                     | 目标值 |
| :------------- | :----------------------------------------------------------- | :----- |
| **可观测性**   | 用户在Timeline上定位到失败步骤的平均时间                     | < 10秒 |
| **可恢复性**   | 由Runtime自动处理（重试/恢复）的瞬时故障比例                 | > 60%  |
| **可回放性**   | 一次Full Replay的成功率（能无差错回放到原始结束状态）        | > 95%  |
| **诊断准确性** | Diagnosis Pipeline输出的主要崩溃原因与修复建议的匹配度（人工评估） | > 70%  |
| **社区**       | GitHub上获得Star数（发布后3个月内）                          | > 500  |

---

**文档结束**

*本文档由ModWeaver产品团队制定，作为V2.0版本开发与评审的依据。*