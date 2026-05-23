## Agent 动态协商与投票机制设计讨论（V3.0 方向）

### 一、为什么要引入协商与投票？

V2.5 中 Agent 之间的协作模式是 **“固定职责 + 顺序/事件驱动”**：
- Planner 生成计划 → Executor 执行 → Diagnoser 诊断 → Repair 修复
- 这是一种 **单向流水线**，没有并行决策，也没有冲突解决。

当任务变得复杂、不确定性强时，单一 Agent 的判断可能不足。例如：
- **Planner** 生成两套候选方案（Forge 路线 vs Fabric 路线），需要其他 Agent 投票决定。
- **Diagnoser** 给出多个可能的崩溃根因（模组 A 冲突 / Java 版本错误 / 内存不足），需要 **Executor** 和 **Repair** 共同投票排序。
- **Memory Agent** 检索到多条冲突记录，置信度不同，需要综合评估。

**协商与投票** 的本质是：**多个 Agent 对同一个决策问题给出意见，系统通过某种算法（投票、加权、博弈）达成共识**，提高决策鲁棒性。

---

### 二、核心概念定义

| 概念                     | 定义                                                         |
| :----------------------- | :----------------------------------------------------------- |
| **提案 (Proposal)**      | 一个 Agent 提出的待决策事项，包含选项、证据、置信度。        |
| **投票 (Vote)**          | 另一个 Agent 对某个选项的支持/反对/弃权，可附带权重和理由。  |
| **协商 (Negotiation)**   | 多轮交互，Agent 之间可以修改提案、让步、交换条件，直到达成共识或超时。 |
| **共识机制 (Consensus)** | 决定最终结果的规则，如多数投票、加权投票、BFT、最长链等。    |
| **仲裁者 (Arbiter)**     | 可选角色，当投票僵持时由仲裁者（或人类）决断。               |

---

### 三、典型应用场景

#### 场景1：多方案选择
- **触发**：Planner Agent 产出 2 个或以上的 Workflow 计划（例如：方案A 使用 Fabric + Sodium，方案B 使用 Forge + OptiFine）。
- **协商流程**：
  1. Planner 将两个提案广播给 Executor、Diagnoser、Memory Agent。
  2. 每个 Agent 根据自身知识投票（Executor 考虑执行稳定性，Diagnoser 考虑历史崩溃率，Memory 检索类似案例）。
  3. 系统按投票规则选择方案，或要求 Planner 合并两个方案。

#### 场景2：冲突根因排序
- **触发**：Diagnoser 输出 3 个可能的崩溃原因，置信度分别为 0.7, 0.5, 0.2。
- **投票流程**：
  1. Repair Agent 对每个原因的可修复性打分（能否自动修复、修复成本）。
  2. Executor Agent 对每个原因的回滚风险打分。
  3. 综合投票得分决定优先尝试哪个修复。

#### 场景3：内存/资源分配仲裁
- **触发**：多个 Workflow 并行执行，争抢有限的文件句柄、网络连接或计算资源。
- **协商**：Resource Governance Agent 发起资源配额投票，各 Workflow 的 Executor Agent 根据自身优先级竞标。

---

### 四、架构设计

#### 4.1 角色扩展

在 V2.5 的 Agent 基础上，新增或增强以下角色：

| Agent                          | 新增职责                                                     |
| :----------------------------- | :----------------------------------------------------------- |
| **Facilitator Agent** (协调者) | 管理协商会话，维护提案池，收集投票，判断共识达成。           |
| **Voter Interface**            | 每个 Agent 实现 `can_vote_on(proposal_type)` 和 `cast_vote(proposal)` 接口。 |
| **Arbiter Agent** (可选)       | 当协商超时或投票平局时，做出最终决定。可配置为规则引擎或调用人类确认。 |

#### 4.2 消息协议

使用现有的 `AgentBus`，定义协商相关事件类型：

```python
class NegotiationEvent(ExecutionEvent):
    event_type: Literal[
        "NEGOTIATION_START",
        "PROPOSAL_ANNOUNCED",
        "VOTE_CAST",
        "VOTE_UPDATE",
        "CONSENSUS_REACHED",
        "NEGOTIATION_TIMEOUT",
        "ARBITER_DECIDED"
    ]
    negotiation_id: str
    proposal: dict
    votes: list[dict]
    consensus_result: Optional[Any]
```

#### 4.3 协商流程

```
Facilitator 收到决策请求
       ↓
创建 Negotiation Session (ID, 提案, 投票规则, 超时)
       ↓
广播 PROPOSAL_ANNOUNCED 给相关 Agent
       ↓
Agent 异步返回 VOTE_CAST (可附带理由、权重)
       ↓
Facilitator 实时统计，满足规则则 CONSUMMATE
       ↓
若超时未达成 → 触发 ARBITER_DECIDED
       ↓
广播 CONSENSUS_REACHED，携带最终结果
```

#### 4.4 投票规则设计

支持多种规则，可配置：

