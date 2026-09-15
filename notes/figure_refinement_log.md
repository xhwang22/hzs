# 主图的三轮实现、评审与精修

> 9/14 更新：当前主图已按 persistent_environment_v5 改为完整 Environment 库、持久 Planner/经验与两类反馈，不再采用旧 World–Scene 底座。下方9/9记录保留为历史；最新主图、演化曲线与结果表说明在文末。

> 本文保留历史实现记录；当前主图是文末的“视觉重绘”版本，保留轨迹驱动重建主线。早期三栏、Commit 和机制执行案例图均不是当前版本。

这次以用户的三个要求验收：技术设计可读、自动 data-centric RSI 回路明确、信息粒度合适。同时检查演化维度、具体案例、纸面字号和视觉风格。所有修改只在 paper 工作目录；未改动或运行 OpenAgentScaler。

## 最终结构

- **(a) Data-centric RSI：** 一条连续回路连接自动程序修订、候选检查、fresh training tasks、当前学生交互、在线 RL 和固定 dev 反馈。Evolver backbone 固定；学生明确标记为 θ(t)，训练更新为 θ(t+1)。
- **(b) Technical design：** World → Scene → Task 的层级，旁边解释 capabilities 和 mechanisms。Workload 与 sampling mix 放在分隔线以下，作为 generator controls，不冒充第四/第五个层级，也不暗示逐 Task 手工改源码。
- **(c) Concrete instance：** 用同一个 Commit Scene 展开一个目标 8 的任务。写操作先产生 pending=8，实际 stored 仍为 3；commit 才使 stored=8。请求与 verifier 绑定相同目标。

图中 record store、Clarify、Commit 对应源码的中性示例。`examples/demo.py` 的初始记录值为 3，位置为 center；`private_choice.py` 的目标位置为 east/west；`staged_update.py` 的目标由参数提供，默认 8。图中的 target 12 是同一参数化构造器支持的示意变体，不是实验数据。条形配比也是示意，不表示测量到的训练比例。

## 评审设置

先尝试使用 gpt-5.6-sol 做独立评审，两次均在返回前因流连接中断失败，未计入完成的评审。随后使用独立上下文的 `design_review` agent，只读图、实际论文页面和方法证据；它没有修改图或源项目。

该评审者实际完成了三次检查：本轮开始时的旧图、第一次实现后的 round 1、第二次实现后的 round 2。第三轮实现只落实第二轮评审提出的措辞精修，并由主 agent 做最终渲染、灰度和几何检查。以下评分是独立评审的主观诊断，不是客观研究指标。

| 独立评审对象 | 技术清晰度 | 自动递归 | 层级／演化维度 | 纸面可读性 | 美观 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 本轮开始的旧图 | 3/5 | 3/5 | 3/5 | 2/5 | 3/5 |
| Round 1 | 4/5 | 4/5 | 4/5 | 3/5 | 4/5 |
| Round 2 | 4/5 | 5/5 | 4/5 | 4/5 | 4/5 |

## 第一次实现

旧图的主要问题是大图标和宣传标题占据空间、底部回路被标题遮断、World–Scene–Task 只显示层级而没有显示可改维度。Round 1 改成上下两层：上方完整自动循环，下方为技术展开与小案例。

自查与独立评审找出：generator 文案挤出节点、World 图标挤压文字、Mixture 像第四级层次、任务叶节点缺少目标字段、probe 与正式 rollout 的关系不够明确、部分小字缩到论文宽度后过小。案例初始状态还需要从一般示意值 0 对齐到实际 demo 源码的 3。

产物：[图](../figures/refinement/round_1/overview.png)、[实际论文页面](../figures/refinement/round_1/paper_page.png)。

## 第二次实现

Gate 移到 fresh production 之前；Interact 显式标出 Student θ(t)，RL 标 θ(t)→θ(t+1)。固定 Evolver、目标字段、源代码一致的初始值均补齐。Workload 和 Mixture 与三级层次分开。案例标题与 Commit Scene 同色、同名，删掉重复解释句，文字加深并放大。

