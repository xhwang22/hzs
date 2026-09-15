# 当前代码与实验依据审计

本轮只读研究材料来自 OpenAgentScaler-env-evolution 的 maintained code、9/10–9/14 报告及对应 run；OpenAgentScaler-env-feedback 用作合回历史，原 OpenAgentScaler 是旧版来源。所有写入留在 envopt-paper。未运行任何训练、benchmark evaluation、原生 grader、资源申请或生成环境代码。

## 实现与协议变化

| 主张 | 直接代码入口（相对 OpenAgentScaler-env-evolution/envopt） | 边界 |
| --- | --- | --- |
| 完整可复用 Environment | generation/environment.py | 不再强制 World JSON + Scene stack；JSON 状态不是表达能力首创 |
| 空业务 bank 初始化 | control/workspace.py 的 empty_bank；control/loop.py CLI 默认 | 仍提供通用框架与 examples；可选 seed-bank 功能不等于本次用了 seed |
| 完整轨迹分析与递归联合 merge | evolution/trajectory_analysis.py；prompts/trajectory_analysis.md、analysis_merge.md | 来源校验不证明语义完整；任务行为含成功策略和失败任务应有行为 |
| Task-linked requirement map、程序算分 | control/capabilities.py | task group 可重叠；不是原子技能正确率；definition 变更需版本化 |
| 持久 Planner 与只读来源查询 | control/planner.py、analysis_sources.py、inspect_context.py、planner_guide.md | Planner 输出计划和经验，不直接执行训练/评测或改 evaluator |
| create/revise/retain/pause 与精确题量 | control/environment_generation.py | 10 是每轮新/修订预算，不是整个 bank 上限；未分配/暂停不补题 |
| CPU 检查 + solvability screen + 至多一次代码修复 | control/environment_generation.py、construction.py、evolution/solvability_guide.md | 最多 first/middle/last 3 个代表实例做模型审查；不能说全量语义证明 |
| 不使用独立学生 probe | control/loop.py；evolution/planner_guide.md | 正式 RL 的 group stats 是后续反馈，不是入训 mixed gate |
| 正式版本关联训练反馈 | evolution/rl_evidence.py、control/planning_context.py、rl_feedback.py | 是训练期间的历史观测，不是最后 checkpoint 的固定策略 probe |
| expected_effect / review_previous | control/planning_feedback.py | 当前 native ACE 使用 decision_brief_v1；较早 τ²/BFCL 计划没有该字段契约 |
| 目标实现/隐藏答案/test 不挂入 Planner | control/planner.py 的挂载清单与只读query接口 | 不能由运行时边界反推所有历史人工输入已完整审计 |

## 空 bank 的直接核实

三个 run 的初始 Git tree 在 env/ 下均只有 seed_manifest.json，没有业务环境模块：

| Run | 初始 commit |
| --- | --- |
| 20260913-022502-83b860-tau2 | 5aad6021d154a5141e29a2990cd5889da8ccbe97 |
| 20260913-022504-defa84-bfcl | 622c97125d60ebdd382fb9c3369309f9dac6896d |
| 20260914-094616-22571a-acebench_agent | cc7ac9df9de95c7fef26e2c5bb6c52187635b4e3 |

这推翻了旧图对当前协议的 curated World 标记。旧稿/旧初始化本身不被改写，见 archive/pre_20260914/。

## 结果快照与数值核对

data/results_20260914.json 的采集时间为 2026-09-14 16:04:42 UTC，冻结每组首 9 个完整轮次，保存 197 个原始结果文件哈希。每份 eval 由 case_groups 的每题三次 passed/failed 重新计算各子类和整体指标，再与 outcome / status / metric_stats 交叉核对；test 还要求对应 checkpoint 与完整训练 job 相同。没有从截图手抄主表，也没有将当前仍变化的 run.json 当永久固定结果。

当前构建改用 data/results_20260915.json：17:43:25 UTC / 次日01:43:25北京时间补齐 ACE R5–R10 Test及R10 dev/训练，原快照保持不变。新增快照保存218条来源文件哈希、旧快照哈希和已变化来源的历史哈希。τ²/BFCL逐字段原样保留；ACE基线、协议、前4轮Test及前9轮其余数据也逐字段一致。新Test通过25题×3重算、固定task IDs及checkpoint/job/status对应校验；native ACE已停止，共10完整轮次。

- τ² dev/test 各 139 题，题目加权；BFCL 各 400 题，四个等大 multi-turn subset；ACE 各 25 题，两个 category 宏平均。
- 表格 dev 选轮规则包含 baseline，浮点 12 位下同分取最早。τ² R5、BFCL R9、ACE R3；不是 test 最高轮。
- ACE Test 最高变为 R7 的56.11%，高于dev选中R3的52.22%，但不据此改选R7；末轮R10为51.11%。
- BFCL 匹配 test base 25.42%；R9 42.08%，+16.67 pp，任务层配对区间约 [12.3, 21.2]。
- ACE native-FC base 41.11%；R3 52.22%，+11.11 pp，区间约 [-5.6, 28.9]。不声称统计显著或跨训练种子可靠。
- τ² R5 test 39.33%，R9 34.05%；31.89% test base 是修复前 replay，dashboard test_baselines.json 明标 comparable=false。按作者要求，图中历史base连至R1并显示描述性差值+7.43 pp，不放dagger及对应图注说明；原始记录不变，正文/附录保留研究边界，主表Δ和配对差值区间仍留空。

