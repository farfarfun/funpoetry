# Changelog

## 1.0.8

### 新增

- 支持读取和更新 PEP 621 的 `[project].version`。
- 增加 `uv.lock` 和 Ruff 开发配置。

### 修复

- 找不到版本源或版本号无效时返回明确错误，CLI 以非零状态退出。
- 补齐公开 API 类型标注和中文文档。

### 变更

- 构建后端由 Poetry 迁移至 Hatchling，依赖管理迁移至 uv。
- 删除未使用的 Poetry 和 cryptography 运行时依赖。

### 废弃

（无）

## 1.0.7 及更早版本

早期版本未维护 CHANGELOG，具体变更参见 git 提交历史。
