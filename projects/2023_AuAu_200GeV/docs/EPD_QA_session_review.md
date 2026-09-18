# EPD calibration: evidence review and next executable step

Date: 2026-09-17. Scope: Run23 Au+Au 200 GeV, candidate_v1 preparation.

**当前尚未生成可用 candidate_v1。** 已完成代码与现有 QA 图检查，并准备了可运行的 QA 脚本。当前环境没有 Day190 原始 ADC 谱，也没有完整 daily/period 数值表；不能完成真实数据 refit、全 detector 排名或接受 calibration constants。

## 1. 已核实的发现

| 发现 | 证据与解释 |
|---|---|
| Day190 EW0 PP1 TT1 的 daily MPV 很低且误差很小 | 远程 notebook 保存的输出显示 `30.02668 ± 0.468794`，标记 `different_from_nominal`。这与交接一致，但只凭该数字不能判定原始谱拟合失败。 |
| 约 87.6 的 period constant 仍待独立重算 | 87.6 来自交接；没有完整 daily 数据及其误差，无法在此重新计算 Day190 的权重占比或 corrected constant。 |
| 207–208 的偏离不限于一个 tile | 已查看 `ADCDelta_190_208.pdf` 全部 24 页的概览。两侧多个 sector 在最后两日呈现成片较大的绝对残差；这是检查共同变化的依据，尚不是 detector-wide split 的结论。 |
| Day193 有更极端的数值异常 | notebook 输出记录 EW1 PP11 TT26 的 MPV 约 `8.588179e21`、误差约 `1.414214`；PDF 第 23 页对应色标达到 `10^21` 量级，其他 tile 的变化因此几乎不可见。 |
| 名义值标记依赖实际使用的代码版本 | 远程 `FindNmip.C` 对 TT1 使用 nominal=115，偏离大于 15 才标记；交接里 191–206 约 103–109 却被标记。需取得实际 Run23 版本，不能把远程参数当作生产参数。 |

PDF 画的是 `abs(daily MPV - period constant)`，不能据此判断变化的正负。每页自动色标不同；一片蓝色不能解释为该 sector 稳定。检查共同变化应使用 signed daily differences，并核对 run/硬件记录和拟合谱。

## 2. 第一批复核对象（不等于完整排名）

这些条目来自交接、已保存的 notebook 输出和 PDF。notebook 显示值可能经过舍入；最终应以原始数字文件为准。以下都是 `manual_review`，没有据此把 tile 标记为 bad。

| 顺序 | Day / tile | 当前证据 | 下一步 |
|---|---|---|---|
| 首个诊断 | 190 / EW0 PP1 TT1 | MPV≈30.02668，误差≈0.468794 | 打开 ADC 谱，确认自动拟合选中了什么；若 refit，记录旧值、新值和拟合设置。 |
| 极端值排查 | 193 / EW1 PP11 TT26 | MPV≈8.588179e21，误差≈1.414214 | 优先复核谱、拟合状态、协方差与输入来源。 |
| 极端值排查 | 193 / EW1 PP11 TT27 | MPV≈−2.752833e11 | 不能作为正的物理 calibration MPV；保留记录，复核来源与拟合。 |
| 极端值排查 | 193 / EW1 PP7 TT24 | MPV≈1.142534e5，误差≈1.414214 | 与 PDF 第 19 页对应，复核拟合。 |
| 极端值排查 | 193 / EW1 PP12 TT1 | MPV≈6.432941e5，误差≈1.414214 | 与 PDF 第 24 页对应，复核拟合。 |
| 后续时段 | 211 / EW1 PP11 TT20；212 / EW1 PP10 TT20 | notebook 记录约 3.961828e19、1.063701e7 | 211–213 的 constant fit 前一并检查。 |
| 时段变化 | 207–208 / 两侧多个 sector | PDF 有共同偏离迹象；目标 tile 约 134–137 来自交接 | 计算 signed median shift、每 sector 同方向 tile 比例，结合 run logs 决定是否分段。 |

## 3. 可运行 QA 脚本

文件：`epd_period_qa.py`。仅需 Python 3 标准库，不依赖 ROOT、pandas 或 numpy。

在 `projects/2023_AuAu_200GeV/` 下，脚本放入 `src/` 后运行：

```bash
python3 src/epd_period_qa.py data/derived/daily_observations_primary.csv \
  --start 190 --end 208 --split-day 207 \
  --out data/derived/qa_190_208_v1
```

