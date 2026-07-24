# 缺陷报告（DEFECTS）

> 本文档记录测试体系发现的现有实现缺陷。按任务要求：**未改动任何业务功能**，
> 缺陷仅以可执行测试形式（`@unittest.expectedFailure`）标注。修复业务代码后，
> 去掉对应的 `@expectedFailure` 装饰器即转为回归断言。
>
> 相关用例见 [`backend/flights/tests/test_defects.py`](../flights/tests/test_defects.py)。
> 运行结果中显示为 `expected failures=15`，不会让 CI 变红。

## 汇总

| # | 类别 | 位置 | 现象 | 期望 | 对应用例 |
|---|------|------|------|------|----------|
| 1 | 日期处理 | `views.flight_list` L34-35 | 非法日期被 `except ValueError: pass` 静默忽略，退化为“返回全部” | 报错 / 返回空集 / 400 | `DateHandlingDefects.*` (3) |
| 2 | 排序未实现 | `views.flight_list` | `ordering` 参数被忽略，恒为插入顺序 | 支持 price / departure_time / airline 排序 | `OrderingDefects.*` (3) |
| 3 | 直飞/中转筛选未实现 | `views.flight_list` | `is_direct` 参数被忽略 | 按 `is_direct` 过滤 | `FilterDefects.test_filter_direct_only` / `test_filter_transfer_only` |
| 4 | 共享航班筛选未实现 | `views.flight_list` | `is_shared` 参数被忽略 | 按 `is_shared` 过滤 | `FilterDefects.test_filter_shared_only` |
| 5 | 输入/语义校验缺失 | `models.Flight` / `views` | 出发=到达、负价、负余票、到达早于出发、非法方法均不校验；无含税总价字段 | 模型/视图层校验并返回 400/405；提供含税价字段 | `ValidationDefects.*` (4) + `MethodHandlingDefects.*` (2) |

合计 **15** 个 expected failures。

## 明细

### 1. 非法日期静默忽略（重点）
[views.py](../flights/views.py#L25-L35) 中：

```python
if departure_date:
    try:
        date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
        flights = flights.filter(...)
    except ValueError:
        pass   # ← 缺陷：非法日期被吞掉，用户以为按日期筛选，实际返回全部
```

- `departure_date=not-a-date` → 期望报错/空集，实际返回全部 6 条。
- `departure_date=2026-13-99` → 期望 400，实际 200。
- `departure_date=2026/08/01` → 期望被识别或报错，实际静默忽略。

**前端连锁影响**：`App.vue` 的搜索/筛选/排序都会把参数发给后端，用户看到的是“看似筛选实则未筛选”的结果，属于典型的静默数据错误。

### 2. 排序参数未实现
前端 `buildSortParams` 会发送 `ordering=price|departure_time|airline`，但后端从不读取该参数。集成测试 [`test_integration.py`](../flights/tests/test_integration.py) 已固化“参数被忽略”的当前行为；`OrderingDefects` 固化“期望排序生效”的目标行为。

### 3 & 4. 筛选参数未实现
前端 `buildFilterParams` 发送 `is_direct` / `is_shared`，后端未处理。

### 5. 校验与含税价
- 模型 `IntegerField` / `DecimalField` 无非负约束，`full_clean()` 不报错。
- 到达时间早于出发时间可保存。
- `flight_detail` 未限制 HTTP 方法（POST 不返回 405）。
- 列表仅返回裸 `price`，前端用静态“含税”文案标注，缺乏真实税费字段（`total_price`）。

## 如何将缺陷用例转为回归断言

修复某项业务代码后，删除对应用例上方的 `@unittest.expectedFailure`：

```python
# 修复前
@unittest.expectedFailure
def test_ordering_by_price_ascending(self):
    ...

# 修复后（转为常规回归断言）
def test_ordering_by_price_ascending(self):
    ...
```

此时该用例将作为正式回归测试保护已修复的行为。
