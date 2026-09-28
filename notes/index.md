# CRYPTO 2026 论文导读索引

按层级、再按 session 分组。L1 = 入门导读（核心定理 + 构造 + 简单证明），L2 = 深入解析（完整推导与既往成果比较）。

## L1 入门导读

### Quantum Cryptography I（2026-08-19）

- [Unclonable cryptography 的 multi-copy security：从 collusion-resistance 到"完全相同的多份拷贝"](L1/145-multi-copy-security-unclonable.md) — *Multi-Copy Security in Quantum Cryptography and More*，Alper Çakan, Vipul Goyal, Fuyuki Kitagawa, Ryo Nishimaki, Takashi Yamakawa。用 PRS + PRF 把"独立采样"提纯成同一个 pure state 的叠加，只靠 OWF 就把 collusion-resistance 升级成 multi-copy security：plain model 首个 public-key quantum coin、首个 multi-challenge/multi-copy UE。
- [少即是多：量子密码中的 copy complexity](L1/369-copy-complexity-less-is-more.md) — *Less is More: On Copy Complexity in Quantum Cryptography*，Prabhanjan Ananth, Eli Goldin。随机相位 + 随机 one-time pad 造出任意 mixed state 族的 purification，$t$ 份拷贝能被 $t$ 个 i.i.d. 样本模拟（误差 $t^2/2^{n_C}$）；由此 one-copy stretch PRSG $\Rightarrow$ $t$-copy PRSG，i.i.d. 安全 $\Rightarrow$ identical-copy 安全。
- [线性量子内存中的 uncloneable cryptography](L1/490-uncloneable-crypto-linear-quantum-memory.md) — *Uncloneable Cryptography in Linear Quantum Memory*，Andrew Huang, Omri Shmueli, Vinod Vaikuntanathan, Mark Zhandry。一把 $O(\lambda)$ qubit 的 coset state 用 $\lambda$ 轮相位-$\mathrm{i}$ Grover 完美地签整条 $\lambda$-bit 消息，claw-free permutation 的 folding CPF 再把归约里的向量长度从 $\lambda^2$ 压到 $2\lambda-1$：one-shot signature 达到平凡下界 $\Theta(\lambda)$。
- [Haar random oracle model 中的 unclonable encryption](L1/595-unclonable-encryption-haar-random-oracle.md) — *Unclonable Encryption in the Haar Random Oracle Model*，James Bartusek, Eli Goldin。密文 $X^kU|m,r_1,0,r_2\rangle$；新的 unitary reprogramming lemma（Haar $U$ 与在含已知点集的随机子空间上拆成 $U_1\oplus U_2$ 不可区分）把 QROM 里的 UE 通用搬进 QHROM——reusable UE 落入 microcrypt。
- [经典 oracle 下的 public-key quantum fire 与 key-fire](L1/709-public-key-quantum-fire-key-fire.md) — *Public-Key Quantum Fire and Key-Fire From Classical Oracles*，Alper Çakan, Vipul Goyal, Omri Shmueli。把 one-shot signature 的 keygen oracle 用它自己的签名"加密"：持有 purified OSS key 者可反复解锁从而克隆，只持 classical 串者受 incompressibility 限制；首个有证明的 quantum fire，no-cloning 与 no-telegraphing 的 classical-oracle 分离。

### Lattice Cryptanalysis II + Isogenies（2026-08-17）

- [Timed commitment 与 timed encryption：通用构造及其 isogeny 实例化](L1/199-timed-commitments-isogenies.md) — *Timed Commitments and Timed Encryption: Generic Constructions and Instantiations from Isogenies*，Mingjie Chen, Jonas Meers。"解唯一、实例可由知情者快速采样"的 VDF + 对称加密 + random oracle 给出 commit 快、可验证打开、完美 binding 的 NITC；用 Deuring VRF 改造的 DeuringVDF 实例化成首个后量子 NITC。
- [带 level structure 的 superspecial isogeny digraph 的 expander 性质](L1/207-superspecial-isogeny-digraph-expander.md) — *Expander properties of superspecial isogeny digraphs with level structure*，Thomas Decru, Krijn Reijnders。高维 isogeny walk 的正确图是带 level structure 的有向图 $\mathcal{G}_g(p,\ell)$；由 automorphism group 在 level structure 上作用的完整分类，得到 $g=1$ 与 $g=2$（$\ell\in\{2,3\}$）weakly Ramanujan、再往上不是的结论。

