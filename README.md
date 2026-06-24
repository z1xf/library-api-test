# 图书借阅管理系统 —— 接口自动化测试项目

> 自建简易后端（Flask + SQLite），围绕其核心业务（用户注册登录、图书管理、借阅归还）独立设计测试用例并实现自动化测试，覆盖等价类划分、边界值分析、场景法、安全测试等设计方法，并在测试过程中真实发现并验证修复了两处后端缺陷。

---

## 项目亮点

- **不是简单调用现成接口**：自己实现被测系统的业务逻辑，因此能针对真实业务规则设计有深度的测试用例，而不只是验证接口能否调通
- **真实发现缺陷，而非仅"跑通"测试**：
  - 通过边界值分析设计的用例（库存数量恰好为 0 时尝试借阅），发现后端库存判断条件存在 `stock < 0` 应为 `stock <= 0` 的边界错误，验证修复后重新跑通
  - 通过等价类划分设计的用例（新增图书时缺少必填字段），发现后端未对 `title` 字段做空值校验，补充校验逻辑后验证修复
- **覆盖完整业务场景**：用户认证、图书增查、借阅状态流转（借阅→重复借阅拦截→归还）、借阅记录的越权与数据隔离校验
- **测试设计与实现分离**：先产出独立的测试用例设计文档（`test_case_design.md`），再据此实现自动化代码，体现"先设计、再实现"的测试工程思路
- **接入 CI 与可视化报告**：GitHub Actions 自动跑测试，pytest-html 生成可视化报告

---

## 技术栈

| 类别 | 工具 |
|---|---|
| 被测系统 | Flask + SQLite |
| 测试框架 | Pytest |
| HTTP 客户端 | requests |
| 测试数据生成 | Faker / uuid |
| 测试报告 | pytest-html |
| CI | GitHub Actions |

---

## 项目结构

```
library-api-test/
├── app/
│   ├── app.py                  # 被测系统：Flask 后端
│   └── library.db              # 运行后自动生成
├── tests/
│   ├── conftest.py             # 公共fixture：启动服务、清空数据库、获取token
│   ├── test_user.py            # 用户模块测试
│   ├── test_book.py            # 图书模块测试
│   ├── test_borrow.py          # 借阅/归还模块测试
│   └── test_borrow_history.py  # 借阅记录模块测试
├── test_case_design.md         # 测试用例设计文档
├── requirements.txt
├── pytest.ini
└── .github/workflows/test.yml  # CI 配置
```

---

## 接口列表

| 模块 | 方法 | 路径 | 说明 |
|---|---|---|---|
| 用户 | POST | /api/register | 注册 |
| 用户 | POST | /api/login | 登录，返回token |
| 图书 | POST | /api/books | 新增图书（需token） |
| 图书 | GET | /api/books | 查询图书列表，支持模糊搜索 |
| 图书 | GET | /api/books/{id} | 查询单本图书 |
| 借阅 | POST | /api/borrow | 借书（需token） |
| 借阅 | POST | /api/return | 还书（需token） |
| 借阅 | GET | /api/borrow/history | 查询本人借阅记录（需token） |

---

## 测试用例设计

完整用例设计见 [`test_case_design.md`](./test_case_design.md)，共编写 24 条测试用例，覆盖以下设计方法：

| 设计方法 | 应用场景举例 |
|---|---|
| 等价类划分 | 邮箱格式校验、缺少必填字段 |
| 边界值分析 | 用户名长度上下边界、库存数量临界值（0/1） |
| 场景法/状态流转 | 借阅→归还完整流程、重复借阅拦截 |
| 错误推测法 | 查询不存在的资源id、重复注册同一用户名 |
| 安全测试/数据隔离 | 未授权访问、跨用户越权操作、借阅记录数据隔离 |

---

## 缺陷发现与修复记录

| 编号 | 发现方式 | 问题描述 | 修复方式 |
|---|---|---|---|
| BUG-01 | 边界值分析（TC-009） | 库存判断条件写成 `stock < 0`，导致库存恰好为0时仍能借阅成功，库存变为负数 | 修正为 `stock <= 0` |
| BUG-02 | 等价类划分（TC-017） | 新增图书接口未校验 `title` 字段是否为空，传空值也能成功创建 | 补充对 `title` 的非空校验 |

测试报告截图（修复前 / 修复后对比）：

```
screenshots/
├── report-bug-found.png      # 库存边界bug被发现时的测试报告
├── report-all-passed.png     # 修复后全部用例通过的测试报告
```

> 注：请将实际截图文件放入 `screenshots/` 文件夹后，取消下方图片引用的注释
>
> <!-- ![发现bug时的测试报告](./screenshots/report-bug-found.png) -->
> <!-- ![修复后全部通过的测试报告](./screenshots/report-all-passed.png) -->

---

## 如何运行

### 1. 创建虚拟环境并安装依赖

```bash
conda create -n library_test python=3.10
conda activate library_test
pip install -r requirements.txt
```

### 2. 启动被测系统

```bash
python app/app.py
```

### 3. 运行自动化测试

```bash
pytest -v
```

### 4. 生成可视化测试报告

```bash
pytest -v --html=report.html --self-contained-html
```

生成的 `report.html` 用浏览器打开即可查看带颜色标注的详细测试结果。

---

## CI 自动化

项目已配置 GitHub Actions（见 `.github/workflows/test.yml`），每次 push 代码会自动：
1. 安装依赖
2. 启动被测服务
3. 执行全部测试用例
4. 生成测试报告并作为构建产物上传

---

## 后续可优化方向

- 增加更多并发/性能维度的测试
- 引入 Allure 替代 pytest-html，生成更丰富的可视化报告
- 补充对借阅记录分页、排序等功能的测试用例
- 探索结合 AI 辅助生成测试用例草稿，对比人工设计的覆盖率差异
