from flask import Flask, request, Response, stream_with_context
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import json
import time
import re
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
                print('检测到研究团队消息:', step['research_team']['messages'])
                for message in step['research_team']['messages']:
                    if hasattr(message, 'content'):
                        # 处理研究团队消息
                        # 按空格分割但保留换行符
                        # 按空格和换行符分割，同时保留换行符作为单词
                        research_words = []
                        for token in re.split(r'(\n)', message.content):
                            if token == '\n':
                                research_words.append(token)
                            else:
                                # 按空格分割并过滤空字符串
                                research_words.extend([word for word in token.split(' ') if word])
                        for i, word in enumerate(research_words):
                            # 流式输出单个单词
                            if i == 0:
                                # 第一个单词，添加前缀
                                yield f"data: [{message.name}] {word}\n\n"
                            elif i == len(research_words) - 1:
                                # 最后一个单词，添加后缀
                                yield f"data: {word}<br>\n\n"
                            elif word == '\n':
                                # 文中换行符
                                yield f"data: <br>\n\n"
                            else:
                                # 中间单词，直接输出
                                yield f"data: {word}\n\n"
                            # print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 研究团队单词: {word}")
                            time.sleep(0.1)  # 单词间短暂延迟
            # 检查写作团队的消息
            if 'writing_team' in step and 'messages' in step['writing_team']:
                print('检测到写作团队消息:', step['writing_team']['messages'])
                for message in step['writing_team']['messages']:
                    if hasattr(message, 'content'):
                        # 处理写作团队消息
                        # 按空格分割但保留换行符
                        # 按空格和换行符分割，同时保留换行符作为单词
                        writing_words = []
                        for token in re.split(r'(\n)', message.content):
                            if token == '\n':
                                writing_words.append(token)
                            else:
                                # 按空格分割并过滤空字符串
                                writing_words.extend([word for word in token.split(' ') if word])
                        for i, word in enumerate(writing_words):
                            # 流式输出单个单词
                            if i == 0:
                                # 第一个单词，添加前缀
                                yield f"data: [{message.name}] {word}\n\n"
                            elif i == len(writing_words) - 1:
                                # 最后一个单词，添加后缀
                                yield f"data: {word}<br>\n\n"
                            elif word == '\n':
                                # 文中换行符
                                yield f"data: <br>\n\n"
                            else:
                                # 中间单词，直接输出
                                yield f"data: {word}\n\n"
                            # print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 写作团队单词: {word}")
                            time.sleep(0.1)  # 单词间短暂延迟
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