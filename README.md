# EnvOpt · ICLR 2027 工作稿

当前标题：**EnvOpt: Persistent Environment Evolution from Agent Feedback**。

论文仓库：[xhwang22/hzs](https://github.com/xhwang22/hzs)。仓库根目录即论文目录，LaTeX入口为 `main.tex`。

本次按 2026-09-14 的新 framework 与 4B 实验重写了摘要、引言、定位、方法、算法、实验和附录，并更新主图。它已不再描述旧 World–Scene 层级或预训练 student probe。结果为现有实验的冻结快照，不是此次重新训练/评测，也不是完成了所有对照的投稿终稿。

## 直接查看

- [论文 PDF](build/main.pdf)
- [新主图](figures/overview.png) · [可编辑 SVG](figures/overview.svg)
- [主实验演化曲线](figures/evolution.png) · [矢量 PDF](figures/evolution.pdf)
- [结果表所在论文页面](build/page_06.png)
- [固定 benchmark 子项曲线](figures/subsets.png)
- [AppWorld 原始 CSV](data/appworld_user_20260915.csv)
- [当前中文 story 与贡献定位](notes/story_zh.md)
- [当前代码、版本与实验依据审计](notes/evidence_audit.md)
- [RSI / EnvHarness / SPADE 对照](notes/rsi_positioning_zh.md)
- [实验呈现与后续对照设计](notes/experiment_presentation_zh.md)
- [更新后的冻结数据](data/results_20260915.json) · [表格派生统计](data/summary_20260915.json) · [原九轮快照](data/results_20260914.json)

## 此次快照

ACE 更新截止 **2026-09-14 17:43:25 UTC / 2026-09-15 01:43:25 北京时间**，补齐 R5–R10 Test 和 R10 dev/训练记录。τ²/BFCL 保留原 16:04:42 UTC 快照且内容不变。三组均已停止：τ²/BFCL 各 9 个完整轮次，ACE 共 10 个，所有完整轮次均有 Test；取消的 ACE R11 不纳入。重编译不会自动读入新点。

| 4B study | dev 选轮 | 该轮 Test | 末轮 Test | 状态 |
| --- | ---: | ---: | ---: | --- |
| τ² | R5 | 39.33% | 34.05%（R9） | 已停止 |
| BFCL multi-turn | R9 | 42.08% | 42.08%（R9） | 已停止 |
| ACEBench-Agent native FC | R3 | 52.22% | 51.11%（R10） | 已停止，Test R1–R10 完整 |

新增 ACE R5–R10 Test 为 **49.44 / 50.00 / 56.11 / 52.78 / 54.44 / 51.11%**。Test 最高为 R7，但不据此更改 dev 选轮。R6/R8 的首次评测启动失败及成功补测记录均保留。ACE 完整轮次总计 626 题、5,008 个 episode，记录的 episode abort 为 0。

BFCL 的匹配 test baseline 为 25.42%，观察到 +16.67 pp；native ACE baseline 为 41.11%，观察到 +11.11 pp，但其小样本配对区间包含 0。τ² 的历史 test baseline 31.89% 使用修复前回放协议，不作为同协议涨幅依据。未混入旧 textual ACE、归档的替代尝试、8B 实验或未完成轮次。

主实验图现为低矮子图组成的2×2布局，各面板横/纵轴独立适配。横轴分别到R9/R9/R10/R8；标题下两套split读数整体居中，split标签保留紫/金色，Δ数字为绿色。无大白圈、dagger或Success/score副标题。原三组双Δ和validation选轮不变，τ²的R0–R1保持连线。

第四面板为作者从另一台机器提供的AppWorld TGC，仅显示Base–R8，按要求不画R9；原始CSV中的R9仍完整保留。图和图注统一显示Train/Test，原始test_normal字段名不改，在显示窗口内train TGC选中的R7显示Δ +6.17 / +3.17 pp。额外添加的AppWorld附录图和章节已经撤下，图形文件归档在archive/appworld_appendix_removed，不再生成或编入论文。模型、repeat和逐题协议尚未提供，不改变本地三组结果表或虚构CI。

原三组本地 benchmark 各只有一个训练/evolution seed，三次 repeat 是评测重复。结果表按 dev 选 checkpoint，不选 test 最大值；CI 是按固定子类分层、整题保留三次 repeat 的配对 bootstrap，不能代表训练种子方差。以上repeat与训练配置说明不自动套用到AppWorld。

## 当前方法主线

空环境库 → 来源可回查的轨迹分析与能力需求统计 → 持久 Planner 和可修订经验 → 完整 Environment 的 create / revise / retain / pause → 有界构造检查 → 新在线 RL → 目标评测与版本化训练反馈。

当前三个 run 的初始 Git 树已核实没有业务环境模块；框架接口和通用 examples 仍是外部输入。单个 Environment 配对实现 task sampler、episode/state/tools 和 verifier，不要求单独的 World JSON 或 Scene stack。正式训练反馈代替了旧的独立 student admission probe。

## 编译与复现图表

在本目录执行：

```sh
make all
.venv/bin/python tools/render_preview.py
.venv/bin/python tools/check_figure.py
.venv/bin/python tools/verify_paper.py
```

官方 ICLR 2027 模板保持不变。主图为 SVG → 矢量 PDF；实验图和结果表由 `tools/plot_results.py` 从冻结 JSON 生成。表格源码为 `tables/main_results.tex`，请修改生成脚本而不是手工改数值。

首次克隆后，创建 `.venv` 并安装 `requirements-paper.txt` 中的依赖。本地 Tectonic 二进制不入库；若已将 Tectonic 安装到 PATH，可用 `make TECTONIC=tectonic` 编译。常规编译只需要本仓库，不需要访问 framework 或运行中的实验。GitHub中保留编译PDF、当前图形与冻结数据；虚拟环境、工具二进制、下载缓存和本地旧稿/图形迭代不上传。

Overleaf：同步仓库后，将主文档设为根目录 `main.tex`，编译器选 `XeLaTeX`，TeX Live 选最新可用版本。根目录 `latexmkrc` 为 Overleaf 配置 `vendor/iclr2027/` 的 `.sty` 和 `.bst` 搜索路径；不要把模板示例文件设为主文档。若此前提示 `iclr2027_conference.sty not found`，确认已拉取 `latexmkrc`，再执行 **Recompile from scratch**。图已提供PDF，无需在Overleaf运行Python绘图。

`tools/collect_results.py` 是独立的只读采集入口，不在常规 make 中调用；它拒绝覆盖既有快照。本次用 `tools/update_ace_results.py` 仅刷新 ACE，校验已存 baseline、前四轮 Test、前九轮 dev/训练及协议未变，并原样保留其他两个 study。更新脚本拒绝覆盖已生成的补充快照。以后继续更新应另存新版本并明确轮次截止，再审核协议与选轮规则。

Python 依赖仅安装在本目录 `.venv`；缓存留在本目录。没有安装系统级 LaTeX 或修改源项目配置。当前完整PDF为14页；主图第2页、结果表第6页、四面板主实验图第7页。声明/参考文献从第8页开始。原有附录内容保留，未再添加AppWorld图表；实际布局记录在 `build/document_check.json`。

## 尚待补齐

固定库 + fresh Tasks、仅参数/配比适配、无经验记忆、陈旧反馈等匹配预算对照；多训练种子；独立任务质量审计；最终冻结协议之后的确认性 test。现有训练中的 2 个 τ²、33 个 BFCL episode abort 已披露，不称作全程无缺陷。论文仍有作者审核与复现材料的 TODO。

## 只读边界与归档

`../OpenAgentScaler`、`../OpenAgentScaler-env-evolution`、`../OpenAgentScaler-env-feedback` 及对应 benchmark/results 均只读。此次没有启动、恢复、停止、评测或修改实验，没有执行生成环境代码。

旧稿及主图存于 `archive/pre_20260914/`；较早图形迭代存于 `figures/archive/` 和 `figures/refinement/`。原快照的 197 条来源哈希保留不动；更新快照含 218 条来源文件哈希与路径，另记录旧快照哈希和已变化的来源哈希版本，代码/研究笔记另有审计。源目录可能由其他工作继续更新，不能据本次只读写作声称外部目录静止。
