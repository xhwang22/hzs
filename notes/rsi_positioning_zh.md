# 当前 RSI 定位与近邻对照

## 主定位

EnvOpt 研究 data-centric RSI 中的环境研究能力：固定研究者依据目标模型的行为，维护并演化独立的可执行训练环境，学生持续在线 RL，新的反馈改变下一轮研究决策。当前重点不是旧 World–Scene 层级，而是 evidence-linked diagnosis、persistent planning/experience 和 versioned environment library。

当前三组业务环境库为空起步；允许通用接口、examples 和目标 dev 证据。这不等于无任何先验、benchmark-free 或完整恢复真实后台。生成器模型参数不训练，学生不接任研究者。

## 三个主要近邻

| 工作 | 可用材料/优化对象 | 应当承认 | EnvOpt 的具体取向 |
| --- | --- | --- | --- |
| RSIBench-Data | task-matched seed repo/examples、共享训练服务；研究者可自行设计数据策略 | 已经定义固定研究者改进另一目标模型的数据研究setting，观察到后续退化 | 给出可执行环境的具体研究方法；空业务bank、完整程序、继续在线RL、任务关联统计与版本反馈 |
| EnvHarness | 已有可执行环境及原始verifier；Stage/Contract/Chain变换 | 能改初始状态、动作、观察和转移，且有policy反馈 | 不直接复用目标实现；从行为证据构造独立训练程序和验收，需要承担模型化与验证风险 |
| SPADE | 语料grounding、完整有状态环境、环境记忆、共享designer/solver RL | 有backend state、multi-turn tool use、reset实例变化、verifier、记忆与可学习性反馈 | 固定外部Planner、目标dev定向诊断、可回查原case、稳定需求组与版本化库/经验决策；本文三组未用外部语料 |

不把差异简单排成优劣。EnvOpt能看目标dev行为，而SPADE主setting不向designer展示benchmark任务；两者信息预算不同。RSIBench-Data的seed repo也不都等于官方eval backend。数据库、程序化任务、environment memory和循环各有先例，不能分别写成首创。

用户要求暂不展开Simia，主线对照集中在上述三篇；其他合成/数据研究工作仍在相关工作中公平引用。

## 当前贡献组织

1. **从解释到可核查研究输入：** 每轨迹机制分析、联合domain/content树合并、源引用回查；另用固定task IDs支持由程序计算的requirement-group结果，避免用LLM标签频次冒充性能。
2. **从一次性生成到可选择的资产演化：** 一个Environment包含sampler、interaction和verifier；同一ID可修订，retention/pause与明确题量支持长期库管理。
3. **从日志堆积到研究反馈：** 版本关联online rewards与固定dev分工；Planner维护经验，当前较新契约显式对照expected effect和下一轮观察，但不将相关性冒充因果。

这是可检验的方法主张，而非独创性证明。下一轮最关键的是固定库/只调参数与配比/完整修订的预算匹配，以及no-experience、stale-feedback对照。

## 图与结果的对应

主图突出：目标实现不可见、source-linked analysis、固定但持久的Planner、可修订经验、空起点库、create/revise/retain/pause及两类反馈。去掉旧World底座、Scene层级和student probe。完整Environment API用一句 sampler–interaction–verifier 表达，不再塞验证细节。

主实验用完整轨迹与dev选轮表支撑“能找到有用检查点，但保持不稳定”。BFCL明显改善、τ²后期退化、ACE native小样本且在R7 Test峰值之后回落，不能讲成所有任务均持续增长。ACE已停止并补齐十轮Test；方法版本、实际题量、checkpoint选择与测量不确定性须与故事一起呈现。
