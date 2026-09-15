# EnvOpt 当前 story：证据驱动的持久环境研究

更新依据：2026-09-14 阅读的 persistent_environment_v5 代码、9/10–9/14 报告及三组 4B run；9/15 北京时间补齐 ACE R5–R10 Test、R10 dev/训练及停止记录。旧版分析保存在 archive/pre_20260914/notes/；它们不能继续充当当前方法说明。

## 中心问题与主张

我们研究 data-centric RSI 的一个具体环节：当研究者拿不到目标 backend/verifier 实现时，怎样把目标模型的行为证据持续转化成可训练的可执行环境？核心不再是旧 World–Scene 命名，而是 **可追溯的诊断 → 有状态的研究决策 → 长期程序资产 → 新在线经验 → 真实目标反馈**。

新 EnvOpt 从空环境 bank 出发，保留通用接口与中性 examples。每个完整 Environment 定义任务采样、初始状态与 actor 交互、真实工具效果及可复用验收。环境不是每轮全部丢弃：Planner 可以 create、revise、retain、pause，历史版本与反馈保留，省略或暂停的环境不自动补题。

这个 setting 支持 trajectory-grounded reconstruction，但有限轨迹不能唯一还原真实后台。“从零”指业务训练环境库为空，不是没有模型先验、代码框架、examples 或目标 dev 信息。

## 三个技术支点

### 1. 从可回查的机制解释到稳定任务组统计

每条完整 dev 轨迹被分析为环境需求、目标行为与失败行为。树式 merge 在每个节点同时合并 domain 名称与内容，保留来源；控制器计算来源并集与计数。Planner 可由摘要短 ID 查原始公开 case，并比较同题跨轮行为。

这解决上下文预算下“摘要从哪里来、是否把 agent 的错误步骤误写成规则”的调查问题，但来源完整不等于语义正确。9/14 的跨轮审计确实发现过成功标签美化、无依据前置条件和 domain 粒度漂移。

另有稳定 capability ID → 真实 dev task IDs 的 requirement map。Planner 定义关联，程序从记录计算 baseline/current 结果，不让 LLM 写测量分数。它避免直接比较变化中的摘要标签计数；但关联 task 的成绩仍不是组合任务中某个原子技能的独立测量。

### 2. 环境是有版本和采样决策的长期资产

保留有用程序、局部修订不合适的机制、创建缺失模式、暂停不应继续采样的环境，是四种不同决策。横向补机制与纵向调挑战/配额分开；前者不是换主题，后者不是一律加难度。采样参数必须在真实 make_task 中实现。

计划目标是 96 题而不是强制填满：每个选中环境 1–10 题；每轮最多 10 个 create/revise，retain 的库规模不受这个数限制。失败/重复造成明确 shortfall，不通过未规划的简单环境补齐；尾批保留。实际 ACE 题量从 96 到第 9 轮 38，正文保留预算说明，不能把等轮次当等训练预算；按作者反馈，主实验图不再另画题量面板。

### 3. 把训练信号、目标效果和研究经验分开

在线 RL 数据提供每个环境实际版本/参数下的 reward distribution、mixed / all-one / all-zero / constant-partial groups 与异常。固定 dev 则提供目标成绩和行为。没有独立 teacher/student admission rollout，也没有要求 mixed 才能进入训练的 gate。

持久 Planner 审阅这些证据后维护可修订经验。当前较新的 decision_brief_v1 要求 expected_effect 和下一轮 review_previous，区分没落地、训练行为未命中、迁移不明与退化；这个严格字段契约用于新 native ACE，而较早 τ²/BFCL v5 尚未用同一契约。不要把新设计追溯到所有旧轮次。

## 结果支持什么故事

当前 τ²/BFCL 各 9 轮、ACE 共 10 轮，dev 选轮仍为 τ² R5、BFCL R9、ACE R3。对应 test 为 39.33%、42.08%、52.22%。BFCL 相对匹配 base 为 +16.67 pp；ACE 为 +11.11 pp，但 25 题 test 的配对区间跨 0。ACE 的 Test 已完整补齐，R7 达到 56.11%、R10 为 51.11%，不因 Test 最高点改选 checkpoint。τ² 后续回落至 34.05%；其历史 test base 有 replay 协议差异，不给同协议 baseline 增益。图按作者要求连接历史base并显示+7.43 pp描述性差值，不放脚注符号；原始协议记录及正文/附录限定不改写，主表仍不报其增益/CI。

因此主线应是：**这个闭环能找到有用的训练策略/检查点，但持续提升仍不可靠，版本化证据与完整轨迹揭示了发现与保持之间的差距。** 不写“已稳定、单调、普适地解决 RSI”。目前缺固定库/调参/无经验等对照，不能将全部增益归因于代码演化或经验记忆。

## Paper 与实验如何对应

1. Introduction：不可访问目标实现的环境构造问题；为何日志、合成 reward 和域标签不足以指导持续研究。
2. Method：完整程序接口；source-linked analysis 与真实 task 关联；persistent planning 与选择性演化；有界实现/审查；正式 RL 反馈。
3. Experiments：2×2主曲线图，原三组dev/test加作者提供的AppWorld train/test-normal TGC（按要求仅Base–R8）；各自适配横纵轴。dev-selected主表仍仅含本地核验三组，不再添加AppWorld附录图表，不自动套用本地模型和repeat配置。
4. Discussion：重建不唯一、分析/生成/审查会同源犯错、稳定需求组不是技能因果测量、单种子与 operator test inspection 的边界。
5. 后续验证：匹配信息/训练/研究预算的固定库、参数配比、完整演化；无经验或陈旧反馈；独立审计与多种子。

现阶段 novelty 的可辩护表述是这些机制组成的特定研究方法与待检验的收益，不是声称首次有数据库、首次生成有状态代码、首次使用经验或首次迭代。
