from huggingface_hub import HfApi


def pull_from_hf(
    hf_token: str,
    hf_repo_id: str,
    filename: str,
    save_dir: str
):
    # download
    hf_api = HfApi(token=hf_token)
    hf_api.hf_hub_download(
        repo_id=hf_repo_id,
        repo_type="dataset",
        filename=filename,
        cache_dir="hf_cache",
        local_dir=save_dir,
        local_dir_use_symlinks=False
    )