# InvestResearch.py 代码说明

这是一个基于 LangChain 框架搭建的"投研 AI Agent"，让大模型能自动调用工具去查数据、搜新闻，然后写出一份投研报告。

整体流程：你给它一个问题 → Agent 自己决定调用哪些工具 → 拿到数据后交给大模型分析 → 输出结构化报告。

---

## 各部分说明

### 1. 搜索工具

```python
search_ddg = DuckDuckGoSearchRun()
search_tavily = TavilySearchResults(max_results=5)
```

两个搜索引擎。Tavily 是专门为 AI Agent 设计的搜索 API，结果质量更好，优先用它；DuckDuckGo 作为备用。

---

### 2. 股票数据函数

```python
def get_stock_data(ticker: str) -> str:
```

用 `yfinance` 库从雅虎财经拉取股票数据，返回市值、PE、PB、股息率、ROE 这几个核心财务指标。`600938.SS` 是中国海油的 A 股代码（`.SS` 表示上交所）。

---

### 3. 简单分析函数

```python
def analyze_stock(ticker: str) -> str:
```

基于拉回来的财务数据做规则判断，比如 PE < 10 就标"估值偏低"，股息率 > 5% 就标"高股息"。这是硬编码的规则逻辑，不是 AI 判断的。

---

### 4. LLM 配置

```python
llm = ChatOpenAI(model="qwen-plus", base_url="https://dashscope.aliyuncs.com/...")
```

用的是阿里云百炼的 `qwen-plus` 模型，但通过 OpenAI 兼容接口接入，所以用 `ChatOpenAI` 这个类就能直接调。

---

### 5. Tools 列表

```python
tools = [Search, SearchDDG, StockData, Analyze]
```

把上面定义的函数和搜索工具包装成 LangChain 的 `Tool` 对象，每个工具有名字和描述。Agent 会根据描述来决定什么时候调用哪个工具。

---

### 6. ReAct Agent

```python
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(...)
```

这是核心。`ReAct` 是一种 Agent 推理模式：Reasoning（推理）+ Acting（行动）交替进行。

流程：

```
思考：我需要搜索中国海油的新闻
行动：调用 Search 工具
观察：拿到搜索结果
思考：我还需要财务数据
行动：调用 StockData 工具
观察：拿到 PE、市值等数据
思考：数据够了，可以写报告了
最终答案：输出投研报告
```

`hub.pull("hwchase17/react")` 是从 LangChain Hub 拉取一个现成的 ReAct prompt 模板，定义了上面这套推理格式。

---

### 7. 执行入口

```python
result = agent_executor.invoke({"input": query})
```

把问题丢给 Agent，它自动跑完整个推理+工具调用流程，最后输出一份包含公司简介、行业分析、财务数据、利好风险、投资结论的报告。

---

## 总结

这段代码让 AI 从"只会聊天"变成了"会自己去查数据、搜新闻，然后写报告"的分析师 Agent。
