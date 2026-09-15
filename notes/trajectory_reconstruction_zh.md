# 从目标轨迹到可训练环境：主图与方法定位

> 历史设计记录（9/9）。下文“预置World”的边界适用于旧协议。9/14 主实验已核实空业务环境库初始化，且采用完整Environment；当前表述见 [story_zh.md](story_zh.md) 和 [evidence_audit.md](evidence_audit.md)。

## 本次收敛的区别

用户强调的主线是：Evolver 从目标 agent 的交互轨迹识别能力需求，推断相应的状态、工具语义和交互依赖，构造独立的可执行训练环境，再通过学生训练与目标评测继续修订。原图的“已有 program bank → RL → feedback”省略了这个最重要的构造过程。

建议的表述是 **trajectory-grounded environment reconstruction for data-centric RSI**。这里 reconstruction 指对训练所需行为作可修订的建模，不是从有限观察唯一恢复真实后台，也不是重放原轨迹。World–Scene–Task 组织的是共享状态/工具、交互机制和新状态/目标实例；constructor/verifier 共同绑定合成任务数据，不声称从轨迹恢复了官方 verifier。

## 当前图如何表达

- **左侧轨迹时间线：** 目标代码不可见，用轻量锁标记说明；工具交互、后续请求与失败类型是输入，而不是可导入的目标环境代码。
- **固定 Evolver：** 从证据推断状态与交互需求，并设计合成任务语义。推断是 coding agent 的程序设计过程，不是额外实现了一套结构学习模型或语义编译器。
- **中央分层构图：** 从下往上，World 底座支撑多个 Scene 程序，各自产生多个新 Task。构造与验收配对写在 Scene 中；工作量与采样配比的说明移至 caption，避免再堆解释卡片。
- **右侧学生及弧形回路：** 准入后收集新在线交互并做 RL，更新的学生进入固定目标评测，新证据返回构造过程。Evolver backbone 不被学生 RL 更新；回环不表示每轮必然提升。

## 必须保留的初始化边界

当前 `../OpenAgentScaler/envopt/control/workspace.py` 的 `new` 会从 `seed/worlds` 复制对应业务 World。`report/2026-09-06-goal/seed_world_and_scene_fewshot_plan.md` 也明确该阶段省去从零构造第一版 World。

因此，图中 World 直接标记 **curated foundation**，caption 披露 pre-supplied World。这和“Evolver 不可读取目标 backend/verifier implementation”是两个不同事实。前者是实验初始化，后者是信息边界。没有通过改图声称当前所有 run 已经采用空业务环境初始化，也没有修改源代码实现这种设置。若最终论文采用完整从零构造协议，需要纳入 World 构造阶段、输入来源和成本，并重新对应实验。

目标实现不可见的依据是 coding sandbox 只挂载 run 本身，不挂载 `lab/` 评测实现、其他 runs 或宿主工作区；允许的信息由 dev feedback 提供。这个运行时边界不证明所有预制资产的历史来源，因此仍需保留 seed 来源审计。

## 示例依据

图是综合机制示意，不是伪装成单条归档轨迹：

- `report/2026-09-06-goal/seed_world_evidence_and_limits.md` 记录 BFCL 可见交互中的 cwd、读写和上下文连续性，以及对应 SQLite 文件/会话基础。
- `envopt/runs/20260908-031723-53c19e-stable_bfcl/env/bank/file_session/path_batch.py` 有递归文件选择、cwd 处理和原文件保留。图中 Path context 是简化的机制标签，`a.txt/b.txt` 是示意实例标记，不是该程序实际采样文件名的记录。
- 同 run 的 `deferred_file.py` 实现先读后请求、same-file 指代、输出写权限和真实文件验收。示意 `[18,24,30]` 的均值为 24，另一实例 mean=31 表示新任务目标；不是测量结果。
- `report/2026-09-08-goal/evolution_data_and_transfer_analysis.md` 提到 BFCL `multi_turn_base_34` 中算对但只声称修正、未真正改文件的行为，以及针对它构造数据。图的 **Claimed write, no effect** 表达这个已记录的失败类型，没有虚构某条完整轨迹的具体文本或性能改善。

## 近邻对照的边界

主线暂聚焦 EnvHarness、RSIBench-Data、SPADE，按用户要求不扩展 Simia 讨论。

- **EnvHarness：** 在既有可执行目标环境及其原始 verifier 上作接口级变换；不能声称只有 EnvOpt 能改变交互机制。
- **RSIBench-Data：** §3.3 和附录 A 提供 task-matched seed repositories / examples，研究者的内部构造策略不限于一种方法；不能把所有 seed repo 等同于官方评测环境代码。
- **SPADE：** §5.3 明确有工具修改的后台状态、逐条用户请求和状态检查，不能按“没有数据库/状态”区分。其 tool-use 环境从代码语料出发，未展示 benchmark task/data 给 designer；EnvOpt 的区别是目标行为证据驱动的构造与修订。不同信息预算需要公平对照。

本次没有将这些差异直接升级为已证明的 novelty 或效果结论。后续需要测试轨迹依据、结构化构造和迭代修订分别带来的收益，而不只证明 pipeline 可以执行。