独立评审认为已达到可用的论文主图水平，没有必须返工的问题。其两个剩余建议是：`Code + mixture` 改成涵盖 workload 参数的 `Program + config`；`Mixture` 改成 `Sampling mix`。它也确认这版案例值得保留，验证不再主导叙事，图没有暗示学生接任 researcher 或成绩必然提升。

产物：[图](../figures/refinement/round_2/overview.png)、[实际论文页面](../figures/refinement/round_2/paper_page.png)。

## 第三次实现

采用上述两处措辞修改，增大 Task 卡片的上下内边距，增加 sampling mix 标签与配比条之间的间距。最后检查正常配色、灰度、5.5 英寸单栏缩放与 PDF。

最终检查结果：

- 按论文 5.5 英寸宽度计算，最小文字约 **7.07 pt**；主要标签约 7.6–9.6 pt。辅助说明仍比图注小，但已避免先前的 5–6 pt 小字。
- 导出的 PDF **不含嵌入位图**；图形和文字均保留矢量，SVG 可编辑。
- 自动检查未发现 text-span 相互重叠或超出画布；这个检查不证明所有图形关系正确，另做了实际看图。
- 灰度下仍可通过标签、连线与布局判断层级和案例，含义不单独依赖颜色。
- LaTeX 编译成功，无未定义引用或横向溢出；主图仍位于第 2 页，主文 8 页。原有非阻断的排版 underfull 提示保留。

最终产物：[主图](../figures/overview.png)、[SVG](../figures/overview.svg)、[矢量 PDF](../figures/overview.pdf)、[论文](../build/main.pdf)。第三轮快照和灰度预览位于 `figures/refinement/round_3/`。

## 保留的边界

图没有把没有实现的分层信号调度或自动语义证明画成事实。四类演化维度对应当前可改内容；学生实际性能是否随着这些迭代提高，仍是论文待验证的问题。分项 reward、预算异常分支、GPU/服务编排、每条 validation case 等细节保留在正文/附录，避免再次挤占主图。

## 2026-09-09：机制导向重构

用户指出，图中的 RSI、层级与验证流程仍不足以说明 contribution。本次以 [contribution_thesis_zh.md](contribution_thesis_zh.md) 为依据，聚焦“能力失败 → 可复用机制程序修订 → 新在线经验 → 学生反馈”。这不是新的效果结论，也不把程序生成、RSI 或层级名称单独包装为首创。

### 第一次实现与审查

旧主图已保存在 `figures/archive/overview_v5.*`。新图沿用易读的矢量样式，作了三个内容调整：

- 上方回路明确以学生失败和训练轨迹驱动下一次机制修订。
- 左侧改为实际 file/session World 的多 Scene、多 Task 扇出，构造—验收配对放进 Scene 卡片；workload 和 sampling mix 与程序层级分开。
- 右侧用 DeferredFile 的延迟目标、同文件指代、噪声中的实际读数和真实产物，替代中性 Commit 数值示例。

主 agent 查看完整图与实际论文第 2 页；独立 `design_review` agent 也读完最新 contribution 笔记并实际看图。其主要意见是：仍需从“机制表达什么”推进到“Scene 编辑改变什么”；源内容到数值输出可能被读成普通 QA；上图 Instantiate/Fresh tasks 位于 probe 前，容易与 caption 的生产顺序产生歧义。未增加未经观测的 revision 前后成败对照。

快照：[第一版图](../figures/refinement/mechanism_round_1/overview.png)、[纸面](../figures/refinement/mechanism_round_1/paper_page.png)。该快照故意保留当时的顺序歧义，便于追踪修改。

### 第二次实现

