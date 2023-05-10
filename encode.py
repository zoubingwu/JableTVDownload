import os
import subprocess
import multiprocessing

def ffmpegEncode(folder_path, file_name, action):
    thread_count = multiprocessing.cpu_count()
    if action == 0: #不轉檔
        return
    elif action == 1: #GPU轉檔
        os.chdir(folder_path)
        try:
            subprocess.call(['ffmpeg', '-i', f'{file_name}.mp4','-c:v', 'h264_videotoolbox', '-b:v', '10000K',
                                '-threads', thread_count, f'f_{file_name}.mp4'])
            os.remove(os.path.join(folder_path, f'{file_name}.mp4'))
            os.rename(os.path.join(folder_path, f'f_{file_name}.mp4'), os.path.join(folder_path, f'{file_name}.mp4'))
            print("轉檔成功!")

        except:
            print("轉檔失敗!")
    elif action == 2: #CPU轉檔
        os.chdir(folder_path)
        try:
            subprocess.call(['ffmpeg', '-i', f'{file_name}.mp4', '-c:v', 'libx264', '-b:v', '3M',
                            '-threads', thread_count, '-preset', 'superfast', f'f_{file_name}.mp4'])
            os.remove(os.path.join(folder_path, f'{file_name}.mp4'))
            os.rename(os.path.join(folder_path, f'f_{file_name}.mp4'), os.path.join(folder_path, f'{file_name}.mp4'))
            print("轉檔成功!")

        except:
            print("轉檔失敗!")
    else:
        return
