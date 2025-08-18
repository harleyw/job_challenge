from flask import Flask, request, Response, stream_with_context
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import json
import time
import setup

# 尝试导入LangGraph相关模块
try:
    from teams_orchestrate import super_graph
    from langchain_core.messages import HumanMessage
    has_langgraph = True
except ImportError as e:
    print(f"Error importing LangGraph modules: {e}")
    has_langgraph = False

# 定义流式响应生成器
def generate_response():
    question = request.json.get('question', '')

    if not has_langgraph:
        yield "data: Error: LangGraph modules not found. Please check your installation.\n\n"
        return

    try:
        # 初始化对话状态
        state = {'messages': [HumanMessage(content=question)]}

        # 逐步处理响应
        for step in super_graph.stream(state):
            # 检查研究团队的消息
            if 'research_team' in step and 'messages' in step['research_team']:
                #print('检测到研究团队消息:', step['research_team']['messages'])
                for message in step['research_team']['messages']:
                    if hasattr(message, 'content'):
                        # 流式输出内容 (符合SSE标准)
                        yield f"data: [{message.name}] {message.content}\n\n"
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 研究团队消息内容:", message.content)
                        time.sleep(1)  # 模拟实时响应
            # 检查写作团队的消息
            if 'writing_team' in step and 'messages' in step['writing_team']:
                #print('检测到写作团队消息:', step['writing_team']['messages'])
                for message in step['writing_team']['messages']:
                    if hasattr(message, 'content'):
                        # 流式输出内容 (符合SSE标准)
                        yield f"data: [{message.name}] {message.content}\n\n"
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 写作团队消息内容:", message.content)
                        time.sleep(1)  # 模拟实时响应
    except Exception as e:
        yield f"data: Error processing request: {str(e)}\n\n"
    print("=============================done=============================")

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')

    if not question:
        return Response(json.dumps({'error': 'Question is required'}), status=400, mimetype='application/json')

    # 返回流式响应
    # 使用stream_with_context包装生成器，确保请求上下文在流式响应期间保持活动
    return Response(
        stream_with_context(generate_response()),  # 生成器函数
        status=200,
        mimetype='text/event-stream',  # SSE格式的MIME类型
        headers={
            'Cache-Control': 'no-cache',  # 禁止缓存
            'X-Accel-Buffering': 'no'     # 禁止反向代理（如Nginx）缓冲
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)