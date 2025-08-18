from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from pprint import pprint
import asyncio

# 导入现有的问答系统组件
import setup
from graph_build import app as graph_app

# 初始化 FastAPI 应用
app = FastAPI(title="问答系统", description="基于 LangGraph 的问答系统")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask", response_class=HTMLResponse)
async def ask_question(request: Request, question: str = Form(...)):
    # 运行问答图
    inputs = {"question": question}
    generation = None
    
    # 执行图并获取结果
    for output in graph_app.stream(inputs):
        for key, value in output.items():
            if key == "generate" and "generation" in value:
                generation = value["generation"]
                break
        if generation:
            break
    
    # 如果没有生成结果，使用默认值
    if not generation:
        generation = "抱歉，无法回答这个问题。"
    
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "question": question, "response": generation}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)