# 小心 ring！LWE 与 MLWE 的 concrete hardness 差距

> **Careful with the Ring! Concrete Hardness Gaps Between LWE and MLWE**
> Jianhua Hou, Haodong Jiang, Tabitha Ogilvie
> CRYPTO 2026 · Lattice Cryptanalysis I (2026-08-17) · **L2 深入解析**
> [ePrint 2026/279](https://eprint.iacr.org/2026/279) · [Slides](https://iacr.org/submit/files/slides/2026/crypto/crypto2026/865/865_slides.pptx)

## §1 背景与问题设定

估计 MLWE/RLWE 的 concrete security 时，业界的普遍做法是把它翻译成"等价的" LWE 实例再跑 estimator——隐含假设是**代数结构只买效率、不送攻击者任何东西**。这个假设写进了 HE 标准（论文引 Bossuat et al., CiC 2024："it is not known how to cryptanalytically exploit the algebraic structures of RLWE and GLWE"），也支撑着大量已部署参数。本文证明：**对现实参数它不成立**——在 power-of-two cyclotomic ring 中，攻击者可以利用对称性得到严格强于对应 LWE 攻击的 hybrid attack。

设定与记号：$R_q=\mathbb{Z}_q[X]/(X^n+1)$（$n$ 为 2 的幂，ring rank），module rank $k$，$m$ 个 MLWE sample 叠成 $\mathbf{b}=\mathbf{A}\mathbf{s}+\mathbf{e}$（$\mathbf{A}\in R_q^{m\times k}$）；flatten 到整数侧记 $N:=kn$、$M:=mn$，$\mathrm{coeff}(x)$ 为 ring 元素的系数向量，$\mathbf{A}_{\mathrm{coeff}}\in\mathbb{Z}_q^{M\times N}$ 满足 $(\mathbf{A}x)_{\mathrm{coeff}}=\mathbf{A}_{\mathrm{coeff}}(x)_{\mathrm{coeff}}$。所有 hybrid attack 共享一个代价结构（$S$ 为 guess 集合；本文把论文的运行时间记号统一写作代价 $C_\cdot$，以免与其他符号冲突）：

$$
\text{总代价}\;=\;\frac{1}{\Pr[\mathbf{s}\in S]}\Big(C_{\mathrm{init}}+|S|\cdot C_{\mathrm{check}}\Big),
$$

昂贵的 $C_{\mathrm{init}}$（lattice reduction / sieve）只依赖 $\mathbf{A}$ 的固定部分,可在所有 guess 间摊销。**本文的全部问题就是：ring 结构能否扩大"与同一份预处理兼容"的 guess 家族，从而改善 $\Pr[\mathbf{s}\in S]$ vs $|S|$ 的权衡？**

## §2 此前的成果

**Primal hybrid（LWE 版）。** 把 $\mathbf{A}$ 的列拆成 guess 部分 $\mathbf{A}_\zeta$（$\zeta$ 列）与 reduction 部分：对后者建格

$$
\Lambda\Big(\begin{bmatrix}q\mathbf{I}_M&\mathbf{A}_{N-\zeta}\\ \mathbf{0}&\xi\mathbf{I}_{N-\zeta}\end{bmatrix}\Big),\qquad \xi=\sigma_e/\sigma_s,
$$

BKZ$_\beta$ 归约一次（$C_{\mathrm{init}}$）；对每个 guess $\mathbf{s}_g$ 用 Babai nearest plane 解码 target $\mathbf{b}-\mathbf{A}_\zeta\mathbf{s}_g$（$C_{\mathrm{check}}$），成功概率 $p_{\mathrm{NP}}\cdot\Pr[\mathbf{s}_\zeta\in S]$；meet-in-the-middle 启发式把 NP 调用降到 $\sqrt{|S|}$。sparse secret（HE 场景，ternary、Hamming weight 低至 32）下这是最强攻击。**关键限制：lattice 固定后，必须 guess 的恰是那 $\zeta$ 个固定坐标。**

**Code-based dual hybrid（Carrier–Meyer-Hilfiger–Shen–Tillich, CRYPTO 2025）**——Kyber/ML-KEM 最优公开估计的来源。坐标三分为 $\mathrm{lat}/\mathrm{enu}/\mathrm{fft}$：对 $\mathbf{A}_{\mathrm{lat}}$ 做一次 sieve 得短向量集（固定、昂贵）；每 trial 猜 $\mathbf{s}_{\mathrm{enu}}=\mathbf{0}$，用 polar code 把 $\mathbf{s}_{\mathrm{fft}}$ 压到可枚举维度、FFT 打分 $V$，$V\ge T$ 即接受。成功概率

$$
\eta\cdot P_{\mathrm{good}}\cdot(1-\mu)-R\cdot q^{k_{\mathrm{fft}}}\cdot P_{\mathrm{wrong}},\qquad \eta=\Pr[\exists\,i\in[R]:\mathbf{s}_{\mathrm{enu}}=\mathbf{0}],
$$

（$R$ 为 trial 数、$T$ 为接受阈值、$1-\mu$ 为后续求解成功率）。同样地，zero-guess 只能在固定的 $[N]\setminus I_{\mathrm{lat}}$ 里选。

**已有的结构利用尝试。** NTRU zero-forcing：secret 的每个 rotation 都是格中短向量，猜任一 rotation 的零集即可——但 NTRU 是齐次问题，猜错就得**从头再来**，昂贵的 reduction 无法摊销，不构成 hybrid；Cool & Cruel（sparse RLWE）：依赖 reduced basis 出现特定 "Z-shape"，且 $q$ 大时 Z-shape 消失；module-BKZ 线（非 power-of-two ring 的 blocksize 次线性增益）：另一种攻击风格。**power-of-two ring 里、与标准 hybrid 框架兼容的结构增益，此前是空白。**

## §3 本文的算法

> **核心定义（coefficient isometry）**：$r\in R$ 是 coefficient isometry，若存在 signed permutation matrix $\boldsymbol{\Pi}_r$ 使
> $$\mathrm{coeff}(rx)=\boldsymbol{\Pi}_r\,\mathrm{coeff}(x)\qquad\forall x\in R.$$

机制一行推完：MLWE sample 满足 $b=\langle\mathbf{a},\mathbf{s}\rangle+e$，则对任意 $r$，双线性给出

$$
rb=\langle\mathbf{a},r\mathbf{s}\rangle+re .
$$

若 $r$ 是 isometry 且 secret/error 分布对 isometry 不变（引理 10：坐标 iid 中心对称分布、或固定 Hamming weight 的中心对称集合上均匀——正好覆盖 discrete Gaussian error + ternary/binomial secret），则 $(\mathbf{a},rb)$ 是**同参数**的 MLWE sample：同一个 $\mathbf{a}$、被 signed-permute 过的 secret $r\mathbf{s}$。于是**同一份昂贵预处理可以攻击一整族 secret** $\{r\mathbf{s}\}_{r\in\mathcal{T}}$（$\mathcal{T}$ 为 isometry 集合）。

两个算法都只改 guess 层：

- **IsometricPrimalHybrid**：guess 变为二元组 $(r,\mathbf{s}_g)$，target 换成 $(rb)_{\mathrm{coeff}}-\mathbf{A}_\zeta\mathbf{s}_g$，其余（BKZ 基、NP 调用）与 LWE 版逐字相同；命中后逆置换恢复 $\mathbf{s}$。
- **IsometricDualHybrid**：每个 trial 额外均匀采一个 $r\leftarrow\mathcal{T}$，检验事件从 $\mathbf{s}_{\mathrm{enu}}=\mathbf{0}$ 换成 $(r\mathbf{s})_{\mathrm{enu}}=\mathbf{0}$，target 换成 $(rb)_{\mathrm{coeff}}$。

Power-of-two 实例化（RotPrimalHybrid / RotDualHybrid）：$\mathcal{T}=\{X^j:0\le j<n\}$，即全部 negacyclic rotation。

## §4 为什么能 work（推导）

### 4.1 为什么每个 monomial 都是 isometry（引理 16，简单代数）

在 $R_q$ 中 $X^n\equiv-1$，故对 $f=\sum_{i=0}^{n-1}f_iX^i$：

$$
X\cdot f\;\equiv\;-f_{n-1}+\sum_{i=0}^{n-2}f_iX^{i+1},
\qquad
\boldsymbol{\Pi}=\begin{bmatrix}0&\cdots&0&-1\\ 1&&&0\\ &\ddots&&\vdots\\ &&1&0\end{bmatrix},
$$

即 $\mathrm{coeff}(Xf)=\boldsymbol{\Pi}\,\mathrm{coeff}(f)$，negacyclic rotation。signed permutation 对乘法封闭，故 $X^j\leftrightarrow\boldsymbol{\Pi}^j$ 全是 isometry。$\square$ 分布不变性同样直接：坐标置换 + 符号翻转正是"iid 中心对称"与"固定权重对称集"这两类分布的对称群元素。

### 4.2 为什么预处理真的兼容：把增益隔离到组合层（引理 11）

这是全文的结构核心。flatten 后 $(rb)_{\mathrm{coeff}}=\mathbf{A}_{\mathrm{coeff}}(r\mathbf{s})_{\mathrm{coeff}}+(re)_{\mathrm{coeff}}$；按列拆分并减去 guess，得在商群 $\mathbb{Z}^{M+N-\zeta}/\Lambda_q(\mathbf{A}_{N-\zeta})$ 中

$$
\begin{bmatrix}(rb)_{\mathrm{coeff}}-\mathbf{A}_\zeta(r\mathbf{s})_\zeta\\ \mathbf{0}\end{bmatrix}
\;\equiv\;
\begin{bmatrix}(re)_{\mathrm{coeff}}\\ -\xi\,(r\mathbf{s})_{N-\zeta}\end{bmatrix}
\pmod{\Lambda_q(\mathbf{A}_{N-\zeta})},
\qquad
\begin{bmatrix}(re)_{\mathrm{coeff}}\\ -\xi(r\mathbf{s})_{N-\zeta}\end{bmatrix}
\overset{d}{=}
\begin{bmatrix}(e)_{\mathrm{coeff}}\\ -\xi(\mathbf{s})_{N-\zeta}\end{bmatrix}.
$$

左式说明"换 target"仍是同一个格上的 BDD 实例；右式（由分布不变性）说明 displacement 的**分布**与 $r=1$ 时逐点相同——于是 nearest plane 的成功率 $p_{\mathrm{NP}}$ 与 $r$ 无关，MitM 概率同理，dual 侧的 $P_{\mathrm{good}},P_{\mathrm{wrong}}$（引理 21/22）也逐字继承。**结论：引入 isometry 后，全部解析部分（reduction、decoding、distinguishing）原封不动，增益被干净地隔离在一个组合量里——primal 是 $\Pr[\mathbf{s}\in S]$，dual 是 $\eta$。**这就是为什么安全估计可以直接复用现有 estimator，只换命中概率公式。

反面印证（Remark 3）：想在纯 LWE 上复制此攻击，需要一个 order-$n$ 的 signed permutation 与均匀随机的 $\mathbf{A}$ 交换——要求 $\mathbf{A}$ 在某行列同时置换下不变（至多差号），对随机矩阵不成立。**这是 MLWE 与 LWE 之间真实的、可量化的结构差异。**

### 4.3 组合增益有多大：命中概率

**Primal（sparse secret）。** 标准 guess 集 $S_{\mathrm{plain}}(h_g)$ = 权重 $\le h_g$ 的段，命中率 $p(h_g)=\Pr[\mathbf{s}_\zeta\in S_{\mathrm{plain}}]$。加 rotation 后 $S_{\mathrm{rot}}=\{X^j\}\times S_{\mathrm{plain}}$，在"各 rotation 上的权重独立"启发式（NTRU zero-forcing 启发式的推广）下

$$
|S_{\mathrm{rot}}|=n\,|S_{\mathrm{plain}}|,\qquad
\Pr[\mathbf{s}\in S_{\mathrm{rot}}]\approx 1-(1-p(h_g))^{n}\approx n\,p(h_g)\quad(\text{当 }np\ll1),
$$

即花 $n$ 倍 guess 换约 $n$ 倍命中率——由于总代价里 $\Pr^{-1}$ 与 $C_{\mathrm{init}}$ 相乘而 $|S|$ 只进 guessing 相，当 reduction 主导时净赚接近 $\log n$ bits。仿真验证（论文 Fig. 1，10000 trials）：启发式与实测吻合；$\log n=14$ 的例子里，同样达到 $2^{-7.9}$ 命中率，带 rotation 需 $2^{27}$ 个 guess，不带需 $2^{78.7}$ 个。

**Dual（Kyber 型 iid secret）。** 原版命中事件要求 $\mathbf{s}$ 在 $[N]\setminus I_{\mathrm{lat}}$ 内的某 $n_{\mathrm{enu}}$ 个坐标全零；带 rotation 后零模式可以取遍**整个** $N$ 维（包括 lat 部分对应的位置被转进来）。设 $p_0=\Pr[\text{单坐标}=0]$、$t$ 为 secret 中零的个数，条件独立启发式给出（$N'=N-n_{\mathrm{lat}}$）：

$$
\eta_{\mathrm{plain}}\approx1-\sum_{t}\Big(1-\tfrac{\binom{t}{n_{\mathrm{enu}}}}{\binom{N'}{n_{\mathrm{enu}}}}\Big)^{R}\Pr[t\text{ zeros in }N'],
\qquad
\eta_{\mathrm{rot}}\approx1-\sum_{t}\Big(1-\tfrac{\binom{t}{n_{\mathrm{enu}}}}{\binom{N}{n_{\mathrm{enu}}}}\Big)^{R}\Pr[t\text{ zeros in }N],
$$

后者分母虽大（$\binom{N}{n_{\mathrm{enu}}}$），但可命中的零模式家族也大得多，仿真（论文 Fig. 2，Kyber512/768/1024 参数）显示 rotation 版在相同 $R$ 下 $\eta$ 一致更高，且两个启发式都与实测吻合。

### 4.4 MitM 保持

primal 的 $\sqrt{|S|}$ 加速在 $S=\mathcal{T}\times S_{\mathrm{plain}}$ 下仍成立，代价是改用**不平衡**分解启发式：$S_{\mathrm{plain}}=S_1+S_2$ 且 $|\mathcal{T}||S_1|\approx|S_2|$，NP 调用数 $|\mathcal{T}||S_1|+|S_2|\approx\sqrt{|S|}$。作者报告两种启发式（平衡/不平衡）只差几 bits，estimator 中留作开关。

## §5 提升了多少

**Sparse RLWE（primal，HE 场景）**——用扩展的 Lattice Estimator（MATZOV cost model，与 HE 标准化流程一致）重估标准化提案参数（论文 Table 1 节选，bits）：

| $\log n$ | $h$ | LWE 估计 | RLWE 估计（本文） | gap |
|---|---|---|---|---|
| 14 | 64 | 141.3 | 130.5 | 10.8 |
| 16 | 64 | 142.5 | 129.7 | 12.8 |
| 17 | 64 | 139.8 | 126.0 | 13.8 |
| 16 | 128 | 134.5 | 120.5 | 14.0 |
| 17 | 128 | 136.4 | 121.6 | 14.8 |

gap 随稀疏度增大，最高约 **15 bits**；大量目标 128-bit 的参数集被拉到线下。作者还普查了近一年顶会 HE 论文的 sparse 参数：除一篇外，每篇都至少有一个参数集跌破其声称的安全级别。

**Kyber/ML-KEM（dual）**：在 Carrier et al. 的三种 cost model（Core-SVP / CC / CN）下全面重估，rotation 带来一致的 **2–3 bit** 下降（如 Kyber512 攻击代价 C0 118.8 / CC 137.1 / CN 132.2 bits），且这纯粹来自 $\eta$ 的提升、distinguishing 分析未动。

诚实的边界（作者自己的 T&C）：增益只在 **hybrid 是最优攻击**时转化为 MLWE–LWE gap（uniform secret/error 下不预期有优势）；所有攻击仍是指数时间——结论不是"ring 让问题变容易"，而是"**把 ring 结构当免费效率的换算在 sparse 情形会高估安全性 10–15 bits**"。

## §6 局限与延伸阅读

只实例化了 power-of-two cyclotomics（其他 ring 中 isometry 可能只有平凡的）；把各 rotation 段建模为完全独立会连到 "guess one out of many keys" 枚举文献，留作未来工作；对标准化的直接含义：HE 的 sparse 参数表需要按含 isometry 的 estimator 重算。

- 本文：[ePrint 2026/279](https://eprint.iacr.org/2026/279)
- Carrier–Meyer-Hilfiger–Shen–Tillich, *Assessing the impact of a variant of MATZOV's dual attack on Kyber*, CRYPTO 2025——被扩展的 dual hybrid 基线
- NTRU zero-forcing 技术与 Cool & Cruel attack（sparse RLWE 攻击线，见本文 §1.5 的引文）——两种被本文区分并超越的既有结构利用方式
