import os
import time
import shutil
import pandas as pd
import gradio as gr
from vidfetch import youtube_dl_install_helper, push_to_hf
from panda70m_downloader import download_video_links, download_videos_by_csv


SAVE_CSV_DIR = "panda70m_csv"
SAVE_VIDEOS_DIR = "panda70m_videos"

def handle(
    hf_token: str, 
    filename: str, 
):
    try:
        import youtube_dl
    except:
        youtube_dl_install_helper(hf_token=hf_token)
        import youtube_dl
    
    download_video_links(hf_token=hf_token, filename=filename, save_dir=SAVE_CSV_DIR)
    
    # devide .csv to 100 files and download
    csv_path = os.path.join(SAVE_CSV_DIR, filename)
    data = pd.read_csv(csv_path)
    for idx in range(len(data) // 100):
        begin_idx = idx * 100
        end_idx = idx * 100 + 100
        part_data = data[begin_idx : end_idx]
        part_filename = filename.replace(".csv", "") + "_{:06d}_{:06d}.csv".format(begin_idx, end_idx)
        targz_filename = part_filename.replace(".csv", ".tar.gz")
        part_save_path = os.path.join(SAVE_CSV_DIR, part_filename)
        part_data.to_csv(part_save_path)
        download_videos_by_csv(
            csv_file_path=part_save_path,
            save_dir=SAVE_VIDEOS_DIR,
            targz_filename=targz_filename
        )
        push_to_hf(
            hf_token=hf_token,
            hf_repo_id="OpenVideo/Panda-70M-raw",
            file_path=os.path.join(SAVE_VIDEOS_DIR, targz_filename),
            path_in_repo=targz_filename
        )
        shutil.rmtree(SAVE_VIDEOS_DIR)
        

with gr.Blocks() as demo:
    gr.Markdown(
        '''
        Panda70M-Downloader
        '''
    )
    hf_token = gr.Textbox(label="HuggingFace Token")
    filename = gr.Textbox(label="csv name")

    with gr.Row():
        button = gr.Button("Submit", variant="primary")
        clear = gr.Button("Clear")

    button.click(
        handle, 
        [hf_token, filename], 
        outputs=None
    )


if __name__ == "__main__":
    demo.launch(debug = True)