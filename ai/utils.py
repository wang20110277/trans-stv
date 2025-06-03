import yaml
import json
import os
import re
import subprocess
import cv2
import time
from pathlib import Path
from datetime import datetime


def load_prompt(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as file:
        prompt = file.read()
    return prompt.strip()


def read_json_file(file_path):
    """读取 JSON 文件并返回内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError as e:
            print(f"解析 JSON 时出错: {e}")
            return None

def write_json_file(file_path, data):
    """将数据写入 JSON 文件"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def read_config(config_path):
    with open(config_path, "r",encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def is_segment(tokens):
    if tokens[-1] in (",", ".", "?", "，", "。", "？", "！", "!", ";", "；", ":", "："):
        return True
    else:
        return False

def is_interrupt(query: str):
    for interrupt_word in ("停一下", "听我说", "不要说了", "stop", "hold on", "excuse me"):
        if query.lower().find(interrupt_word)>=0:
            return True
    return False

def extract_json_from_string(input_string):
    """提取字符串中的 JSON 部分"""
    pattern = r'(\{.*\})'
    match = re.search(pattern, input_string)
    if match:
        return match.group(1)  # 返回提取的 JSON 字符串
    return None


def merge_frames_with_audio(audio_path, fps=25):
    video_idx = audio_path.split("/")[-1].split("_")[-1].split(".")[0]
    print(f"[Real-time Inference] Merging frames with audio on {video_idx}")

    video_path = str(Path(audio_path).parent.parent / "videos" / f"{video_idx}.ts")
    frame_path = str(Path(audio_path).parent.parent / "frames" / f"{video_idx}")
    start_time = time.time()

    ffmpeg_command = [
        'ffmpeg',
        '-framerate', str(fps),
        '-i', f"{frame_path}/%08d.jpg",
        '-i', audio_path,
        '-c:v', 'libx264',
        '-shortest',
        '-f', 'mpegts',
        '-y',
        video_path
    ]
    subprocess.run(ffmpeg_command, check=True)
    print(f"[Real-time Inference] Merging frames with audio costs {time.time() - start_time}s")
    return video_path


def get_video_duration(video_path):
    print(cv2.__version__)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    return round(duration, 2)


def split_into_sentences(text, sentence_split_option):
    text = ''.join(text.splitlines())
    sentence_endings = re.compile(r'[。！？.!?]')
    sentences = sentence_endings.split(text)
    sentences = [s.strip() for s in sentences if s.strip()]
    split_count = int(sentence_split_option)
    return ['。'.join(sentences[i:i + split_count]) for i in range(0, len(sentences), split_count)]


def get_timestamp_str():
    fmt = "%Y%m%d_%H%M%S"
    current_time = datetime.now()
    folder_name = current_time.strftime(fmt)
    return folder_name


def merge_videos(video_folder_path, suffix='.mp4'):
    output_path = os.path.join(video_folder_path, f'merged_video{suffix}')
    file_list_path = os.path.join(video_folder_path, 'video_list.txt')

    def extract_index(filename):
        index = filename.split('.')[0].split('_')[-1]
        return int(index)

    with open(file_list_path, 'w') as file_list:
        ts_files = [f for f in os.listdir(video_folder_path) if f.endswith('.ts')]
        ts_files.sort(key=extract_index)

        for filename in ts_files:
            file_list.write(f"file '{filename}'\n")

    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', file_list_path,
        '-c', 'copy',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-y',
        output_path
    ]

    subprocess.run(ffmpeg_command, check=True)
    return output_path

