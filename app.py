import os.path
import shutil
import gradio as gr
import subprocess
import uuid
from data_preparation_mini import data_preparation_mini
from data_preparation_web import data_preparation_web
from demo_mini import interface_mini

# 自定义 CSS 样式
css = """
#video-output video {
    max-width: 300px;
    max-height: 300px;
    display: block;
    margin: 0 auto;
}
"""

video_dir_path = ""
# 假设你已经有了这两个函数
def data_preparation(video1, video2):
    global video_dir_path
    # 处理视频的逻辑
    video_dir_path = "video_data/{}".format(uuid.uuid4())
    data_preparation_mini(video1, video2, video_dir_path)
    data_preparation_web(video_dir_path)

    return "视频处理完成，保存至目录{}".format(video_dir_path)

def demo_mini(audio):
    global video_dir_path
    # 生成视频的逻辑
    audio_path = audio  # 解包元组
    wav_path = "video_data/tmp.wav"
    ffmpeg_cmd = "ffmpeg -i {} -ac 1 -ar 16000 -y {}".format(audio_path, wav_path)
    print(ffmpeg_cmd)
    os.system(ffmpeg_cmd)
    output_video_name = "video_data/tmp.mp4"
    asset_path = os.path.join(video_dir_path, "assets")
    interface_mini(asset_path, wav_path, output_video_name)
    return output_video_name  # 返回生成的视频文件路径

# 启动网页的函数
def launch_server():
    global video_dir_path
    asset_path = os.path.join(video_dir_path, "assets")
    target_path = os.path.join("web_demo", "static", "assets")

    # 如果目标目录存在，先删除
    if os.path.exists(target_path):
        shutil.rmtree(target_path)

    # 将 asset_path 目录下的所有文件拷贝到 web_demo/static/assets 目录下
    shutil.copytree(asset_path, target_path)

    # 启动 server.py
    subprocess.Popen(["python", "web_demo/server.py"])

    return "访问 http://localhost:8888/static/MiniLive.html"

# 定义 Gradio 界面
def create_interface():
    with gr.Blocks(css=css) as demo:
        # 标题
        gr.Markdown("# 视频处理与生成工具")

        # 第一部分：上传静默视频和说话视频
        gr.Markdown("## 第一部分：视频处理")
        gr.Markdown("""
        - **静默视频**：时长建议在 5-30 秒之间，嘴巴不要动，是主体视频。嘴巴如果有动作会影响效果，请认真对待。
        - **说话视频**：只需 1-5 秒，需要张嘴，作用是捕捉嘴巴内部的细节。
        """)
        with gr.Row():
            with gr.Column():
                video2 = gr.Video(label="上传静默视频", elem_id="video-output")
            with gr.Column():
                video1 = gr.Video(label="上传说话视频", elem_id="video-output")
        process_button = gr.Button("处理视频")
        process_output = gr.Textbox(label="处理结果")

        # 分隔线
        gr.Markdown("---")

        # 第二部分：上传音频文件并生成视频
        gr.Markdown("## 第二部分：测试语音生成视频")
        gr.Markdown("""
        - 上传音频文件后，点击“生成视频”按钮，程序会调用 `demo_mini` 函数完成推理并生成视频。
        - 此步骤用于初步验证结果。网页demo请执行第三步。
        """)
        # audio = gr.Audio(label="上传音频文件")

        with gr.Row():
            with gr.Column():
                audio = gr.Audio(label="上传音频文件", type="filepath")
                generate_button = gr.Button("生成视频")
            with gr.Column():
                video_output = gr.Video(label="生成的视频", elem_id="video-output")

        # 分隔线
        gr.Markdown("---")

        # 第三部分：启动网页
        gr.Markdown("## 第三部分：启动网页")
        gr.Markdown("""
        - 点击“启动网页”按钮后，会启动 `server.py`，提供一个模拟对话服务。
        - 在 `static/js/dialog.js` 文件中，找到第 35 行，将 `http://localhost:8888/eb_stream` 替换为您自己的对话服务网址。例如：
          ```bash
          https://your-dialogue-service.com/eb_stream
          ```
        - `server.py` 提供了一个模拟对话服务的示例。它接收 JSON 格式的输入，并流式返回 JSON 格式的响应。
        - 示例输入 JSON：
          ```bash
          {
              "prompt": "用户输入的对话内容"
          }
          ```
        - 示例输出 JSON（流式返回）：
          ```bash
          {
              "text": "返回的部分对话文本",
              "audio": "base64编码的音频数据",
              "endpoint": false  // 是否为对话的最后一个片段，true表示结束
          }
          ```
        - **注意**：本项目使用了 WebCodecs API，该 API 仅在安全上下文（HTTPS 或 localhost）中可用。因此，在部署或测试时，请确保您的网页在 HTTPS 环境下运行，或者使用 localhost 进行本地测试。
        """)
        launch_button = gr.Button("启动网页")
        launch_output = gr.Textbox(label="启动结果")

        # 绑定按钮点击事件
        process_button.click(data_preparation, inputs=[video1, video2], outputs=process_output)
        generate_button.click(demo_mini, inputs=audio, outputs=video_output)
        launch_button.click(launch_server, outputs=launch_output)

    return demo

# 创建 Gradio 界面并启动
if __name__ == "__main__":
    demo = create_interface()
    demo.launch()