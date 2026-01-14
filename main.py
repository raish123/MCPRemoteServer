#In this File what we are doing we are creating a remote server step is almost same 
#but one thing that i have do push my code to github distributed version contro system through that fastmcp cloud 
#we have to deploy
#and then either create proxy server or else direct integrate the url with custom connector from claude desktop.

from fastmcp import FastMCP
import random
import sqlite3
from datetime import datetime
import os,sys

BASE_DIR = r"D:\MCPPratical"
os.makedirs(BASE_DIR, exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, "expenses.db")
CAT_PATH = os.path.join(BASE_DIR, "categories.json")

# Create MCP server instance
mcp = FastMCP(name="ExpenseRemoteServer")

# Database connection helper function
# ---------------------------
def get_connection():
    return sqlite3.connect(
        database=DB_PATH,check_same_thread=True
    )

# Tool 1: connection establish

# Create table
# ---------------------------
@mcp.tool(name="create_Table_tool",description="this fuction will create table in database")
def create_table():
    conn = get_connection() #establishing connection btn python and sqlite3
    
    #cursor object will execute the command for me with help of connection
    cursor = conn.cursor()
    
    #create table command.
    sql_query = """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        subcategory TEXT DEFAULT "",
        expense_date TEXT,
        created_at TEXT
    )
    """
    #now telling to create table for me.
    cursor.execute(sql_query)
    
    #permantenly saving into database and closing the connection.
    conn.commit()
    conn.close()


#calling fxn to create tables in database
create_table()



# Tool 2: Add Expense
@mcp.tool(name="add_expense_tool",description="this fuction will add expense in existing table in database")
def add_expensedd_expense(
    category: str,
    amount: float,
    subcategory:str,
    expense_date: str | None = None
    ):
    
    if expense_date is None:
        expense_date = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses (
        category,
        amount,
        subcategory,
        expense_date,
        created_at
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        category,
        amount,
        subcategory,
        expense_date,
        datetime.now().isoformat()
    ))

    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    
    return {
        "status":"ok",
        "id":expense_id
    }


# Tool3:List all expenses
# ---------------------------
@mcp.tool(name="list_expense_tool",description="this fuction will give the list of record in existing table wrt to dates")
def list_expenses(
    start_date: str | None = None,
    end_date: str | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""SELECT * FROM expenses
                   where expense_date between ? and ?
                   ORDER BY expense_date DESC""",(start_date,end_date)
                   )
    rows = cursor.fetchall()
    
    # Column names
    columns = [col[0] for col in cursor.description]
    
    conn.close()

    if not rows:
        return []

    result = [dict(zip(columns, row)) for row in rows]
    
    return result




# Tool3:Summarizing all expenses
@mcp.tool(
    name="summarize_expenses",
    description="Summarize expenses by category with optional filters"
)
def summarize_expenses(
    start_date: str | None = None,
    end_date: str | None = None,
    category: str | None = None
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            category,
            SUM(amount) AS total_amount,
            COUNT(*) AS record_count
        FROM expenses
        WHERE 1=1
    """
    params = []

    # Optional date filters
    if start_date:
        query += " AND expense_date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND expense_date <= ?"
        params.append(end_date)

    # Optional category filter
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " GROUP BY category ORDER BY category ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    columns = [col[0] for col in cursor.description]
    conn.close()

    if not rows:
        return []

    return [dict(zip(columns, row)) for row in rows]



#now adding resource to my mcp 
#so that he can refer to define sub categories in case if user not providing subcategory
@mcp.resource("expenses://categories", mime_type="application/json")
def get_categories():
    with open(CAT_PATH, "r", encoding="utf-8") as f:
        return f.read()



# Entry point
if __name__ == "__main__":
    mcp.run(transport="http",host = "0.0.0.0",port=8000)

