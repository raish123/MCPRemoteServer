from fastmcp import FastMCP

mcp = FastMCP.as_proxy(
    "https://expense-tracker-mcp-serv.fastmcp.app/mcp",
    name = "expense Proxy server"
)



if __name__ == "__main__":
    mcp.run()#stdio