### Foundations II（2026-08-20）

- [超越二次：用 quartic character 解锁伪随机性](L1/444-quartic-character-pseudorandomness.md) — *Beyond Quadratic: Unlocking Pseudorandomness with Quartic Character*，Mriganka Dey, Sampa Dey, Sampurna Pal, Subhabrata Samajder, Rana Barua。把 Legendre symbol 换成 $\mathbb{Z}[i]$ 上的 quartic character，每次求值出 2 bit，一条归约链证明它在同一 QRA 下是 weak PRF，关闭 Damgård 1988 的最后一问。

### Post-Quantum Cryptography（2026-08-18）

- [译码失败率有界的高效 QC-MDPC 密码系统](L1/502-qcmdpc-bounded-dfr.md) — *Efficient QC-MDPC Cryptosystems with Bounded Decoding Failure Rate*，Alessandro Annechini, Alessandro Barenghi, Gerardo Pelosi, Simone Perriello。给真实部署的三轮 parallel decoder 建出首个 closed-form DFR 模型，新发现的 half codeword 失败源解释了 sequential proxy 估计 parallel decoder 为何不可靠。

## L2 深入解析

### Lattice Cryptanalysis I（2026-08-17）

- [Learning with Alternating Moduli、合数模上的 Arora-Ge 与 weak PRF](L2/10-learning-with-alternating-moduli.md) — *Learning with Alternating Moduli, Arora-Ge over Composite Moduli, and Weak PRFs*，Yilei Chen, Liheng Ji, Wenjie Li。把 BIPSW 型 weak PRF 的 heuristic 换成 well-formed 的常数模 LAM/LWR 假设，并完整刻画合数模 Arora-Ge 的攻击边界。
- [从符号泄露恢复 lattice signature 密钥：Halfspace Learning](L2/306-halfspace-learning-key-recovery.md) — *Halfspace Learning for Lattice Signature Key Recovery from Signs*，Marcus Brinkmann, Nicolai Kraus, Alexander May。只泄露 sign 这一最粗粒度的信息，HAWK/Falcon 在几十到几百个签名内、ML-DSA 在 sign 模型下首次被完整恢复密钥，且不用 lattice reduction。
- [小心 ring！LWE 与 MLWE 的 concrete hardness 差距](L2/865-lwe-mlwe-hardness-gap.md) — *Careful with the Ring! Concrete Hardness Gaps Between LWE and MLWE*，Jianhua Hou, Haodong Jiang, Tabitha Ogilvie。ring 的 isometry（rotation）在 sparse secret 的 hybrid 攻击里带来免费的猜测增益，把 ring 结构当免费效率换算会高估安全性 10–15 bit。

### Lattice Cryptanalysis II + Isogenies（2026-08-17）

- [定与不定 Lattice Isomorphism Problem 的密码分析及其在 DEFI 上的应用](L2/187-definite-indefinite-lip-defi.md) — *Cryptanalysis of Definite and Indefinite Lattice Isomorphism Problems With Applications to DEFI*，Markus Kirschmer, Cong Ling, Ali Sadreddin。indefinite form 的 genus 塌缩成单 class、再归约到可解的 norm equation，rank $\ge3$ 的 DEFI 被破。
- [借 Irreducible Decomposition 探究 Lattice Isomorphism Problem 的复杂度](L2/235-lip-complexity-irreducible-decomposition.md) — *Exploiting the complexity of the Lattice Isomorphism Problem via Irreducible Decomposition*，Kaijie Jiang, Yinchen Liu。用 irreducible decomposition 建立 LIP 的 search/decision/counting 变体之间的归约，说明 LIP 类方案不能指望 worst-case NP-hardness。

### Lattice-Based Cryptography（2026-08-17）

- [不用 discrete Gaussian 的 preimage sampleable functions](L2/553-preimage-sampleable-without-gaussians.md) — *Preimage sampleable function families without discrete Gaussians*，Eamonn W. Postlethwaite, Filip Trenkić。用均匀 bits 与 randomised rounding 得到最大 entropy 的均匀 preimage、全链条可证明的 PSF，代价是 $\beta$ 明显差于 Gaussian 基线。