| 规则           | 描述                                                         | 适用场景                 |
| :------------- | :----------------------------------------------------------- | :----------------------- |
| **简单多数**   | > 50% 支持即通过                                             | 低风险决策               |
| **绝对多数**   | 需 > 2/3 支持                                                | 高风险决策（如删除模组） |
| **加权投票**   | 每个 Agent 有预设权重（如 Executor 权重 0.4，Diagnoser 0.3） | 依赖专业权威             |
| **Borda 计数** | 对多个选项排序，按位次得分                                   | 多方案选择               |
| **一致同意**   | 必须全票通过，否则失败                                       | 安全性要求极高           |
| **最长链共识** | 借鉴区块链，记录投票链，防止篡改                             | 需要审计不可否认         |

#### 4.5 协商轮次

对于复杂问题，支持多轮协商：
- **Round 1**：各 Agent 匿名提交投票。
- **如果未达成**：Facilitator 公开当前票数分布，允许 Agent 修改投票（可附带理由）。
- **Round 2**：重新投票。
- **最多 N 轮**（默认 3 轮），仍未达成则进入仲裁。

---

### 五、技术实现要点

#### 5.1 数据模型

```python
class Vote:
    agent_id: str
    proposal_id: str
    choice: str | int   # 选项标识
    confidence: float   # 0-1，该 Agent 对自己判断的信心
    reason: str         # 可选，用于调试和回放
    timestamp: datetime

class NegotiationSession:
    id: str
    proposal: dict
    options: list[str]
    rule: VotingRule   # 枚举
    timeout_seconds: int
    votes: list[Vote]
    status: str        # OPEN, CONSENSUS, TIMEOUT, ARBITER
    result: Optional[str]
```

#### 5.2 一致性保证

- **幂等投票**：同一 Agent 对同一提案多次投票，以最后一次为准。
- **投票截止**：超时后不再接受新投票。
- **会话隔离**：不同 Negotiation Session 完全独立。

#### 5.3 与 Timeline 集成

所有协商事件（投票开始、每个投票、共识达成）都作为 `ExecutionEvent` 写入 Timeline，便于回放和调试。可以在 UI 中展示：
- 一个“协商卡片”，显示提案、选项、各 Agent 的投票柱状图。
- 点击可展开每个 Agent 投票的理由（如果提供了）。

#### 5.4 与 Memory 系统结合

- **记录历史投票**：将每次协商的结果存入 Execution Memory，作为未来 Agent 投票的参考。
- **学习投票行为**：Reflective Memory 可以分析某些 Agent 的投票准确性（例如，某 Agent 总是投错方案，可以降低其权重）。

---

### 六、边缘情况与容错

| 问题                                  | 解决方案                                                     |
| :------------------------------------ | :----------------------------------------------------------- |
| **部分 Agent 不响应投票**             | 超时后未投票视为弃权；弃权票不计入分母。                     |
| **投票平局**                          | 启用 Arbiter Agent 裁决，或回退到默认策略（如选第一个选项）。 |
| **提案本身有歧义**                    | Facilitator 允许 Agent 在投票时附带“修改提案”请求，触发新的一轮提案完善。 |
| **恶意 Agent**（人为错误或 LLM 异常） | 可配置最低置信度阈值，置信度过低的投票将被标记但不计入；未来可引入声誉系统。 |
| **协商风暴**（短时间内大量协商）      | Resource Governance 限制并发协商数量（如最多 5 个），多余的排队。 |

---

### 七、与现有模块的关系

- **取代部分硬编码逻辑**：原本由单一 Agent（如 Planner）独自决定的内容，改为协商。
- **与 Evaluation Engine 结合**：可以评估不同投票规则的效果（例如，“加权投票比简单多数的成功率高出 10%”）。
- **与 Resource Governance 结合**：协商本身也会消耗时间和 token，需要配置协商超时和最大轮数，防止递归协商。

---

### 八、实现路线图（V3.0 建议）

| 阶段          | 内容                                                         | 工时估计 |
| :------------ | :----------------------------------------------------------- | :------- |
| **Phase 3.1** | 实现 `Facilitator Agent` 和基础投票模型（简单多数），集成到 AgentBus。 | 2 周     |
| **Phase 3.2** | 在 1~2 个真实场景中替换为协商（如方案选择、根因排序）。      | 2 周     |
| **Phase 3.3** | 增加加权投票、多轮协商、Arbiter Agent。                      | 2 周     |
| **Phase 3.4** | Timeline 集成 + 可视化 UI（投票卡片）。                      | 1 周     |
| **Phase 3.5** | 与 Evaluation Engine 结合，自动调优投票规则。                | 1 周     |

---

### 九、最终思考

**动态协商与投票机制** 是多 Agent 系统从“固定流水线”迈向 **真正的协作智能** 的关键一步。它不仅仅是“让 Agent 聊天”，而是通过结构化的投票协议，平衡效率与可靠性。

在 Minecraft 模组整合这个领域，本身就充满了不确定性（版本兼容、冲突、社区质量不一），因此特别适合作为协商机制的试验场。V3.0 实现后，ModWeaver 将能够：
- 自动化解 “Forge vs Fabric” 这种困扰玩家多年的难题。
- 在多种修复方案中选出最稳妥的一条。
- 让整个系统表现出超越单个 LLM 的判断力。