## 关键实验边界

1. **Native ACE 与旧 textual ACE 分开。** 当前 22571a 使用 9/14 的 native FC、full history、同官方业务工具与 state grader。旧 5aaa5e 以及其归档替代 job 不纳入新曲线。Test现已补齐R1–R10，全部为真实完成的评测，不补值、不外推。
2. **“repeat3”不是“三训练种子”。** 每组只有一个训练/evolution run，bootstrap 按同题三次记录一起重采样，只表示固定模型的测试集不确定性。
3. **不是统一冻结版本的完成对照。** τ²/BFCL 使用较早 v5 规划/反馈契约，native ACE 使用 decision_brief 和更完整的 RL group 查询；维护、恢复及参数/上下文修复需保留。没有固定库、参数-only、无记忆等结果。
4. **尾批、失败与题量不隐藏。** τ²/BFCL/ACE 总题量分别 846/809/626；episode 总数 6768/6472/5008。最后完整轮次分别为R9/R9/R10，题量88/76/52，不把每轮写成96。ACE取消的R11无完整checkpoint，不纳入曲线。
5. **异常不写成零缺陷。** 直接只读 tar 成员检查：BFCL R2 有32条 invalid user context abort，R1有1条 empty user turn；τ² R3有1条 user tool budget exhaustion、R8有1条 empty user turn。ACE十轮记录0 episode abort；R6/R8 Test首次在推理前toolchain检测失败，随后补测成功，失败progress与恢复结果均保留。完整token/reward-group审计和权重更新不消除这些缺陷的影响。
6. **Operator-only test。** 不向Planner提供test，但操作者反复看过checkpoint tests，论文因此不声称是方法冻结后的一次性 pristine holdout。最终确认性研究应另行冻结方法/选轮与test。

## 近期报告入口

- report/2026-09-10-goal/persistent_environment_evolution_plan.md：重构动机，不能单独当作已实现证据。
- report/2026-09-12-goal/implementation_progress.md：v5反馈、capability/pool、精确分配与ACE接入。
- report/2026-09-13-goal/v5_cohort_start.md、v5_cohort_restart_20.md：旧两组4B的启动与恢复。
- report/2026-09-13-goal/tau2_split_update.md、tau2_test_replay_repair.md：τ² split和test修复边界。
- report/2026-09-14-goal/experiments_stopped.md：旧三组停止；这不代表9/14新native ACE也停止。
- report/2026-09-14-goal/cross_model_goal.md：native ACE/新反馈实现；8B不是本文4B主实验。
- report/2026-09-14-goal/analysis_cross_iteration_review.md：analysis有用但不能当客观能力趋势的具体反例。
- report/2026-09-14-goal/ace4_native_test_sweep/readme.md：native ACE只冻结R1–R4的test补测。
- report/2026-09-15-goal/ace4_stopped_test_sweep.md：ACE完成R1–R10后停止，R11取消；后六轮Test补测及R6/R8启动失败后的恢复。最终progress在01:26:20北京时间记录全部done。
- report/experiment_dashboard/test_results.py、test_baselines.json：test基线及协议可比性的显示规则。

旧 9/9 的2495文件指纹审计属于历史工作，不被拿来证明这次新worktree或活动run的完整来源。原始framework可能由其他工作继续更新，本文保存的是读取时版本和冻结结果。

## AppWorld用户提供的外部记录

用户提供另一台机器运行的Base/R1–R9聚合CSV，原样保存在data/appworld_user_20260915.csv；SHA-256为a1b9f845ade0bf1210bc7e939f0579b263e51e2740298716488c76686bfd2e10。原列名train_tgc/train_sgc/test_normal_tgc/test_normal_sgc及空字段保留，绘图时只将比例乘100。独立meta文件记录来源，不把这些聚合数冒充本机逐题核验结果。

R9两个Test字段均缺失；train TGC为0.0205761316872428、SGC为0。原行保留不变，但按作者明确要求从主图中排除，显示窗口为Base–R8，缩放和选轮只使用这个窗口。最高train TGC仍为R7：Train/Test-normal TGC为12.345679/12.698413%，相对各自Base为+6.172840/+3.174603 pp。SGC列保留原始值，不再生成额外图形。

目前未提供模型、repeat数、反馈split协议、任务列表或checkpoint原始文件，已经非阻塞询问作者；这些字段保持未知，不套用Qwen3-4B×3，也不生成CI。只保留主图第四面板TGC，此前自行添加的AppWorld附录图与说明已撤下归档。本地三组冻结JSON及结果表数据不变。
