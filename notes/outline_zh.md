# 当前大纲与篇幅安排

当前为 ICLR 2027 匿名工作稿；模板不改。初投稿主文上限9页，声明、参考文献与附录按官方规则另算。当前PDF为14页，主图在第2页、主结果表第6页、演化图第7页，正文延续到第8页。

| 部分 | 当前职责 |
| --- | --- |
| Abstract | 空环境库、可回查诊断、持久Planner/经验、选择性程序演化，以及有边界的4B初步结果 |
| Introduction | 目标实现不可用时如何把行为反馈变成持续训练资产，区分解释、训练信号和目标效果 |
| Related work | RSIBench-Data的setting；EnvHarness的已有backend；SPADE的语料/联合训练；其他合成与自适应方法 |
| Method | 完整Environment；source-linked analysis和真实task关联；create/revise/retain/pause；有界检查与online反馈 |
| Experiments | τ²/BFCL各9轮、ACE共10轮的单种子记录，dev-only选择、完整dev/test曲线、实际预算、test主表与不确定性 |
| Discussion | 重建不唯一、模型分析/审查会错、无匹配消融、维护与数据异常、反复test查看的边界 |
| Appendix | 接口、reward、版本差异、benchmark/native/replay协议、数据快照/统计、subset曲线、待做对照 |

方法不再按World–Scene–Task/cold-start/student-probe组织。核心研究状态为program bank、task-linked requirement map、maintained experience和student/optimizer。当前严格expectation/review契约只属于新native ACE版本，不能追溯给较早τ²/BFCL。

主实验保留过程图和dev选轮主表的互补分工：曲线说明是否持续改善，表说明在明示选择规则下的test效果。附录按固定benchmark子类展开，不按每轮变化的LLM domain label作能力趋势。

尚无固定库、仅采样控制、无记忆或陈旧反馈实验，留作明确的后续对照，不填虚构数值、不抄不匹配文献成绩。图形与具体数据设计见 experiment_presentation_zh.md。
