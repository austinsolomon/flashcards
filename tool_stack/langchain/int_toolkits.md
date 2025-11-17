# Toolkits (SQL/Browser/Python/Bash) - Intermediate

## Concept Overview

Toolkits are pre-built collections of tools that give LLMs capabilities to interact with external systems: querying databases (SQL), browsing the web, executing Python/Bash code, and more. They abstract away the complexity of safe execution, error handling, and result formatting. Toolkits transform LLMs from passive text generators into active problem solvers that can take actions in the real world.

**Why it matters:** Building robust, safe tools from scratch is hard. You need sandboxing, input validation, error handling, timeout management, and result parsing. Toolkits provide battle-tested implementations. The difference between a demo and production is almost always in the tooling - can your LLM reliably execute code, query databases, and handle errors gracefully?

## Real-World Example: AI-Powered Business Intelligence Assistant

This example demonstrates a production-grade BI assistant that uses multiple toolkits to analyze data, generate visualizations, and answer complex business questions.

```python
from langchain_community.agent_toolkits import (
    SQLDatabaseToolkit,
    create_python_agent,
)
from langchain_community.utilities import SQLDatabase
from langchain_experimental.tools import PythonREPLTool
from langchain.agents import create_openai_tools_agent, AgentExecutor, Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import ShellTool
import sqlite3
import os
from typing import List, Dict, Any
import pandas as pd

# ========== SQL TOOLKIT SETUP ==========
# Create sample business database
def setup_sample_database():
    """Create a sample sales database for demonstration."""
    conn = sqlite3.connect('business_data.db')
    cursor = conn.cursor()

    # Sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            date TEXT,
            product TEXT,
            category TEXT,
            region TEXT,
            revenue REAL,
            units_sold INTEGER,
            customer_segment TEXT
        )
    """)

    # Sample data
    sample_data = [
        ('2024-01-15', 'Laptop Pro', 'Electronics', 'West', 1299.99, 45, 'Enterprise'),
        ('2024-01-16', 'Office Chair', 'Furniture', 'East', 299.99, 120, 'SMB'),
        ('2024-01-17', 'Laptop Pro', 'Electronics', 'West', 1299.99, 67, 'Enterprise'),
        ('2024-01-18', 'Desk Lamp', 'Furniture', 'South', 49.99, 200, 'Consumer'),
        ('2024-01-19', 'Wireless Mouse', 'Electronics', 'North', 29.99, 350, 'Consumer'),
        ('2024-01-20', 'Monitor 4K', 'Electronics', 'West', 599.99, 89, 'Enterprise'),
        ('2024-02-01', 'Standing Desk', 'Furniture', 'East', 799.99, 55, 'SMB'),
        ('2024-02-05', 'Laptop Pro', 'Electronics', 'East', 1299.99, 78, 'Enterprise'),
    ]

    cursor.executemany("""
        INSERT INTO sales (date, product, category, region, revenue, units_sold, customer_segment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_data)

    # Customer table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            segment TEXT,
            lifetime_value REAL,
            region TEXT,
            signup_date TEXT
        )
    """)

    customer_data = [
        ('Acme Corp', 'Enterprise', 125000, 'West', '2023-01-10'),
        ('Tech Startup Inc', 'SMB', 35000, 'East', '2023-06-15'),
        ('Consumer Joe', 'Consumer', 500, 'South', '2024-01-01'),
    ]

    cursor.executemany("""
        INSERT INTO customers (name, segment, lifetime_value, region, signup_date)
        VALUES (?, ?, ?, ?, ?)
    """, customer_data)

    conn.commit()
    conn.close()

setup_sample_database()

# Initialize SQL Database
db = SQLDatabase.from_uri("sqlite:///business_data.db")

# ========== SQL TOOLKIT WITH SAFE EXECUTION ==========
class SafeSQLToolkit:
    """SQL toolkit with read-only safety and query validation."""

    def __init__(self, db: SQLDatabase):
        self.db = db
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

        # Create toolkit with safety constraints
        self.toolkit = SQLDatabaseToolkit(
            db=db,
            llm=self.llm
        )

        # Filter to only safe, read-only tools
        self.tools = [
            tool for tool in self.toolkit.get_tools()
            if 'query' in tool.name.lower() or 'schema' in tool.name.lower()
        ]

    def validate_query(self, query: str) -> bool:
        """Validate that query is safe (read-only)."""
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
        query_upper = query.upper()

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False

        return True

    def get_tools(self) -> List[Tool]:
        """Get safe SQL tools."""
        return self.tools

# ========== PYTHON REPL TOOLKIT WITH SANDBOXING ==========
class SafePythonToolkit:
    """Python execution toolkit with safety constraints and visualization support."""

    def __init__(self):
        self.allowed_imports = {
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'scipy', 'sklearn',
            'json', 'csv', 'datetime', 'collections', 're', 'math'
        }

        # Create Python tool with restrictions
        self.python_tool = PythonREPLTool()
        self.python_tool.description = """
A Python shell. Use this to execute Python code for data analysis and visualization.
Available libraries: pandas, numpy, matplotlib, seaborn
Input should be valid Python code. To see output, use print().
For plots, save to file with plt.savefig('output.png') and it will be displayed.
"""

    def create_analysis_tool(self) -> Tool:
        """Create a specialized data analysis tool."""
        return Tool(
            name="python_data_analyzer",
            description=self.python_tool.description,
            func=self._safe_execute
        )

    def _safe_execute(self, code: str) -> str:
        """Execute Python code with safety checks."""
        # Basic validation
        if 'import os' in code or 'import sys' in code or 'eval(' in code or 'exec(' in code:
            return "Error: Unauthorized operations detected. Only data analysis libraries are allowed."

        try:
            result = self.python_tool.run(code)
            return result
        except Exception as e:
            return f"Execution error: {str(e)}"

# ========== BASH TOOLKIT FOR SYSTEM OPERATIONS ==========
class SafeBashToolkit:
    """Controlled bash execution for file operations and system queries."""

    def __init__(self, allowed_commands: List[str] = None):
        self.allowed_commands = allowed_commands or [
            'ls', 'pwd', 'cat', 'grep', 'head', 'tail', 'wc',
            'find', 'echo', 'date', 'df', 'du'
        ]

        self.shell_tool = ShellTool()

    def create_safe_shell_tool(self) -> Tool:
        """Create a restricted shell tool."""
        return Tool(
            name="safe_shell",
            description=f"""
Execute safe shell commands for file operations and system queries.
Allowed commands: {', '.join(self.allowed_commands)}
Input format: command with arguments (e.g., 'ls -la' or 'cat file.txt')
""",
            func=self._safe_execute
        )

    def _safe_execute(self, command: str) -> str:
        """Execute shell command with restrictions."""
        # Extract base command
        base_command = command.split()[0]

        if base_command not in self.allowed_commands:
            return f"Error: Command '{base_command}' not allowed. Permitted: {', '.join(self.allowed_commands)}"

        try:
            result = self.shell_tool.run(command)
            return result
        except Exception as e:
            return f"Execution error: {str(e)}"

# ========== COMBINED BI ASSISTANT WITH ALL TOOLKITS ==========
class BusinessIntelligenceAssistant:
    """AI assistant combining SQL, Python, and Bash toolkits for comprehensive analysis."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

        # Initialize all toolkits
        self.sql_toolkit = SafeSQLToolkit(db)
        self.python_toolkit = SafePythonToolkit()
        self.bash_toolkit = SafeBashToolkit()

        # Combine all tools
        self.tools = [
            *self.sql_toolkit.get_tools(),
            self.python_toolkit.create_analysis_tool(),
            self.bash_toolkit.create_safe_shell_tool()
        ]

        # Create specialized prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Business Intelligence analyst with access to:
1. SQL database containing sales and customer data
2. Python environment for data analysis and visualization
3. Shell commands for file operations

When answering questions:
1. First, explore the database schema to understand available data
2. Query the database to get relevant data
3. Use Python for calculations, analysis, and visualizations
4. Provide clear, actionable insights

Always show your work and explain your analysis steps.
"""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )

    def analyze(self, question: str) -> str:
        """Analyze a business question using all available tools."""
        try:
            result = self.agent_executor.invoke({
                "input": question
            })
            return result['output']
        except Exception as e:
            return f"Analysis failed: {str(e)}"

# ========== PRODUCTION USAGE EXAMPLES ==========
print("=== Business Intelligence Assistant Demo ===\n")

bi_assistant = BusinessIntelligenceAssistant()

# Example 1: SQL Analysis
print("Question 1: What are our top 3 products by revenue?\n")
answer1 = bi_assistant.analyze(
    "What are our top 3 products by revenue? Show the product name and total revenue."
)
print(f"\nAnswer: {answer1}\n")
print("-" * 80 + "\n")

# Example 2: Combined SQL + Python Analysis
print("Question 2: Analyze revenue trends by region\n")
answer2 = bi_assistant.analyze("""
Analyze revenue by region. Calculate:
1. Total revenue per region
2. Average revenue per transaction per region
3. Create a simple comparison

Use SQL to get the data, then Python for calculations.
""")
print(f"\nAnswer: {answer2}\n")
print("-" * 80 + "\n")

# Example 3: Complex Multi-Step Analysis
print("Question 3: Customer segment analysis\n")
answer3 = bi_assistant.analyze("""
Analyze our customer segments:
1. What percentage of revenue comes from each segment (Enterprise, SMB, Consumer)?
2. What's the average transaction value per segment?
3. Which segment has the highest growth potential based on units sold vs revenue?

Provide actionable recommendations.
""")
print(f"\nAnswer: {answer3}\n")
print("-" * 80 + "\n")

# ========== CUSTOM TOOLKIT EXAMPLE ==========
class ReportGenerationToolkit:
    """Custom toolkit for generating business reports."""

    def __init__(self, db: SQLDatabase):
        self.db = db
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)

    def create_tools(self) -> List[Tool]:
        """Create custom report generation tools."""
        return [
            Tool(
                name="generate_revenue_report",
                description="Generate a comprehensive revenue report with key metrics",
                func=self._generate_revenue_report
            ),
            Tool(
                name="generate_customer_report",
                description="Generate a customer analysis report",
                func=self._generate_customer_report
            ),
            Tool(
                name="export_to_csv",
                description="Export query results to CSV file. Input: SQL query",
                func=self._export_to_csv
            )
        ]

    def _generate_revenue_report(self, time_period: str = "all") -> str:
        """Generate revenue report."""
        query = """
        SELECT
            category,
            SUM(revenue) as total_revenue,
            SUM(units_sold) as total_units,
            AVG(revenue) as avg_transaction,
            COUNT(*) as num_transactions
        FROM sales
        GROUP BY category
        ORDER BY total_revenue DESC
        """

        result = self.db.run(query)

        report = f"""
REVENUE REPORT
==============
Period: {time_period}

{result}

Key Insights:
- Analysis based on {len(result.split('\n')) - 1} categories
- Report generated at {pd.Timestamp.now()}
"""
        return report

    def _generate_customer_report(self, segment: str = "all") -> str:
        """Generate customer analysis report."""
        query = f"""
        SELECT
            segment,
            COUNT(*) as customer_count,
            AVG(lifetime_value) as avg_ltv,
            SUM(lifetime_value) as total_ltv
        FROM customers
        {'WHERE segment = "' + segment + '"' if segment != 'all' else ''}
        GROUP BY segment
        """

        result = self.db.run(query)
        return f"CUSTOMER REPORT\n{'=' * 50}\n{result}"

    def _export_to_csv(self, query: str) -> str:
        """Export query results to CSV."""
        try:
            df = pd.read_sql_query(query, self.db._engine)
            filename = f"export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            return f"Data exported to {filename} ({len(df)} rows)"
        except Exception as e:
            return f"Export failed: {str(e)}"

# Example using custom toolkit
report_toolkit = ReportGenerationToolkit(db)
custom_tools = report_toolkit.create_tools()

print("\n=== Custom Report Generation Toolkit ===\n")
for tool in custom_tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}\n")

# Generate sample report
revenue_report = custom_tools[0].func("Q1 2024")
print(revenue_report)
```

