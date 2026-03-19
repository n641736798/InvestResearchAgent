# ======================
# 导入工具
# ======================
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
import yfinance as yf

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain import hub

import os


# ======================
# 搜索工具（升级：Tavily + DuckDuckGo）
# ======================

search_ddg = DuckDuckGoSearchRun()



# Set the environment variable before using Tavily
os.environ["TAVILY_API_KEY"] = "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"

# Then initialize without passing the key
search_tavily = TavilySearchResults(max_results=5)



# ======================
# 股票数据
# ======================
def get_stock_data(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        data = {
            "市值": info.get("marketCap"),
            "PE": info.get("trailingPE"),
            "PB": info.get("priceToBook"),
            "股息率": info.get("dividendYield"),
            "ROE": info.get("returnOnEquity"),
        }
        return str(data)
    except Exception as e:
        return f"获取失败: {str(e)}"


# ======================
# 简单分析逻辑
# ======================
def analyze_stock(ticker: str) -> str:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        pe = info.get("trailingPE")
        div = info.get("dividendYield")
        roe = info.get("returnOnEquity")

        result = []

        if pe and pe < 10:
            result.append("估值偏低")
        elif pe and pe > 20:
            result.append("估值偏高")

        if div and div > 0.05:
            result.append("高股息")

        if roe and roe > 0.15:
            result.append("ROE较强")

        return "\n".join(result) if result else "无明显价值信号"

    except Exception as e:
        return f"分析失败: {str(e)}"


# ======================
# LLM
# ======================
llm = ChatOpenAI(
    model="qwen-plus",
    api_key="sk-98d6f08a356e4b9bbde15d7cab4ae551",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0
)


# ======================
# Tools
# ======================
tools = [
    Tool(
        name="Search",
        func=search_tavily.run,
        description="用于搜索公司新闻、行业信息、最新动态（优先使用）"
    ),
    Tool(
        name="SearchDDG",
        func=search_ddg.run,
        description="备用搜索工具"
    ),
    Tool(
        name="StockData",
        func=get_stock_data,
        description="获取股票财务数据，输入如 600938.SS"
    ),
    Tool(
        name="Analyze",
        func=analyze_stock,
        description="分析股票估值和质量指标，输入如 600938.SS"
    ),
]


# ======================
# Prompt（关键优化点）
# ======================
prompt = hub.pull("hwchase17/react")


# ======================
# Agent
# ======================
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)


# ======================
# Query
# ======================
query = """
请对中国海油（600938.SS）进行投研分析：

要求：
1. 公司简介
2. 行业分析（必须调用搜索工具）
3. 财务数据分析（必须调用StockData）
4. 利好与风险
5. 投资结论（保守）

结构化输出，避免编造数据。
"""

result = agent_executor.invoke({"input": query})

print(result["output"])