- 上方改为 **Program bank / Programs + controls → Admit → Fresh tasks / Interact**。Admit 压缩表示候选检查与 fixed-student probes；不表示一定通过或必然产生模型更新。
- Scene 明标 **edit unit**，Task 明标 **goal data**；多实例由分支直接展示，不再用一行重复层级的文字解释图。
- 右侧明确 **Scene edit: timing + write access**：读源文件后，下一 user turn 揭示后续目标，再允许输出写入。三段标成 **Tool observation / Next user turn / Tool write**，不是输入文字到输出答案的静态 QA。
- 底部 **Constructor ↔ verifier** 配合 source/readings/output goal，说明配对复用的语义依据；不暗示所有目标数据提前可见给学生。
- Caption 与方法段落同步改为 DeferredFile，并将 verifier 的范围明确为实际源文件读取记录及结果文件状态，不声称验证了全部推理过程或证明语义正确。

### 源码与示例边界

以下路径均位于只读的 `../OpenAgentScaler/envopt/runs/20260908-031723-53c19e-stable_bfcl/env/bank/file_session/`：

- `deferred_file.py`：`setup` 构造源文件和实际读数；`call` 在后续请求前阻止写入，并记录正确源文件已读；`user_turn` 在读后揭示 same-file 请求；`make_task` 与 `check` 共享具体数据。`check` 检查正确输出位置、内容、其他文件不变，以及实际读取相同 source ID 的记录。
- `private_destination.py`：多个公开目的地同样可用，用户偏好私有；揭示偏好后再允许写入。图中 `alpha/bravo` 是 `staging_alpha/staging_bravo` 的短标签，不是另造的测量任务。

DeferredFile 案例使用受支持的 integer-only / listed 变体。示意实际读数 `[18,24,30]` 的均值为 24，draft `[25,35]` 符合实现中的噪声生成规则；另一 Task 叶节点 mean=31 可由 `[21,31,41]` 得到。数值、简写对话和配比条均是示意，**没有执行这些任务，也没有把它们称为真实 rollout 或已验证的 revision 收益**。Workload 的 size/depth 是跨机制的一般控制示例，不宣称 DeferredFile 存在独立的 reading-count 消融旋钮。

图中没有加入尚未实现的成对 decision-preservation 检查、反事实约束优化、自动迁移保证或新学生接任 Evolver。所有源项目访问均为读取，未修改或操作实验。

### 编译与视觉检查

运行 `make all`、`tools/render_preview.py` 和新增 `tools/check_figure.py`：论文仍为 14 页，主文 8 页，主图第 2 页。实际 5.5 英寸宽度下最小字体约 **7.07 pt**；图形为纯矢量，无嵌入位图；文字 span 无相互重叠、无画布越界。第一版发现的 World 两行文字包围盒相交已通过增加行距修复。源 SVG 保持可编辑，未从 PDF 反向覆盖。

最终快照：[第二版图](../figures/refinement/mechanism_round_2/overview.png)、[纸面](../figures/refinement/mechanism_round_2/paper_page.png)。灰度与纸面尺寸的预览、几何检查报告一并保存在该目录。几何检查不证明语义正确，因此仍配合实际看图与独立审查。

独立评审再次查看第二版完整图、纸面尺寸图和论文页面，确认没有仍必须修改的事实或可读性问题。随后主 agent 仅压缩 caption 和对应方法段落的重复措辞，保留所有机制和证据边界，重新编译并检查第 2 页及正文结尾：完整 Discussion 仍在第 8 页结束，第 9 页从 AI use statement 开始。模板、字号和版心未改；现有非阻断的 algorithm.sty 编码提示及 underfull vbox 保留，无未定义引用或横向溢出。

## 2026-09-09：轨迹驱动重建，重新选择视觉中心

用户进一步明确：之前图仍没有呈现 EnvOpt 相对已有方法的区别。新的中心是 **目标可见轨迹 → 推断机制 → 构造可执行训练任务族**，而不是“已有 program bank → 训练”的一般系统回路。详细定位、源程序依据、近邻对照及初始化边界见 [trajectory_reconstruction_zh.md](trajectory_reconstruction_zh.md)。

旧图已保存为 `figures/archive/overview_v6.*`，包括当时图注。第一次重排保留纯矢量图标与原 1400 × 920 画布，改为三栏并将 RL/评测缩成底部反馈回路。目标环境实现有锁标记，左侧是轨迹证据，中间是固定 coding Evolver 的推断与设计，右侧是一对多的程序/任务层级。

