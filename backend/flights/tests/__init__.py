"""flights 应用测试包。

按关注点拆分：
- factories：测试数据工厂
- test_models：模型约束与关联
- test_views_list：flight_list 列表视图边界
- test_views_detail：flight_detail 详情视图边界
- test_serialization：序列化字段完整性
- test_integration：多条件组合 + 排序语义 + 与种子数据一致的端到端断言
- test_defects：故意暴露现有实现缺陷（expectedFailure）
"""
