# Learning with Alternating Moduli、合数模上的 Arora-Ge 与 weak PRF

> **Learning with Alternating Moduli, Arora-Ge over Composite Moduli, and Weak PRFs**
> Yilei Chen, Liheng Ji, Wenjie Li (IIIS Tsinghua & Shanghai Qi Zhi Institute)
> CRYPTO 2026 · Lattice Cryptanalysis I (2026-08-17) · **L2 深入解析**
> [ePrint 2025/968](https://eprint.iacr.org/2025/968) · [Slides](https://iacr.org/submit/files/slides/2026/crypto/crypto2026/10/10_slides.pptx)

## §1 背景与问题设定

**电路类 $\mathrm{NC}^0[q]$**：常数深度、poly size 电路，门为 2-fan-in AND/OR、NOT，与 **unbounded-fan-in $\mathrm{MOD}_q$**（输入中 1 的个数是 $q$ 的倍数则输出 0，否则 1）。这个类为 MPC 量身定做：加法（$\mathrm{MOD}_q$）本地免费、乘法（2-fan-in）才要通信。经典障碍：$\mathrm{AC}^0$ 中 weak PRF 至多 quasipolynomial 安全（Linial–Mansour–Nisan），所以 subexponential 安全的 wPRF 必须住在它之外——最小可行的类在哪里，是密码、复杂度与学习论共同的问题。

**LAM（本文形式化的新假设）**：$q_1>q_2\ge2$，$\gcd(q_1,q_2)=1$，secret $\mathbf{s}\in\mathbb{Z}_{q_1}^n$，

$$
\text{sample}=\big(\mathbf{a},\ (\langle\mathbf{s},\mathbf{a}\rangle\bmod q_1)\bmod q_2\big),\qquad \mathbf{a}\leftarrow\mathbb{Z}_{q_1}^n,
$$

search 版求 $\mathbf{s}$，decisional 版与 $(U(\mathbb{Z}_{q_1}^n),\,U(\mathbb{Z}_{q_1})\bmod q_2)$ 区分。为什么必须互素：若 $c\mid\gcd(q_1,q_2)$，则 sample 模 $c$ 后是**无噪声**线性方程 $\langle\mathbf{s},\mathbf{a}\rangle\bmod c$，Gaussian elimination 直接学出 $\mathbf{s}\bmod c$。LWR 是它的近亲（把外层 mod 换成 rounding $\lfloor(q_2/q_1)\cdot\rceil$）。本文的三个问题：LAM 能否落在 LWE 上？常数模下 Arora-Ge 算法对合数模 LWE/LAM 的杀伤力如何？$\mathrm{NC}^0[q]$ 里 wPRF 的存在边界在哪？

## §2 此前的成果

**"Dark matter" wPRF（Boneh–Ishai–Passelègue–Sahai–Wu, TCC 2018）**：alternating moduli 技巧的开山之作——key 为 $\mathbf{A}\in\mathbb{Z}_2^{m\times n}$，

$$
F_{\mathbf{A}}(\mathbf{x})=\mathrm{map}(\mathbf{A}\mathbf{x}\bmod 2),\qquad \mathrm{map}(\mathbf{y})=\sum_i y_i\bmod 3,
$$

住在 $\mathrm{NC}^0[2,3]$、MPC-friendly，是该类中唯一已知的 subexponential 安全候选路线。七年间有多个后续构造与密码分析尝试，所有已知攻击都是指数时间——但它的安全性**从未**归约到任何 well-formed assumption，只能假设"构造本身安全"。

**Arora-Ge（ICALP 2011）**：error support 为常数大小 $[d]$ 时多项式时间解 LWE——把每个 sample 变成关于 secret 的多项式方程（error 只有 $d$ 种取值 ⟹ $d$ 次多项式恒零），线性化后解方程组。但其分析靠 **Schwartz-Zippel lemma，只对素数域成立**；合数模下该算法的行为此前没有发表过的分析。这两条线在本文交汇：BIPSW 构造的安全性分析，恰恰需要搞清楚常数合数模上的代数攻击边界。

## §3 本文的算法与结果

五项结果，两条主线（归约线 + 攻击线）：

**(i) 大模数下 LAM ⇔ LWE**（定理 22，informal）：若 $q_1>2Bmq_2$（$B$ 为 error bound），则 search-LAM 的 $\epsilon$-solver 给出 search-LWE$_{n,m,q_1,D_B}$ 的 $\Omega(\epsilon^2)$-solver；配合 search/decision 及反向归约，该参数域内两者互相等价（技巧承自 LWR–LWE 归约,Banerjee–Peikert–Rosen）。**代价：要求 $q_1\ge\mathrm{poly}(n)$**——常数模数下归约全部失效，只能靠攻击刻画。

**(ii) 合数模 Arora-Ge**（引理 31）：$q=p^\kappa$、error 分布支撑 $[d]$ 且每点概率 $\ge\sigma$、$N=\binom{n+d}{n}$、$m>10N\log q/\sigma$ 时，Arora-Ge 以压倒性概率输出

$$
\mathbf{s}\ \bmod\ \frac{q}{\gcd(d!,\,q)} .
$$

三种命运一目了然：$\gcd(d!,q)=1$（含素数模）→ 全恢复；$\gcd=q$（即 $d!\equiv0\bmod q$）→ 多项式恒零、一无所获；中间情形 → 部分恢复。顺带把素数情形的 sample 数改进 $q/(q-d)$ 倍（修正原论文对 Schwartz-Zippel 下界的一处放松）。

**(iii) 递归 Arora-Ge + CRT**（定理 30）：只要 $d!\bmod q\ne0$，对一般合数 $q=p_1^{\kappa_1}\cdots p_t^{\kappa_t}$ 都能 poly 时间**全恢复** $\mathbf{s}$。对 LAM/LWR 的含义：两者都可视作模 $q_1$、error support $[\lfloor q_1/q_2\rfloor]$ 的 LWE，故 **$\lfloor q_1/q_2\rfloor!\bmod q_1\ne0$ 的参数全被杀死**（论文 Table 1：如 $q_1=24$ 时 LAM 最大安全 $q_2=5$）。

**(iv) $\mathrm{NC}^0[p]$ 中不存在 wPRF**（$p$ 素数）：见 §4.3。于是候选构造的内层模必须**非** prime power。

**(v) 新候选 wPRF**：对互素常数 $q_1,q_2$、素数 $p\mid q_1$，key $\mathbf{S}=(\mathbf{s}_1,\dots,\mathbf{s}_\ell)\in\mathbb{Z}_{q_1}^{n\times\ell}$（$\ell=O(n)$ 份求和杀 bias）：

$$
g_{\mathbf{S}}(\mathbf{x})=\Big(\sum_{i=1}^{\ell}\big((\langle\mathbf{s}_i,\mathbf{x}\rangle\bmod q_1)\bmod q_2\big)\Big)\bmod p .
$$

具体实例 $q_1=24,\ q_2=5,\ p=2$：住在 $\mathrm{NC}^0[2,3]$（深度 2–3），安全性基于**常数模 LAM 这一 well-formed assumption**。LWR 版本 $L_{\mathbf{S}}$ 类似；当 $q_2\mid q_1$ 时 LWR 无 bias，单份 $K_{\mathbf{s}}$ 即可。有趣的对照：BIPSW 的 $F_{\mathbf{A}}$ 恰是 $g_{\mathbf{S}}$ 取 $q_1=6,q_2=2,p=3$ 的形态——但 $\gcd(6,2)=2$ 违反 LAM 的互素要求，**原始 dark-matter 构造仍不被任何假设捕获**。

## §4 为什么能 work（推导）

### 4.1 Arora-Ge 的骨架与"$d!$ 现象"

对每个 sample $(a_i,b_i)$ 构造

$$
P_i(z)=\prod_{j=0}^{d-1}\big(b_i-a_i z-j\big),
$$

代入 $z=\mathbf{s}$ 得 $P_i(\mathbf{s})=\prod_j(e_i-j)=0$（$e_i\in[d]$ 必中其一）——**completeness 免费**。把 $z^j$ 线性化为新变量后解模 $q$ 线性方程组即可。难点全在 soundness：错误解为什么撑不过所有方程？素数域靠 Schwartz-Zippel；合数模上作者换成一个**直接的线性代数论证**，其核心可以在论文自带的玩具例（$n=1,\ q=16,\ d=4$）里完整看见：

换元 $\tilde y_j:=(s-z)^j$ 后，方程组的系数把 $e_i\in\{0,1,2,3\}$ 逐个代入、写成矩阵，再做 Gaussian elimination，得到上三角形

$$
\begin{bmatrix}24&0&0&0\\ 12&12&0&0\\ 8&12&4&0\\ 6&11&6&1\end{bmatrix}
\begin{bmatrix}a_i\tilde y_1\\ a_i^2\tilde y_2\\ a_i^3\tilde y_3\\ a_i^4\tilde y_4\end{bmatrix}
\not\equiv\mathbf{0}\pmod{16}\ \text{（需证其概率下界）}.
$$

**关键就是左上角的 $24=d!$**：第一行读作 $24\,a_i\tilde y_1\equiv 8\,a_i\tilde y_1\pmod{16}$，当 $a_i$ 为奇数（概率 $1/2$）时，它非零 $\iff\tilde y_1$ 为奇。也就是说方程组能且只能把 $\tilde y_1=s-z$ 钉死到奇偶——即恢复 $\mathbf{s}\bmod 2=\mathbf{s}\bmod\frac{16}{\gcd(24,16)}$。一般情形同理：消元后主对角首元恒为 $d!$，**$d!$ 在 $\mathbb{Z}_q$ 中的可逆程度 $=$ Arora-Ge 能钉死 secret 的程度**，引理 31 的 $\bmod\,q/\gcd(d!,q)$ 由此而来。这个论证完全绕开 Schwartz-Zippel，还顺手收紧了素数情形的 sample 复杂度。

### 4.2 递归 + CRT：把"部分"变成"全部"

拿到 secret 的低位信息后（以玩具例即 $\mathbf{s}\bmod2$）：令 $\mathbf{s}'=(\mathbf{s}-(\mathbf{s}\bmod 2))/2$（以玩具例为例），把原实例改写成 secret 为 $\mathbf{s}'$、模数 $q'=8$、error bound $d'=2$ 的新 LWE 实例——**模数与 error support 同时缩小**，对新实例再跑一遍 Arora-Ge；几轮后 error 被完全去除，剩下的用 Gaussian elimination 收尾。不同素数幂分量并行处理后由 CRT 拼回。终止条件恰是 $d!\bmod q\ne0$：一旦 $d!\equiv0$，第一轮就已经零信息，递归无从启动——这条分界线同时就是 §3(v) 候选参数的**安全设计准则**（选 $\lfloor q_1/q_2\rfloor!\equiv0\bmod q_1$）。

### 4.3 为什么 $\mathrm{NC}^0[p]$ 里没有 wPRF（$p$ 素数）

两步。**第一步（表示）**：$\mathrm{MOD}_p$ 门可写成 $\mathbb{Z}_p$ 上的多项式 $1-\big(\sum_i x_i\big)^{p-1}$（Fermat 小定理：和 $\equiv0$ 时该幂为 0，否则为 1）——次数只乘 $p-1$；AND/OR 是 2-fan-in、次数只乘 2；常数深度复合下总次数 $O(1)$。故 $\mathrm{NC}^0[p]$ 的任何函数都是 $\mathbb{Z}_p$ 上**常数次数多项式**。**第二步（区分）**：常数次数的 $n$ 元多项式活在维度 $n^{O(1)}$ 的单项式空间里——把每个查询点的单项式向量拼成矩阵，真 wPRF 的输出必须落在该矩阵的列空间（线性代数可检验），随机函数以压倒性概率不满足。多项式时间区分器即成。$\square$ 有意思的反面（定理 43）：$q$ 含两个不同素因子时，某些 $\mathrm{NC}^0[q]$ 电路对**任何**模数 $N$ 都不能用低次多项式计算——这正是 alternating moduli（两个素数）躲过此攻击的结构原因。

### 4.4 剩余攻击面与 bias

LAM 分布有 bias（$(U(\mathbb{Z}_{q_1})\bmod q_2)$ 并非均匀），BKW 类算法给出 $2^{O(n/\log n)}$ 攻击——这是常数模 LAM 假设的真实上限；构造层面 $g_{\mathbf{S}}$ 对 $\ell=O(n)$ 份求和使 bias 指数小，BKW 不再适用于 wPRF 本身。线性密码分析同样被求和抵挡。

## §5 提升了多少

与既有低深度 wPRF 候选的对照（论文 Table 2）：

| 候选 | 电路类 | 猜想安全性 | 假设 |
|---|---|---|---|
| BIPSW18 (dark matter) | $\mathrm{NC}^0[p_1,p_2]$ | $2^{O(n)}$ | **heuristic** |
| BCG+20 | $\mathrm{AC}^0[2]$ (XNF) | $2^{\tilde O(n^{1/3})}$ | Variable-Density LPN |
| BCG+21 | $\mathrm{AC}^0[2]$ (sparse $\mathbb{F}_2$ poly) | $2^{\tilde O(\sqrt n)}$ | heuristic |
| **本文 $g_{\mathbf{S}}$ / $L_{\mathbf{S}},K_{\mathbf{s}}$** | $\mathrm{NC}^0[p_1,p_2]$ | $2^{O(n/\log n)}$ | **常数模 LAM / LWR** |

同一电路类、同样 MPC-friendly（深度 2–3），换来的是**把 heuristic 换成 well-formed assumption**；代价是标称安全从 $2^{O(n)}$ 降到 $2^{O(n/\log n)}$——且这是诚实计法：已知对构造本身的最好攻击是 $2^{O(n)}$，但底层假设受 BKW $2^{O(n/\log n)}$ 制约，作者按假设的短板填表。攻击侧的收获独立成立：合数模 Arora-Ge 的完整刻画（含 Table 1 的参数生死簿）与 $\mathrm{NC}^0[p]$ 不可能性，为这一带的所有构造划出了代数攻击的精确边界。

## §6 局限与延伸阅读

常数模 LAM 的 hardness 没有归约支撑，是纯粹的新假设（尽管比"假设构造安全"干净得多），需要更多密码分析检验；原始 BIPSW 实例（$\gcd=2$）仍游离在假设体系之外；大模数等价性要求 $q_1>2Bmq_2$，中间参数带的地位未知。

- 本文：[ePrint 2025/968](https://eprint.iacr.org/2025/968)
- Boneh–Ishai–Passelègue–Sahai–Wu, *Exploring crypto dark matter*, TCC 2018——被本文"收编进假设体系"的构造源头
- Arora–Ge, *New algorithms for learning in presence of errors*, ICALP 2011——被推广到合数模的经典算法