主 agent 实看完整图与印刷尺寸图；独立 `design_review` 先看图再读 caption，认为信息边界及重建主线已可直接识别，不易再误读为包装原环境或静态 QA。但它指出两处重要事实边界：World 的预置来源不应只在图注披露；合成目标设计不应像从轨迹恢复了官方 verifier。主 agent 另发现绿色卡片文字越出卡片、RL → eval 箭头被误标为 Fresh episodes。

第二次修改落实：

- World 内直接标 **curated foundation**；构造/evolve 不冒充当前严格空初始化。
- 中列改 **Infer & design**，绿色卡片写 **Design task semantics**，将目标机制推断与合成任务验收设计区分。
- 轨迹示意增加具体工具返回与短时间箭头，补入历史报告支持的 **Claimed write, no effect** 失败类型；图中与图注都标明是综合示意，不是某条真实日志。
- 底部标 **Interact + RL → Updated student → Fixed-dev evaluation**，明确学生更新和评测顺序。
- 缩短卡片文案、增加目标锁图标与标题的间距；不缩小字体规避空间问题。

已同步修改图注、方法开头和文件例子段落。没有改动源项目、运行实验、修改 ICLR 模板或将 proposed decision-preservation checks 加进当前图。第一轮快照保留已发现问题；第二轮保存最终矢量图、论文页面、纸面尺寸/灰度预览与检查报告。

最终独立复核确认，图本身已表达目标实现不可见、轨迹驱动构造、独立训练任务族和递归反馈，未发现仍必须修改的事实、箭头或阅读问题。主 agent 再看最终第 2 页与灰度图：最小印刷字号约 7.07 pt，纯矢量 PDF，无文字 span 重叠/越界，编译无未定义引用或横向溢出。全篇 14 页，完整 Discussion 在第 8 页结束，第 9 页从 AI use statement 开始。原有非阻断排版/编码警告保留。

产物：[第一轮](../figures/refinement/reconstruction_round_1/overview.png)、[最终图](../figures/refinement/reconstruction_round_2/overview.png)、[最终纸面预览](../figures/refinement/reconstruction_round_2/paper_page.png)、[检查报告](../figures/refinement/reconstruction_round_2/figure_check.json)。

## 2026-09-09：视觉重绘，不再以技术可读性代替审美

用户明确反馈三栏版“非常丑”。本次没有继续加方法标签，而是重新分配视觉重量。旧图已存为 `figures/archive/overview_v7.*`。独立评审本次只做审美诊断：三栏卡片同权重、图标像素材拼贴、粗回线像边框、标题/解释比实际图形更重。

新构图以中央 World–Scene–Task 为完整视觉对象：底座表示共享 World，两个有折角的程序页表示 Scene，上方小任务页表示实例。左侧改为无框、单线、少量强调色的行为时间线；固定 Evolver 为小代码标记；右侧学生为统一线条的芯片示意。反馈回路改用有留白的曲线。技术解释保留在 caption，World 的 curated 初始化边界仍在图内。

第一轮实际看图后继续删减：去掉封面式长标题和底部大号 RSI 字样，将 RSI 标注放在反馈弧线旁；降低芯片实心色块的重量，强化中央 Scene/World 的文字；删除 World 平面上无标注的装饰小块。两类 Scene 收敛为青绿与浅暖色，失败仅用少量陶土色。不使用渐变、光晕、装饰性 emoji 或栅格生成背景。

最终画布由 1400 × 920 缩为 1400 × 660，减少约 28% 高度，没有缩小最小字号。固定 5.5 英寸印刷宽度下仍约 7.07 pt；纯矢量、无嵌入位图，文字 span 无重叠/画布越界。修复左侧曲线末端方向和 World 前立面的文字边距。图注改为解释从下到上的层级；workload/mix 的文字移入图注而非声称删除这些控制。

