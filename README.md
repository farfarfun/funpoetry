# funpoetry

`funpoetry` 是一个轻量级版本号递增工具，支持 PEP 621 的 `[project].version`、旧版 Poetry 的
`[tool.poetry].version`，以及 `script/__version__.md` 版本文件。

## 安装

```bash
pip install funpoetry
```

## 使用

在项目根目录执行：

```bash
funpoetry version-upgrade
```

命令会读取当前版本、按 64 进制递增修订号并写回原文件；找不到受支持的版本源时以非零状态退出。

开发环境使用 uv：

```bash
uv sync --dev
uv run pytest
```

## 发布

发布前执行测试和代码检查：

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

通过后在项目根目录执行完整发布流程：

```bash
uv run funbuild build
```

该命令由 `funbuild` 统一完成版本递增、构建、安装校验、发布、推送和 Git 标签创建。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
