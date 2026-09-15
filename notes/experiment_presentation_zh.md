# Main experiment 的呈现设计

## 采用：一张过程图 + 一张主表 + 一张附录子项图

### 过程图（Figure 2）

现为2×2四面板：τ²、BFCL multi-turn、ACEBench-Agent native FC、AppWorld TGC。横轴分别适配到R9/R9/R10/R8，不统一拉到10；原三组数据不变，AppWorld按作者要求只显示Base–R8。纵轴取显示窗口内跨度18%或至少2个百分点的留白，范围为24–43、18–50、16–63、4–16。刻度完整，不平滑曲线；AppWorld原始R9行保留在CSV，但不参与绘图或缩放。

采用5.5×3.7英寸2×2布局，单个绘图区保持低矮和原字号。标题下两组读数以组合文本居中排布，不再贴左右两端；split标签保留紫/金色，Δ数字统一绿色#2F8B63。曲线和baseline色不变，最大数据点2.65pt。AppWorld显示Train/Test，原始CSV字段名不改；仅处理主图，不再追加附录图表。

两套Δ均在validation选出的同一checkpoint上计算：τ² Val +8.63 / Test +7.43，BFCL +22.58 / +16.67，ACE +30.00 / +11.11（pp）；不在test上另挑最高点。τ²历史base与R1保持连线；按作者要求，图面及图注不放dagger或对应说明。原始可比性记录、正文与附录的研究边界不改写。ACE R1–R10 Test齐备，不混入旧textual版本；标题注明native FC。

### 主表（Table 1）

每行一个benchmark，列为 t*、Base (%)、Selected (%)、Δ pp [95% CI]、Last (%)。只把dev规则选定的test列加粗，避免把test最大值包装成方法选择。Last是最后完整训练checkpoint的test：τ²/BFCL为R9，ACE为R10（51.11%），表注明确不同轮数。

表格用booktabs、无竖线、轻量列距、数字右对齐。百分比分数与百分点变化分开标单位，不将Δ pp放进一个“score %”跨列表头。τ²不可比baseline有dagger且不计算Δ；ACE脚注说明native FC、两类宏平均与十轮Test齐备。

CI从配对的test task差值计算：在固定subset内有放回采样Task，将该Task的3repeat一并保留，保持原benchmark加权。10000次bootstrap，随机种子20260914。它不是3训练种子，也不是跨seed置信区间。ACE的宽区间跨0，正文明确写出。

### 附录图（Figure 3）

用固定benchmark子类的dev曲线，不用每轮自由merge的domain名字作能力曲线。显示τ² Telecom后期退化、BFCL Missing Function改善、ACE早期Multi-Step增长；只是关联观察，不归因于某次env修改。

AppWorld只在主图显示TGC，Train/Test Δ为+6.17/+3.17 pp。此前自行添加的附录Figure 4及其说明已撤下，图形归档，不再生成。原CSV的SGC列与R9行保留，不因此新增论文图表。

## 当前可写的结论

- BFCL：dev选R9，test42.08 vs匹配base25.42，+16.67 pp。
- τ²：dev选R5，test39.33，R9退到34.05。历史test base31.89协议不完全匹配，不报告同协议Δ。
- ACE native：dev仍选R3，test52.22 vsbase41.11。R7 test56.11更高但不可用test改选；R9为54.44，末轮R10为51.11。十轮Test已全部补齐，R11取消不纳入。
- 不能写“稳定持续提升”“优于所有合成方法”“memory或program revision已被消融证明有效”。

## 后续应补的主表

目前的主表是单种子现象快照，不是最终算法对照表。协议冻结后，用各benchmark作为列、各方法作为行：base、fixed early library + fresh sampling、parameter/allocation-only、full EnvOpt，再加入no-experience/stale-feedback等消融。所有训练和research预算公平记账，保留失败搜索成本。若做SPADE/EnvHarness适配，对信息访问和官方实现差异另行注明，不抄其论文分数填匹配比较。

达到该阶段后，主文保留“跨方法test主表 + 完整evolution图”；版本/子项/质量审计放附录。当前不为尚未测量的行伪造分数。