技术边界未改变：没有从零启动的新实验，没有恢复官方 verifier 的保证，没有引入未实现的设计，也未修改源项目。审美判断不以评审者“通过”代替作者意见；本次记录具体视觉修改和可验证的排版结果。

## 2026-09-14：新版完整环境框架与真实结果

这次不是继续润色旧图。重新阅读了两个新 worktree、9/10–9/14 重构/审计报告、Planner/生成/分析/反馈代码和三组4B记录，核实新 run 空环境bank起步，并已删除旧 mandatory World–Scene 与独立 student probe 叙事。旧稿整体保存在 archive/pre_20260914/。

新主图沿用克制的青绿/暖色、程序页和开放曲线语言：target evidence 经source-linked analysis进入persistent Planner；Planner维护经验，选择create/revise/retain/pause；中央是可持久复用的完整程序库，每个程序包含sampler/interaction/verifier。初始空库、版本号、暂停保留都在图上可见。正式在线训练的版本化reward/trace与固定dev结果分别回到研究过程。

主实验图是三列、上下两层：完整dev/test轨迹（相同纵轴、不同线型/点型）加实际题量；标dev选轮，τ²旧test基线断开，native ACE缺失test不补值。主表按dev规则列选择轮、test base/selected/last与配对Task bootstrap的Δ区间；固定subset细分曲线放附录。实现与数值由冻结data/results_20260914.json驱动，图和表不手抄数据。

独立review实际查看主图、主实验图、论文结果页及冻结数据/绘图实现，指出并已修正：训练反馈应进入Planner而非直接自动写入经验；独立ACE图需native FC标签；repeat3句子需限定已测dev/test；百分比分数和百分点Δ不能放在同一个跨列表头。另修正主图文字/虚线拥挤和附录长字段溢出。评审不是对方法有效性的验证。

最终检查包括数据重算与split/选轮/版本边界、矢量输出、印刷字号、文字边界和编译。没有修改framework、执行生成环境、启动或干预实验。快照截止14 Sep 2026 16:04:42 UTC，仅首9个完整轮次；ACE后续进度不自动写进论文。

交付前再检查主图、主实验论文页和附录子项图，发现 BFCL 最后一项图例过于贴近底边。增加附录图底部留白，保持曲线面板高度，并添加图例边界断言。重新运行完整编译、页面预览、主图检查和离线数据核验，全部通过：14 页，主图第 2 页、主表第 6 页、演化图第 7 页，声明/参考文献从第 8 页开始；197 条来源哈希记录，主图纯矢量、最小印刷字号 7.07 pt，无文字重叠或画布越界。未定义引用和横向溢出未出现；既有 algorithm.sty 编码提示和 underfull vbox 是保留的非阻断警告。

### 作者反馈：压低演化图、移除 Tasks 面板

去掉主实验图下方的 Tasks 柱状图，画布由 5.5 × 3.2 英寸改为 5.5 × 2.1 英寸，高度减少约 34%。三张图分别保留完整纵轴刻度，同时保持统一 0–65% 范围；统一单行标题与次级度量标签、细线和浅网格，缩减 ACE 未测区的说明文字。没有改动任何数据点、选轮规则或不兼容基线的断开标记。

同步删除 caption 的 Top/Bottom 描述，题量预算说明保留在正文而非图中。查看独立图和嵌入页面后完成重新编译及离线核验；新增检查确保无 Tasks 面板、三组纵轴刻度完整、画布高度正确。全篇仍为 14 页，演化图现位于第 6 页、结果表位于第 7 页；README 链接同步更新。源项目和 live runs 未访问或修改。

### 作者反馈：连接 baseline 并标注 Δ

按要求将 τ² 的历史 R0 test 接至 R1，不再使用断开的三角；去掉子图标题下的 Success/score 说明，将 native FC 合入 ACE 标题、百分比单位移至图注。三图在 dev 选中的 checkpoint 上圈出 test 值，并以短引线标注相对各自 test baseline 的差值：+7.43 pp†、+16.67 pp、+11.11 pp。选择规则仍与主表一致，不改用 test 最高点。τ² 的跨协议限定保留为图注 dagger，原始可比性记录及主表空缺增益/CI 不变。

