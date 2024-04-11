import os
import shutil
import pandas as pd
from data4co import compress_folder
from huggingface_api import pull_from_hf


def download_video_links(hf_token: str, filename: str, save_dir: str):
    # check save dir
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    # download
    pull_from_hf(
        hf_token=hf_token,
        hf_repo_id="OpenVideo/Panda-70M-Original-Links",
        filename=filename,
        save_dir=save_dir
    )
    

def download_videos_by_csv(
    csv_file_path: str,
    save_dir: str, 
    targz_filename: str,
):
    import youtube_dl
    
    # path/dir
    folder_name = targz_filename.replace(".tar.gz", "")
    download_videos_dir = os.path.join(save_dir, folder_name, "download_raw")    
    log_path = os.path.join(download_videos_dir, "log.txt")
    targz_path = os.path.join(save_dir, targz_filename)
    
    # make dirs
    if not os.path.exists(download_videos_dir):
        os.makedirs(download_videos_dir)
    
    # read from csv
    csv_filename = os.path.basename(csv_file_path)
    shutil.copy(src=csv_file_path, dst=os.path.join(download_videos_dir, csv_filename))
    data = pd.read_csv(csv_file_path)
    links = data["url"].tolist()
    videos_id = data["videoID"].to_list()    

    failed_links = [] # record failed links
    for link, video_id in zip(links, videos_id):
        # check if downloaded
        video_save_path = os.path.join(download_videos_dir, video_id[1:]+".mp4")
        if os.path.exists(video_save_path):
            continue
        
        # download
        ydl_opts = {
            'format': 'best',
            'quiet': False,
            'outtmpl': os.path.join(download_videos_dir, video_id[1:]+".mp4"),
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([link])
            except:
                failed_links.append(link)

    # delete videos larger than 100MB
    video_files = os.listdir(download_videos_dir)
    delete_videos = []
    for file in video_files:
        file_path = os.path.join(download_videos_dir, file)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert to megabytes
        if file_size_mb > 500:
            delete_videos.append(file_path)
            os.remove(file_path)
    
    # Write  to log file
    with open(log_path, 'w') as file:
        file.write('Fail to download\n')
        file.write('\n'.join(failed_links))
        file.write('Delete videos larger than 500MB\n')
        file.write('\n'.join(failed_links))
    
    compress_folder(download_videos_dir, targz_path)