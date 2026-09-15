# EnvOpt：重新建立 contribution 的论证

> 历史分析（9/9）。9/14 新协议与最新贡献定位见 [story_zh.md](story_zh.md)、[rsi_positioning_zh.md](rsi_positioning_zh.md)；本页保留研究思路，不作为当前 World/Scene、seed 或 probe 协议说明。

> 后续与用户明确的上游定位是“从目标轨迹推断并构造训练环境”，而不只是在既有 bank 上调难度。新主图与 from-scratch 初始化边界见 [trajectory_reconstruction_zh.md](trajectory_reconstruction_zh.md)。下文保留对具体设计和 novelty 边界的分析。

本页重新审视研究主张，不继续用图的布局或模块名称代替 novelty。依据包括维护代码、实际 run 的 Scene 程序、9 月 8 日的 evolution/transfer 分析和 9 月 9 日的 admission 案例报告，以及最接近论文的方法原文。历史实验只作为动机与设计证据；本次没有运行实验或修改 OpenAgentScaler。

## 1. 之前的稿子缺少什么

此前已经描述了“固定 Evolver、World–Scene–Task、probe、RL、dev feedback”，但没有充分建立从问题到设计选择、再到可检验收益的因果链。这些内容大多属于 setting、表示接口或运行保障。把它们排成三个贡献点，不能回答 reviewer 最重要的问题：已有相关方法为什么不够，选这个设计究竟多解决了什么？

RSI 是正确的问题定位，但不是 EnvOpt 独有的新意。World–Scene–Task 是有用的组织方式，但三层名字本身也不是研究结论。自适应难度、程序化环境、partial rewards、state-first checks、代码代理和自动训练各有清楚的先例。

## 2. 对近邻工作的纠偏

| 近邻 | 原文已有的内容 | EnvOpt 能讨论的具体差异 |
| --- | --- | --- |
| RSIBench-Data §3 | 固定外围服务的跨模型数据研究；可修改 data strategy、环境/任务、验证和 curriculum；不是规定一种内部方法 | 它定义评价问题；我们提出一种具体的可执行机制表示和迭代方法。持续 RL 与其从固定基座 SFT 不同，但这项差异单独不足以构成算法 novelty。 |
| EnvHarness §§2–3 | 可组合的 Stage/Contract/Chain；可以改初始状态、actions、observations 和 transition mechanics；根据 policy 轨迹写组件、fresh validate；也有 RL | 我们不止包装固定 base task/original verifier，还在 Scene 中维护新任务构造器与 verifier，持久管理 bank 和实例分布。代价是需要承担生成 verifier 的可靠性风险。不能声称“只有我们能改交互机制”。 |
| SPADE §§3.1、4 | 用程序生成完整环境，reset(seed) 已能改变目标和初始状态；designer/solver 共享模型，designer 用 hint-regret 等信号训练 | 差异是稳定 World 与可编辑 Scene 的结构化搜索、独立 coding Evolver、目标 dev grounding 和 bank 生命周期，不是表达能力更广或首次复用环境程序。 |
| EnvScaler §4 | 先生成初始状态再造任务；每个任务生成验证 checklist/functions；已有分项 reward | 有针对性的差异是 Scene-level constructor/verifier 配对复用和后续反馈驱动的程序修订。先状态后任务和分项评分不应列作独立发明。 |
| RODS §3 | 按能力边界选 seeds、保留技能类别配额、按 API 依赖结构重合成、动态 replay；实践使用 mean-progress reward proxy | 我们直接编辑产生交互的程序及目标分布，不仅沿固定 synthesis pipeline 生成结构相近的 variants；但“保持结构”“覆盖”和“variance 有用”也已有明确先例。 |
| FACET §2 | 从共同的实际执行环境派生任务工件、保持来源意图、针对性修复 | 共享状态 grounding 不是独有。应论证我们的可复用 Scene 单元在持续修订中带来的具体收益。 |

以上只支持可辩护的差异，不构成对全部文献的独创性证明。尤其“程序就是分布”“一次环境生成多个实例”不能作为排除 SPADE 等工作的论据。

## 3. 我建议的中心主张

**EnvOpt 研究如何把目标 agent 的能力失败，转化为可复用、可修订的可执行训练机制，再由这些机制持续产生当前学生可学习的经验。**

对应的英文 thesis 可写为：

> EnvOpt performs data-centric research for agent self-improvement by evolving reusable environment programs that turn diagnosed capability gaps into fresh on-policy training distributions.

其中真正需要实验检验的是：以这种机制程序为修改单元，是否比固定 generator、只调参数/配比，以及缺少这种结构的完整环境重写，更能找到有迁移价值的经验。不能仅以“pipeline 跑通”或“生成 reward 上升”回答这个问题。