也支持原始带标记的每日 TXT，或六列 merged daily TXT：

```bash
python3 src/epd_period_qa.py NmipConstantsDays190_208.txt \
  --start 190 --end 208 --split-day 207 --out qa_190_208_v1
```

**优先使用保留 `auto_flag` 的 daily CSV 或原始 daily TXT。** 数字清洗后的文件无法恢复已删掉的标记；脚本会记为 `unknown_qa`。不得输入 `Nmip_Day_190.txt` 等 period constants。输出目录必须不存在，避免覆盖上一轮。

| 输出文件 | 内容 |
|---|---|
| `period_qa.csv` | 744 个 tile 的 constant、constant_error、chi2、ndf、chi2_ndf、最大残差、最大权重、missing/flagged days、status 等。 |
| `tile_qa_queue.csv` | 按优先级、chi2/ndf、最大残差排序的 tile 复核队列，包含 missing coverage。 |
| `manual_qa_queue.csv` | 按优先级和 leave-one-out constant shift 排序的 tile-day 队列，保留输入文件与行号。 |
| `input_audit.csv` | 本次时段内每条原始数据及数值排除原因。 |
| `sector_step_diagnostic.csv` | 指定 split-day 前后每个 sector 的 signed median shift 和超过阈值的正/负变化 tile 数；不执行分段。 |
| `qa_run.json` | 输入与脚本 SHA-256、阈值、时段、行数及状态计数，便于追溯。 |

### 统计与状态约定

- constant 使用独立误差假设下的逆方差加权常数拟合；constant_error 仅为该模型的统计误差，不包含系统误差，也未按高 chi2 放大。
- **带 `fit_failed` / `different_from_nominal` 的正有限 MPV 仍进入诊断 constant**，以暴露原始结果的影响，并明确列入复核；这不是接受该 calibration。
- 非有限或非正 MPV、非有限或非正误差不进入加权拟合，原因留在 audit 中。大但有限的误差不单独触发剔除。
- 没有 sigma clipping、误差下限、自动替换、自动接受或自动 split。移除单日仅用于 leave-one-out 诊断。
- ndf=0 或无可拟合点时 chi2/ndf 留空，不写成 0。缺失 tile 的 constant 留空，不补零。
- 状态只有 `provisional`、`manual_review`、`missing`。`accepted` 和 `bad` 留给后续有证据的审阅决定。
- 默认 10 ADC、6σ、chi2/ndf>5、最大权重超过均匀权重 5 倍，都是可配置的**复核阈值**，不是已验证的 physics acceptance cuts。leave-one-out pull 也不是经多重比较校正的显著性。
- split-day 诊断比较两段 median，每段至少两个数值有效点；它只能提示 step/drift，不能区分真实变化、拟合算法变化与运行条件变化。

验证：与独立 numpy 加权最小二乘对照；合成异常点影响排名、两段变化、无效数值/零误差、单点 ndf、744-tile 缺失覆盖、重复行和错误格式拒绝、period 输入拒绝及防覆盖检查均通过。**尚未对真实完整数据运行，也未与 ROOT 运行结果直接对比。**

## 4. 现有 DayFitsHistos.C 的改进点

代码审查使用当前上传版本，未覆盖它。

1. 它计算 `tChi2` 和 `tAveErr`，但没有写入输出，`Nmip_Day_*` 第六列固定写 `0.0`。该零值是输出占位，不代表已测得零不确定度。
2. 固定读取 `744 × days × 6` 个数，未检查打开/读取成功、重复键或索引范围。缺行或格式中断可能使零值进入后续索引；这属于待修复的输入验证问题，不能据此认定当前完整数据已受影响。
3. period fit 失败时退回 simple mean，并把 chi2/ndf 写进内存为 0，未把失败状态随 constant 保存；后续 candidate 不能把这种结果当成正常拟合。
4. 建议保留原始 daily flags 的独立表。新脚本已提供不依赖修改 ROOT 宏的 sidecar QA 输出。

## 5. candidate_v1 覆盖清单

下表的可用性来自交接，**不是本次对完整 constants 的验证**。当前没有这些数值表的完整内容，未编造 744-tile constants 或 accepted 状态。