独立图和第 6 页实际预览已检查，标记未遮住其他轮次；画布仍为 5.5 × 2.1 英寸，各自纵轴刻度保留。重新编译与离线核验通过，新增按冻结数据核对三项 Δ 文本及删除副标题的断言。论文仍为 14 页，主结果表在第 7 页，源项目未访问或修改。

### 9/15 北京时间：补齐 ACE Test

只读核对停止报告、两批Test progress、完成status、逐题结果和R10训练outcome。ACE已完成十轮并停止，R11无完整checkpoint；补入R5–R10 Test（49.44、50.00、56.11、52.78、54.44、51.11%）及R10 dev/训练记录。R6/R8的推理前toolchain启动失败及成功恢复记录保留，不将失败尝试当成额外测点。

新增不可覆盖快照data/results_20260915.json，时间17:43:25 UTC / 01:43:25北京时间，218条来源哈希。原快照及τ²/BFCL数据不变；ACE旧baseline、前四轮Test和前九轮其余数据逐字段一致。正常make改读新冻结文件，不采集源项目。

主图和附录曲线横轴延伸至R10，移除Test through R4；保持低高度、各面板纵轴和Δ标记。ACE仍按dev选R3，所以Δ维持+11.11 pp；主表Last补为R10的51.11%，图注、引言、实验、附录、中文说明同步删除运行中/缺失Test的旧表述。十轮实际总题量626、episode数5008。

重新编译、查看独立曲线/附录图/论文第6和7页，并通过离线数据、旧快照哈希与内容不变、选轮、Test补齐、图形文本及矢量检查。全篇仍14页；演化图第6页、主表第7页。除既有algorithm.sty编码提示外没有编译问题；没有修改framework或运行/干预任何实验。

### Dashboard 风格重排：双 Δ、独立尺度、小数据点

只读参考 dashboard 的 app.js 中 bestCheckpoints/chart 与 style.css 的 Val/Test 样式。它按Val选择共同checkpoint，并独立计算两套baseline差值；本图沿用这一逻辑，没有改成各自挑Test峰值。图形重排为标题、并排Val/Test Δ读数、完整曲线；采用紫/金配色、实/虚线、小圆/方点和两条淡baseline点线。大白圈及其引线全部移除，最大数据点从5.2pt降至2.65pt。

纵轴依据各自完整Val/Test历史（含两套baseline）添加max(2pp,跨度18%)留白并取整：τ² 24–43，BFCL 18–50，ACE 16–63。各自刻度完整；图注明确独立缩放，不能跨图用斜率比较增益。Val Δ为+8.63/+22.58/+30.00，Test Δ为+7.43/+16.67/+11.11，共同选轮R5/R9/R3。

首版实际查看后，第二版收紧读数与图面的间距、微调选轮标签字号，保持5.5×2.1英寸。按作者随后要求，去掉图面dagger及对应图注说明。未改写原始结果、可比性记录或其他实验数据。

已检查独立图、144dpi纸面尺寸、灰度版和最终论文第6页。自动校验六个Δ的精确计算、独立完整范围、点大小、文字无重叠/越界、纯矢量与冻结结果一致；编译通过，仍14页。首版和最终版保存在figures/refinement/evolution_dashboard_round_1及evolution_dashboard_final；常规构建不查询源实验。

### 加入外部AppWorld轨迹

将用户粘贴的完整CSV单独保存，原三组数据不动。主实验图改为5.5×3.7英寸的2×2四面板，新增AppWorld TGC；每个绘图区仍为低矮比例，使用原字号、点大小、紫/金配色和独立纵轴。AppWorld标Train/Test-normal，不把其train当成已确认的Val协议；按train TGC最高的R7显示+6.17/+3.17 pp。缺失R9 test用NaN断线，不补零、复制或插值。