核心关注是**目标决策结构**。例如，必须发现 API 并组织请求、在上下文变化后解析同一个资源、先获得一个私有偏好再决定动作、完成真实用户侧操作后才能继续。这些关系需要由实际状态、能力、信息和时序实现。把文本变长或增加重复操作，不自动增加这样的决策。

## 4. 技术选择一：以机制程序为可复用搜索单元

把优化对象写成 `q_phi(x) = sum_s alpha_s q(x | W, S_s, eta_s)`。这里的关键在于各变量具有不同作用：

- **W：** 通常复用业务状态、工具与公开规则，必要时扩展或修复底座。
- **S：** 改变某类任务的交互机制、构造目标的程序和成功判据。
- **eta：** 改变机制内的工作量，例如实体数、依赖长度、干扰项或信息负担。
- **alpha：** 改变不同机制的训练预算与覆盖。

这不是一个新概率公式，而是对代码搜索空间的有意义分解。World 为多个机制提供共同语义；Scene 让缺陷修复和任务机制扩展可以作用于后续许多实例；Task 负责具体实例化。我们应证明这种分解提高修订的复用性、局部性或预算效率，而不只展示 Python 有三个类。

当前代码确实支持有实质的机制变化。例如实际 `social_handoff.py` 将 publish_post 交给 user，只有真实发布后才得到 post ID，之后才恢复 agent 的 repost/comment；`deferred_file.py` 则将“先读文件”和“后续要求计算并写回同一文件”分成真实互动阶段，并检查实际输出。这比中性示例里“把 3 改成 8”更能说明系统的表达和修改对象。

但它们是否有训练价值仍需分开判断。9/8 报告记录 social_handoff 在两轮中均 64/64 成功、0 mixed，且完整组合 dev case 仍失败。**有实质代码变化不等于有有效贡献；这正是对照实验要回答的部分。**

## 5. 技术选择二：新目标的生成与验收在同一机制中绑定

Scene 配对维护 `make_task` 与 `check`，Task 保存具体 goal data，request、合法 user facts 与 verifier 从这些数据派生。它解决的是“持续生成新目标时，目标含义如何跨多个工件保持一致”的问题。

例如，一个 Scene 生成涉及具体航班、人数、金额和授权条件的新任务。变换人数或目标，就必须同步改变用户应确认的条件、实际环境效果和验收依据。系统需要同时接受合法替代路线，并拒绝与请求不符的实际结果。这里的贡献候选是**可复用的构造—验收单元与它的演化接口**，而不是“有一个 reward function”。

结构上的事实是：每个新 Task 不再独立生成一份 Python checker，验收代码在 Scene 中重用。不能从这个事实直接推断成本必然更低、错误率必然更小，因为每个实例仍要检查，而且 constructor/verifier 可能同源犯错。分别测量程序生成数量、实例验证成本、错误接受和错误拒绝，才可能得到实证贡献。

## 6. 技术选择三：扩展机制与校准机制是两种研究动作

当目标能力未被环境表达，应扩展状态/工具/交互结构；当机制存在但学生过难或饱和，应调其 workload 和预算。这两个动作作用于任务分布的不同层面。把它们混为“继续加难度”，容易在少数好造的任务里局部循环。

当前实现以覆盖 bank、固定 dev 与 RL history 指导这种选择，并以固定学生的短 probe 辅助校准。程序修改与学生权重更新分阶段发生，帮助区分数据改变和学生改变。

但目前的策略仍主要依赖 coding agent 的判断和 GUIDE；coverage 自动检查主要是类别与引用，admission 只要求 portfolio 存在实测同题 variation。它不是已经证明高效、稳定的结构搜索算法，也不是一个新的 regret/bandit/meta-gradient 方法。9/9 报告中的反复 uncertain/refine 阻挡进一步说明，不能把验证流程本身宣传成已经解决研究效率的问题。

## 7. 最有价值的科学问题：可训练性与目标决策是否一致

已有报告提供了直接动机，且应按历史快照准确引用：

1. **Automation，9/8 的 7 轮快照。** 训练成功率从 14.8% 到 51.4%，但 benchmark rubric 没有持续提升；训练接口大量使用 resource-specific helpers，避开目标 benchmark 的 api_search/api_fetch 操作链。这个差距不是增加数据量就能自动消失。
2. **BFCL，同一快照的 6 轮。** 单项社交交接任务全对，目标 dev case 还要求车辆、换算、工具恢复和社交动作的组合，仍未成功。机制数量与组合覆盖是两回事。
3. **τ²，同一快照的 4 轮。** mixed groups 增多，dev 没同步提高；环境修复、reward 修正和难度下降都在影响 synthetic 指标。