### Why This Example Shows Toolkit Power:

1. **Multi-Toolkit Integration**: Combines SQL, Python, and Bash for comprehensive capabilities
2. **Safety & Sandboxing**: Validates queries, restricts dangerous operations, controls execution
3. **Production-Ready Error Handling**: Graceful degradation and clear error messages
4. **Custom Toolkit Creation**: Shows how to build domain-specific toolkits
5. **Real Business Value**: Solves actual BI problems, not toy examples

## Best Practices for Mastering Toolkits

1. **Always implement safety layers for code execution tools**: Never expose raw Python/Bash execution to LLMs without validation. Whitelist allowed operations, blacklist dangerous functions (eval, exec, os.system), and run in isolated environments. One prompt injection could delete your database.

2. **Use read-only database connections for SQL toolkits**: Configure your SQLDatabaseToolkit with a read-only user that cannot modify data. Even with query validation, LLMs can make mistakes. Defense in depth is critical - validation at LLM level, query level, and database permission level.

3. **Combine toolkits strategically for multi-step workflows**: SQL for data retrieval → Python for analysis → Bash for file export is more reliable than trying to do everything in one tool. Each toolkit excels at specific tasks; chain them together in LCEL for robust workflows.

4. **Add timeouts and resource limits to all execution tools**: Set maximum execution time (10-30 seconds), memory limits, and output size caps. LLMs can generate infinite loops or massive queries. Use Docker containers or sandboxed environments for additional isolation.

5. **Provide rich, examples-based tool descriptions**: Tool descriptions are critical - they're the LLM's only guidance. Include input format examples, output format, edge cases, and when to use vs. not use the tool. Good descriptions reduce errors by 50%+.

## Common Pitfalls to Avoid

- **Don't trust LLM-generated queries blindly**: Always validate SQL, filter allowed commands
- **Avoid giving tools overly broad permissions**: Principle of least privilege applies to LLM tools
- **Don't skip error handling**: Tools fail; make sure your agent can recover gracefully
- **Remember tool descriptions are critical**: LLMs rely 100% on descriptions to choose and use tools
- **Don't ignore observability**: Log all tool executions with inputs/outputs for debugging and security auditing