| 时段 | 来源 | 交接状态 | candidate 前所需工作 |
|---|---|---|---|
| 162–168 | Yuno | reviewed daily | 取得完整数据，做 period fit；明确主要分析范围是否仅从 167 开始。 |
| 169–175 | Cameron | period result + badTiles | 读取 period 表和 badTiles，保留逐 tile QA；已有 collaborator result 不等于全部 tile accepted。 |
| 176–182 | Ding | 744 constants + PDF | 取得数字表，用 daily 数据计算 QA，并确认人工修订。 |
| 183–186 | Eloy / Erik | period result | 读取 `Nmip_Day_183.txt`、相关 refit 和 QA。 |
| 187 | — | no data | 记录 no-data gap；不填造 calibration，不自动跨 gap 延长有效期。 |
| 188–189 | Eloy / Erik | period result | 将 `Nmip_Day_189.txt` 解释为 188–189 period，读取 QA。 |
| 190–208 | Ding | 744 constants + PDF，有明显异常 | 完成 Day190、Day193 复核和 207–208 范围诊断；拆段保持待定。 |
| 209–210 | — | locally unavailable | 记录缺失，需找回数据或获得有依据的有效期决定。 |
| 211–213 | Ding | daily available | 极端拟合 QA、period fit、记录人工审阅。 |

最终字段保留交接中的 `period_start, period_end, ew, pp, tt, calibration_mpv, source, status, qa_flag, notes`，并建议增加 `constant_error, source_file, input_sha256, review_record`。所有 manual fixes 应以 `(day, ew, pp, tt)` 明确替换并保留旧值；不能把原始与修订数据简单拼接成重复行。

## 6. 解锁下一步所需文件

先提供：

1. **Day190.root**（或包含 `AdcEW0PP1TT1` 的 ROOT 文件）。仅看谱可先给 `ADCspectraDay190.pdf` 第 1 页；在远程宏布局中目标 tile 位于第 2 pad。实际 refit 需要 histogram 数据。
2. **实际 Run23 的 FindNmip.C / refit 宏**，以核对真实拟合模型、范围、初始化与约束。
3. **daily_observations_primary.csv**，用于完整 190–208、211–213 QA 和 sector 范围判断。

合并 candidate 时再需要 `period_references.csv`、`manual_refits.csv`、`badTiles.txt`、Yuno 的 reviewed daily 数据，以及最新 Ding period 文件。若可打包，可一次提供 `projects/2023_AuAu_200GeV/data/` 的文本表和相关 ROOT 谱。

## Sources

