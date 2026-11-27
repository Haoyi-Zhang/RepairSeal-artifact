# RepairSeal：本轮修订的 signed 接收器

`receiver.py` 是本轮加固实现的统一命令行入口。它只从 `current/src/` 加载接收器模块，并在输出中记录请求身份、修订标识和实现文件的 SHA-256。请通过这个入口使用修订实现。

## 环境与安装

本轮实际验证环境为 **Linux、CPython 3.12.14、pycparser 3.0**。依赖固定在 [requirements.txt](requirements.txt)。CLI 不调用 C 编译器；源码经过接纳检查后，按声明的语义解释。

以下命令从 `artifact/` 执行，虚拟环境放在项目外：

```sh
python3 -m venv ../../repairseal-current-venv
. ../../repairseal-current-venv/bin/activate
python -m pip install -r current/requirements.txt
python -B current/receiver.py --help
```

## 一个可直接运行的真实补丁例子

`apr-043` 是已保留的真实 Angelix 补丁请求。下面先完整判定，再生成和复查单点反驳。输出文件必须尚不存在，父目录必须已存在。

```sh
request_file=experiments/introclass-certificates/records/cases/apr-043/request.json

python -B current/receiver.py decide --request "$request_file"

python -B current/receiver.py produce-refutation \
  --request "$request_file" --output ../../apr-043-refutation.json

python -B current/receiver.py check-refutation \
  --request "$request_file" --evidence ../../apr-043-refutation.json
```

完整判定返回 `REFUTED`，义务为 `repair`，该有限域内的 canonical 输入为 `[-1,-1,-2]`。单点复查确认输入确属声明点集且违反所指义务；它不证明其他点或全局最小性。`produce-refutation` 为寻找见证可能先执行完整域求值，不能把生产成本记成单点检查成本。

## 操作与结果

| 操作 | 含义 | 附加参数 |
| --- | --- | --- |
| `decide` | 完整判定请求并返回 canonical 结果 | 默认 `--algorithm demand`；可用 `--algorithm materialized` |
| `produce-record` | 完整求值并输出完整向量证据 | 可用 `--output NEW_FILE` |
| `check-record` | 重建请求并检查完整向量证据 | 必须提供 `--evidence FILE` |
| `produce-refutation` | 寻找并打包一个违反请求的输入 | 接受请求没有反驳，返回 `INVALID` |
| `check-refutation` | 检查请求绑定的单点反驳 | 必须提供 `--evidence FILE` |

所有操作都必须提供 `--request FILE`。检查操作接受原始证据 JSON，也接受本 CLI 输出的带 `evidence` 字段的封装。省略 `--output` 时 JSON 写到标准输出；已有文件不会被覆盖。`--algorithm` 仅适用于 `decide`。

| 退出码／结果 | 解读 |
| --- | --- |
| `0`，`result.status = ACCEPT` | 在声明有限域和语义下接受 |
| `0`，`result.status = REFUTED` | 成功计算或确认违反；这是有效语义结果 |
| `3`，`result.status = UNSUPPORTED` | 超出源码或请求 profile，不作语义判断 |
| `2`，`result.status = INVALID` | 请求、证据或读取等边界无效 |
| `2`，标准错误中的 `OUTPUT_ERROR` | 无法以新建方式写入输出 |

**不能把退出码 0 当成候选正确。** 自动化调用应检查 `result.status`。实现和请求哈希用于绑定与复核，不是作者签名或历史批准证明。

## 语义范围与修正

入口接受 `repairseal-int32-point-task-v1`：原程序、候选和参照的源码字符串，以及排序、无重复的实际 int32 输入向量。域最多 4,096 点，保留点之间的相关性，不按坐标轴自动补成笛卡尔积。策略固定为 `reference-everywhere`：候选须在所有声明点定义良好并与参照相符；此接口没有非空的独立 preservation 区域。原程序仍绑定在请求中。

源码必须满足封闭 signed 标量 profile，包括受限的 `main`、初始十进制输入、标量语句、受支持的整数表达式和分支，以及规范化的单个数值或标签观察。循环、数组、指针运算和其他未建模结构在接纳时被拒绝；int32 算术溢出等情况由定义性义务处理。所有角色每次调用均重新接纳，不信任证据声称的 AST 或源码意义。

本轮修复显式检查 pycparser 的对齐属性，并收紧 `(void)` 参数的限定形式。历史前端可能忽略这些属性并对本应拒绝的源返回语义结果；修订前端在判断候选之前返回 `UNSUPPORTED`。某些合法 C 对齐声明也在当前 profile 外，因此拒绝不等于该程序存在语义反例。

`current/src/` 保留完整的 16 模块集合，仅 `codeflaws_int32_bridge.py` 相对历史集合改变。`artifact/src/` 与历史结果、源码绑定和旧实验保持原样，用于精确复现。运行历史入口不能视为已使用本轮修复。逐项对照见 [source-attribute audit](../experiments/deep-review/receiver-audit/README.md)。

额外的弱序分析只针对比较／复制片段，其 13／75 类覆盖论证不扩大本 CLI 的有限接受域，也不证明任意 C 或任意 I/O 的全 int32 正确性。

## 统一验收

从 `artifact/` 运行，选择尚不存在的输出目录：

```sh
python -B verify_deep_review.py --output ../../repairseal-review-check
```

命令核对新研究和实现的绑定，重新计算源码接纳、弱序类及独立复核结果，重跑轨迹反例，并执行 **70 项定向／兼容性测试**。本轮最终结果为 `PASS_DEEP_REVIEW`。加 `--checks-only` 只重算新证据；加 `--historical` 额外运行原有 **203 项历史结果检查**。历史检查通过不代表重新执行了旧 CBMC／CPAchecker campaign。

统一验收检查保留的 native 收据，不重新启动对应编译 campaign。本轮新弱序研究另有 **78 次编译、10,602 次实际 GCC 执行**，来自一个 GCC 的三个优化／sanitizer 模式，并非三个独立编译器。最终记录见 [final-gate/result.json](../experiments/deep-review/validation/final-gate/result.json)。