这些观察不是已经完成的因果消融，但共同指向一个可检验命题：**自动 environment evolution 应以保持并补足目标决策结构为约束来校准可训练性。** 当前项目具备表达这些机制和做修订的基础，对这一约束的系统实施与有效性证明还不充分。

## 8. 如果要增加一个更硬的技术设计，我优先补什么

建议把“保持关键决策地调 workload”从 GUIDE 中的要求，推进成修改时明确记录、能用局部反例检查的性质。尽量复用 Scene 现有接口，不先建设大型 DSL。

例如对 private-choice 机制构造一对诊断 Task：初始 agent 可见内容相同，用户的私有偏好不同，正确目标动作也不同。若某个简化把偏好写进唯一公开候选或排序，成对检查就暴露这个捷径。目标不是强制每条成功轨迹必须调用同一个工具，而是保留“可靠完成任务需要获得额外信息”的结构。一次偶然猜对仍可合法成功；任务族层面的信息需求与单条轨迹判分应分开。

对 API 工作流，减少需处理的对象，但保留目标接口的发现/请求构造条件；对文件会话，降低目录深度，但保留 cwd 改变后的相对引用；对 staged write，减少更新对象，但保留暂存与实际提交的区别。诊断集可复用作检查，不当成新的训练样本。

这可以形成更强的“受目标决策约束的机制演化”方法。它目前是明确的补强建议，不能当作已经实现的贡献，也需要与 RODS 的结构保持、EnvHarness 的交互约束及其他反事实环境设计工作进一步做 novelty 对照。

## 9. 可以怎样组织 contributions

不要将三个熟悉的模块分别包装成三个发明。建议围绕一个主方法安排两个设计支点与一个经验性问题：

1. **方法：** 针对 data-centric RSI 的可执行任务机制程序优化，将失败分析连接到程序修订和新在线经验。
2. **关键设计：** 分解 World/Scene/实例与 workload/mixture 的职责，并配对复用任务构造器和 verifier，使机制级修订有清楚的语义对象。
3. **实证贡献，待完成：** 测试机制程序修订的收益、任务语义一致性和多轮改进可靠性；分析为什么提高合成可训练性可能无法产生迁移。

若补强并验证 §8，再把“保持目标决策的校准”提升为算法设计的一部分。若不补强，也必须用扎实对照证明已有结构与搜索方法有收益；否则当前稿子更像一个合理系统的设计说明，尚没有足够强的研究贡献论证。

## 10. 决定故事是否成立的最小实验

| 问题 | 关键对照 | 看什么 |
| --- | --- | --- |
| 编辑机制是否有用 | 同 bank、同训练预算：fresh resampling / 只改参数与配比 / 完整程序修订 | 真实 test 迁移、每类能力、全部 coding/probe 成本 |
| 三层搜索单元是否值得 | 相同源能力与 agent/反馈预算：结构化 World–Scene 重用 vs 不带该分解的完整环境程序生成/重写 | 修订成本、复用、缺陷与迁移；不能把 baseline 故意限制成弱模板 |
| 配对复用 verifier 是否有用 | 同 goal/state grounding：Scene-owned verifier vs 每 Task 生成 checker | 独立审计的误接受/误拒绝、合法替代路径、成本 |
| 后续反馈是否驱动改进 | 更新反馈 vs 固定/陈旧反馈；同总量的一次性造数与多轮造数 | 首次/末次/最佳/选定 checkpoint、多个 evolution seed |
| 决策保持是否必要 | 合理调整工作量 vs 会绕过目标机制的简化，独立计算被保留的机制 | 相似训练难度下的迁移差异；示例必须承认是受控设计实验 |

当前不应把所有实验全铺开。最先完成第一行，以及一个真实机制 revision 的前后案例；再据结果决定哪一个设计消融最能解释收益。图也应在这条因果链确定后重画，不能继续用中性 commit 示例替代主要科学论证。

## 证据入口

- 维护接口：`../OpenAgentScaler/envopt/generation/scene.py`、`core.py`、`propose.py`、`control/coverage.py`、`control/calibration.py`、`evolution/GUIDE.md`。
- 实际机制程序：`../OpenAgentScaler/envopt/runs/20260908-031723-53c19e-stable_bfcl/env/bank/business_ops/social_handoff.py`；同 run 的 `env/bank/file_session/deferred_file.py`。
- 历史迁移分析：`../OpenAgentScaler/report/2026-09-08-goal/evolution_data_and_transfer_analysis.md`。
- 准入问题：`../OpenAgentScaler/report/2026-09-09-goal/admission_block_case_review.md`。
- 论文原文：`sources/paper_text/EnvHarness_2608.19880.txt`、`SPADE_2608.19197.txt`、`EnvScaler_2601.05808.txt`、`RODS_2606.19047.txt`、`RSIBenchData_2607.25886.txt`、`FACET_2608.18580.txt`。