附录另加AppWorld TGC/SGC双图，SGC也按同一R7显示+6.17/+3.57 pp。保留R9 train TGC/SGC的真实下降，不根据曲线猜测训练原因。主表仍仅列有本地核验的三组4B结果，模型/repeat等待作者补充。

已查看独立四面板图、双指标图、最终论文第7与14页，并重跑编译/数据验证。验证包含CSV原精度与哈希、R9空值、共同选轮、双指标Δ、四个独立纵轴、图中文字无重叠越界及纯矢量。PDF现15页，主表第6页、演化图第7页、AppWorld双指标图第14页；无未定义引用或横向溢出，已有非阻断编码/underfull警告保留。未访问另一台机器或操作源实验。

### 按作者限定范围：仅主折线图，AppWorld截到R8

撤回此前自行添加的AppWorld附录章节、双指标图和相关正文段落；未删除原有附录图表。额外图形和旧预览转入archive/appworld_appendix_removed，可恢复，绘图脚本不再生成这些附加图。原CSV及R9数据完整保留，metadata明确按作者要求仅显示Base–R8；AppWorld纵轴重新按该窗口适配为4–16。

主图四个横轴分别自适应到9/9/10/8，刻度由各自范围计算；双读数用组合文字盒居中对齐benchmark标题，标签保留紫/金色，八个Δ数字改为绿色#2F8B63。没有改动原三组数据、选轮、线条或原有结果表。检查显示标题/读数/刻度无重叠或越界，组合读数中心与面板中心误差小于0.5pt，PDF中八个Δ均为指定绿色，AppWorld不包含R9绘图点。

重新编译并查看主图与论文第7页，数据、原CSV哈希、显示窗口、独立横纵轴、颜色、居中和无额外Figure 4的验证通过。全篇恢复14页，主表第6页、四面板图第7页；无未定义引用或横向溢出，既有非阻断警告保留。

### 方法主图：按作者的三困难—三设计重排

主图改为三层：上层from-scratch data-centric RSI研究者/环境/学生反馈闭环；中层Direct Codex的三个设计困难（持续可执行多样性、行为覆盖、定向生成）；下层一一对应目标grounded构造pipeline、可追溯归并analysis和target-linked环境pool。保留代码页、学生芯片、靶标、归并树与reward图标；去掉API方法、逐项验证、版本号、四种action及经验文件等细节。旧图保存在figures/archive/before_story_redesign。

grounding按作者定义表示“这个env针对什么benchmark需求”的显式声明，不是额外语料来源。归并树保留来源，图中紫色路径表示摘要回查具体case；当前公开query直接发布summary→cases索引，不能把任意中间节点浏览界面当作已验证功能。case–env–reward链接表达可追溯的训练目标，不等于保证每个Task都有效迁移。Direct Codex部分是困难/方法动机，没有新增未核对的失败baseline数值。

实际查看初版大图及第2页后，将右下case图标/标签左移，避免贴近关联箭头；图注增加RSIBench-Data setting引用。保留25px最小字体，对应5.5英寸印刷宽度7.07pt；纯矢量，无文字重叠或越界。本次只改方法主图、图注及相应说明，不改变实验折线图、数据或附录图表。

### 从挑战列表改为原生Codex工作流

按作者要求，上层移除from-scratch角标、fixed model/empty at start/online RL及箭头上的小字，保留Researcher → Training data → Model和Traj. + feedback回路，Training data改用普通数据页图标。中层标题改为Typical research workflow with native Codex，加入Analyze trajectories → Generate data → Submit data的图标及明确箭头，各步骤下对应行为覆盖、数据多样性/可执行性和反馈关联困难。

下层重新排序，使Traceable merge analysis、Target-grounded pipeline、Target-linked env pool分别垂直对应中层的分析、生成和提交阶段。Caption保持两句，不重复工程细节。旧图存于figures/archive/before_native_workflow。

已实际查看独立图及论文第2页，重新编译和核验通过；14页，最小印刷字体7.07pt，纯矢量，无文字重叠/越界。没有改实验折线图或添加附录内容。