- 当前上传的 `DayFitsHistos.C`（本次只读）。
- 当前上传的 `ADCDelta_190_208.pdf`（24 页，已查看全页概览与关键页）；`ADCDelta_176_182.pdf` 已取得，未在本次据此宣布整个 period 通过 QA。
- [远程 notebook](https://github.com/cdxing/EpdCalibration/blob/apple-epd-ml/projects/2023_AuAu_200GeV/notebooks/01_problem_data_baseline.ipynb)，本次读取的 blob SHA `9decd08554ed8c686db5bce8ddce89cfafd8c8c6`。保存的输出是历史执行记录，不代表本次重跑。
- [远程 FindNmip.C](https://github.com/cdxing/EpdCalibration/blob/apple-epd-ml/FindNmip.C)，blob SHA `510dd1cec6b3c3088ad29399b42de75dc551cce7`。
- [远程 ingest_calibration.py](https://github.com/cdxing/EpdCalibration/blob/apple-epd-ml/projects/2023_AuAu_200GeV/src/ingest_calibration.py)，blob SHA `2d4b2028192961558ea79b60c741d109697ba97d`。
- 本轮用户提供的 Work Session Handoff。交接中的 period 值与状态在本文均按其原有证据等级处理。

### 169–175 QA: EW0 PP1 TT7 Day169 reviewed and retained
- Trigger: large_leave_one_out_pull = 6.09 for Day169.
- Day169 MPV: 127.793991 ± 0.988674.
- Neighbor tiles TT6/TT8 also shift upward on Day169, so this is not an isolated TT7 fit anomaly.
- Detector-wide median shift: 168→169 = +2.008%%; 169→170 = -0.150%%.
- Modern 169–175 weighted constant = 122.101379 ± 0.323078.
- cracz period reference = 122.101379, exactly matching the modern weighted constant to 6 decimals.
- Decision: retain Day169 observation; no refit, no exclusion, no segment split. Treat large leave-one-out pull as reviewed diagnostic only.

### 176–182 QA closed

- Final QA output: `data/derived/qa_176_182_v3`
- 742 tiles provisional.
- EW1 PP1 TT6 and EW1 PP2 TT10 are known dead tiles; all 176–182 observations excluded from the period fit with no carry-forward. Their `manual_review / insufficient_points` status is expected because `n_used=0`.
- Day179 EW0 PP6 TT2 automatic MPV `105.997108` was not supported by manual refit.
- Accepted replacement: `116.307190 +/- 1.289736`, fit start 60, FitStatus 0, chi2/ndf ~1.07.
- Fit-start checks at 50, 60, and 70 were stable; start 80 was unstable/degraded.
- Conclusion: 176–182 is scientifically closed; no unresolved blocking QA items remain.

### 183–189 QA closed

- Eloy period references are complete: 183–186 has 744 tiles and 188–189 has 744 tiles.
- Day187 is an intentional no-data gap; `timestampAndNotes.txt` explicitly states "No data for Day 187." No calibration is fabricated or carried across the gap.
- Day188 was merged with Day189 because of low statistics.
- EW1 PP1 TT6 and EW1 PP2 TT10 are known dead tiles and have final reference MPV 0.0 in both periods.
- Day184 EW1 PP3 TT6–9 strange-shape tiles are documented in the historical notes and appear in `RefitWork.txt`.
- Run 24186010 on Day186 contained single-value spikes in 34 documented tiles. These tiles are not listed in `RefitWork.txt`.
- Period-level cross-check against 188–189 gives median absolute change 0.457% for the 34 affected tiles, with 0/34 changing by more than 5%; no group-level evidence of contamination of the final 183–186 period constants was found.
- Conclusion: accept Eloy's 183–186 and 188–189 period references for candidate v1, retaining the documented Day187 gap and known-dead-tile semantics.

### Day211 pedestal-shift calibration semantics

For EPD reconstruction, `StEpdHitMaker` uses

    nMIP = (ADC + offset) / mip

where `ADC` is the raw value returned by `trg->epdADC(...)`.

Therefore, for a channel with a shifted pedestal:

- raw pedestal position ≈ +P
- DB `offset` ≈ -P
- DB `mip` is the pedestal-subtracted 1-MIP spacing, not the absolute raw-ADC position of the 1-MIP peak.

Example: Day211 EW1 PP11 TT19
- low-ADC peak ≈ 118.5
- next MIP-like peak ≈ 254.5
- peak separation ≈ 136 ADC
- candidate interpretation: `offset ≈ -118.5`, `mip ≈ 136`
- then `(254.5 - 118.5) / 136 ≈ 1 MIP`

The existing `FindNmipFix.C` fit assumes zero offset and models peaks approximately at
`mip, 2*mip, 3*mip, ...`. It therefore cannot correctly fit a spectrum with a large additive
pedestal shift. The manual raw-ADC fit result near 273 must NOT be accepted as the MIP constant.

Next action: validate this interpretation with an offset-aware fit / pedestal-subtracted spectrum
before assigning the final Day211 calibration constants.

#### Day211 EW1 PP11 TT19 pedestal-aware validation

The raw-ADC spectrum shows a shifted low-ADC structure near 118.5 ADC and the next MIP-like peak near 254.5 ADC.

STAR reconstruction uses:

    nMIP = (ADC + offset) / mip

with raw `ADC = trg->epdADC(...)`.

A validation histogram was constructed with the x axis shifted by 118.5 ADC while preserving all bin contents. The existing multi-MIP fitting model was then applied unchanged.

Fit-start stability:
- start 60: MPV = 141.375 +/- 0.686, chi2/NDF = 1332.25/616 = 2.16
- start 70: MPV = 140.679 +/- 0.591, chi2/NDF = 1083.42/606 = 1.79
- start 80: MPV = 140.804 +/- 0.535, chi2/NDF = 940.29/596 = 1.58, FitStatus = 0

Accepted validation result:
- candidate DB offset = -118.5 ADC
- candidate mip = 140.804016 +/- 0.534756 ADC

Artifacts:
- ADCspectraFix_Day211_EW1_PP11_TT19_PedSub_20260917.pdf
- NmipConstantsFix_Day211_EW1_PP11_TT19_PedSub_20260917.txt

This result must NOT yet be entered as a normal `replace_daily_observation` review because the current review schema carries only MIP and not DB offset. Using mip=140.804 with offset=0 would be incorrect.
