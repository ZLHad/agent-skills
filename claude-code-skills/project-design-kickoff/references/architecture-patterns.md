# 架构扩展性预留（Level 3）

复杂项目的 4 条架构约束。这些不是"可选优化"，而是 **Day 1 就要预留的接口**——违反了再补会非常痛苦。

---

## 原则 1：薄封装 — 核心业务逻辑与框架无关

**约束**：核心业务模块**不直接** `import` 重量级外部框架（Web 框架 / ML 库 / Agent 编排器 / 云 SDK 等），全部通过薄封装层。

**示例**：

```
项目结构（示意）：
├── core/                    ← 业务逻辑（零外部框架依赖）
│   ├── domain/              ← 业务对象
│   ├── services/            ← 业务服务
│   └── adapters/            ← 抽象接口
└── infra/                   ← 薄封装层
    ├── http/                ← 包装 FastAPI / Express
    ├── db/                  ← 包装 SQLAlchemy / Prisma
    └── llm/                 ← 包装 Anthropic SDK / OpenAI SDK
```

**为什么重要**：
- `core/` 可以脱离框架跑单元测试（mock adapters 即可）
- 换底层（FastAPI → Django，Qlib → FinRL）只改 infra/，业务代码不动
- 核心业务可以作为独立库发布

**Day 1 的动作**：建立目录分层，每个外部依赖**只有一个文件**直接 import 它。

---

## 原则 2：插件化一切会变的东西

**约束**：识别项目中"会变化或扩展"的组件，从 Day 1 就用**抽象基类 + 注册表**模式。

**识别"会变"的信号**：
- 未来可能加更多同类实例（如"加一个新的数据源"、"加一个新的 Agent"、"加一个新的 LLM provider"）
- 可能换实现（如"从 SQLite 切到 PostgreSQL"）
- 需要按配置启用/禁用

**模式**：

```python
# 抽象基类
class BaseXxx(ABC):
    name: str
    @abstractmethod
    def do_something(self, ...) -> ...: ...

# 注册表 + 装饰器
_registry: dict[str, type[BaseXxx]] = {}

def register(name: str):
    def decorator(cls):
        _registry[name] = cls
        return cls
    return decorator

# 使用
@register("foo")
class FooImpl(BaseXxx):
    ...
```

**典型需要插件化的维度**：
- 数据源 / 外部 API 适配器
- 业务规则 / 策略 / 评估器
- LLM provider / 模型路由
- 通知渠道（邮件 / Slack / Webhook / ...）
- 导入导出格式

**Day 1 的动作**：不是所有插件点都要立刻实现，但**基类和注册机制要先建**。

---

## 原则 3：外部生态 adapter 预留

**约束**：项目内部用自己的抽象标准，但**在边缘目录预留 adapter 层**，即使 Day 1 不实现任何 adapter，也要建占位 + README 说明扩展方向。

**示例**：

```
core/adapters/
├── README.md                      ← 说明扩展方向（哪些外部生态会对接）
├── external_api/                  ← Phase 2/3 对接外部 API
├── plugin_framework/              ← Phase 2/3 加载外部插件生态
└── ...
```

**为什么**：任何"引入外部生态"的动作都应该是**"加文件"而不是"改文件"**。提前建好目录+README，未来导入外部源代码或生态时不侵入现有业务代码。

**这和原则 2 的区别**：原则 2 是项目内同类组件的插件化（我有 N 个数据源），原则 3 是**跨生态边界**的适配（我要接入完全不同体系的外部工具）。

---

## 原则 4：多用户 / 多环境预留

**约束**：如果项目**未来可能**变成多用户 / 多环境 / 多租户，从 Day 1 就在数据库 schema 和 API 层**预留维度字段**，单用户场景默认值填充。

**最小预留动作**：

```sql
-- 所有"归用户所有"的表加 user_id 字段，单用户默认 1
CREATE TABLE xxx (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL DEFAULT 1,
    ...
);
CREATE INDEX idx_xxx_user_id ON xxx(user_id);
```

```python
# API 层依赖注入 current_user，单用户永远返回 admin
def get_current_user() -> User:
    return User(id=1, username="admin")

@router.post("/...")
async def endpoint(current_user: User = Depends(get_current_user)):
    await do_something(user_id=current_user.id, ...)
```

**Day 1 的动作**：
- 数据库 schema 的 DDL 里就加 `user_id`
- API 路由就通过 `Depends(get_current_user)` 获取当前用户
- 未来启用多用户时，**只需要替换 `get_current_user` 的实现**，上层业务代码不变

**类似地**：如果未来可能多环境（dev/staging/prod），可以预留 `env: str` 或 tenant 维度。

**警告**：不是所有项目都需要这条。**如果明确项目就是一人自用**，可以跳过。但**一旦有一点可能性未来开放给别人**，Day 1 预留成本很低、事后补成本很高。

---

## 共同的思维方式

四条原则背后是同一个判断：

> **"一锅烩"的代码能跑但扩不动。从 Day 1 就在"可能变的地方"留接口**——接口设计得再轻，也比后面重构强得多。

**反面教训**：
- "先跑通再说，后面再重构" —— 通常"后面再重构"就是"永远不重构"
- "现在就一个数据源，写死 Tushare 吧" —— 三个月后要加 AKShare 时发现所有调用都绑死
- "现在单用户就好，user_id 以后加" —— 以后加意味着全库数据迁移

**正面做法**：
- 写第一行业务代码前，花 10 分钟想清楚"这里是 fixed 的还是可能变的"
- 可能变的都走抽象 + 配置
- adapter 目录 Day 1 就建，即使是空的

---

## 在 CLAUDE.md 里怎么体现

Level 3 模板的"需要特别注意的约束"章节应该包含：

```markdown
## 需要特别注意的约束

1. **核心业务逻辑框架无关**（原则 1）
2. **插件化"会变"的组件**（原则 2）
3. **adapter 目录预留**（原则 3）
4. **多用户/多环境预留**（原则 4，如适用）
```

每条约束都应该 link 到一份详细文档（通常是 `doc/docs/architecture/layers.md`），避免 CLAUDE.md 本身变成长文档。
