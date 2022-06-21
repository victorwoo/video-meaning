"""
Convert video to a mean image
"""
import os
import shutil

import cv2
import numpy as np

INPUT_DIR_NAME = "input"  # The name of the directory used to provide the input video.
KEYFRAMES_DIR_NAME = "keyframes"  # The name of the directory used to output the keyframes.
OUTPUT_DIR_NAME = "output"  # The name of the directory used to output mean images.
# Number of frames to be skipped in input (e.g 2 will calculate every third frame).
# FRAME_SKIPS = (0, 1, 9, 49, 99, 199, 499, 999)
FRAME_SKIPS = (999,)
WRITE_KEYFRAMES_TO_FILE = False  # Whether write keyframes to KEYFRAMES_DIR_NAME dir.
# noinspection SpellCheckingInspection
SUPPORTED_VIDEO_EXTS = (".mp4", ".mov", ".mkv")


def video_to_mean_image(video_file_name, frame_skip):
    """
Convert video to a mean image
    :param video_file_name: Video file name
    :param frame_skip: Number of frames to be skipped in input (e.g 2 will calculate every third frame)
    :return: None
    """
    accumulate_frame = None

    print(f"Analyzing {video_file_name} @ frame skip = {frame_skip}.")
    base_filename = os.path.splitext(video_file_name)[0]
    file_path = os.path.join(INPUT_DIR_NAME, video_file_name)

    # 创建关键帧目录
    keyframe_dir = os.path.join(KEYFRAMES_DIR_NAME, base_filename)

    if os.path.exists(keyframe_dir):
        # 如果关键帧目录存在则先删除目录
        shutil.rmtree(keyframe_dir)
    if WRITE_KEYFRAMES_TO_FILE:
        # 如果需要写入关键帧，则创建关键帧目录
        os.mkdir(keyframe_dir)

    frame_index = 0  # 当前帧号
    keyframe_index = 0  # 当前关键帧号

    camera = cv2.VideoCapture(file_path)
    try:
        while True:
            # 从视频文件中读取一帧
            success, current_frame = camera.read()

            if not success:
                # 读取不成功，通常是读完了。
                print("Read to end.")
                break

            # 首帧，提取画面宽度、高度、通道数（一般是 3）
            if frame_index == 0:
                frame_width = len(current_frame)  # 画面宽度
                frame_height = len(current_frame[0])  # 画面高度
                frame_channel_count = len(current_frame[0][0])  # 画面通道数（一般是 3，即 R、G、B）
                print(f"Width = {frame_width}, Height = {frame_height}, Channel Count = {frame_channel_count}")
                print("Keyframe information:")
                accumulate_frame = np.zeros((frame_width, frame_height, frame_channel_count), dtype=np.int32)

            # 读到一个关键帧
            if frame_index % (frame_skip + 1) == 0:
                accumulate_frame += current_frame  # 将当前帧每个像素的 RGB 值累积到一个"累积帧"中
                print("{:0>6d}: {}".format(keyframe_index, accumulate_frame[0][0]))

                # 将关键帧写入文件
                if WRITE_KEYFRAMES_TO_FILE:
                    key_frame_path = os.path.join(keyframe_dir, "{:0>6d}.jpg".format(frame_index))
                    cv2.imwrite(key_frame_path, current_frame)

                keyframe_index += 1
            frame_index += 1
    finally:
        camera.release()

    print(f"Total number of frames = {frame_index}, total number of keyframes = {keyframe_index}")
    new_image = accumulate_frame / keyframe_index
    new_image_path = os.path.join(OUTPUT_DIR_NAME, "{}@{}.jpg".format(base_filename, frame_skip + 1))
    print("Write mean image to {}.".format(new_image_path))
    cv2.imwrite(new_image_path, new_image)


# 查找视频文件
video_file_names = list(filter(
    lambda file:
    any(file.endswith(ext) for ext in SUPPORTED_VIDEO_EXTS),
    os.listdir(INPUT_DIR_NAME)))

# 创建 output 目录
if os.path.exists(OUTPUT_DIR_NAME):
    # 如果 output 目录存在则先删除目录
    shutil.rmtree(OUTPUT_DIR_NAME)
os.mkdir(OUTPUT_DIR_NAME)

for current_video_file_name in video_file_names:  # 遍历视频文件
    for current_frame_skip in FRAME_SKIPS:  # 遍历帧率
        video_to_mean_image(current_video_file_name, current_frame_skip)  # 视频转平均画面
