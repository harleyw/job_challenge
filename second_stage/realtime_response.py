from flask import Flask, Response, stream_with_context, request
import time

def stream_generator():
    """需要访问请求上下文的流式生成器"""
    # 从request中获取参数（如`user_id`）
    #user_id = request.args.get('user_id', 'unknown')
    user_id = request.json.get('question', '')
    # 逐次生成数据
    while True:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        # 使用请求参数生成响应内容
        yield f"data: User {user_id} - {current_time}\n\n"
        time.sleep(1)

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def stream_response():
    # 使用stream_with_context包裹生成器，传递请求上下文
    return Response(
        stream_with_context(stream_generator()),  # 关键：包裹生成器
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)


