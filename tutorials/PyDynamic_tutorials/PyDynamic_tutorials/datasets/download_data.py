from typing import Optional

from download import download


def download_tutorial_data(
    url: str, replace: Optional[bool] = False, verbose: Optional[bool] = True
):
    """Download a file to the datasets subfolder and return its file path

    Parameters
    ----------
    url : str
        The full URL to download the file from without leading '/'.
    replace : bool, optional
        If the file should be replaced in case it was alreaady loaded previously.
    verbose : bool, optional
        Print progress bar and other information if True (default) or not if False.
    """
    # Construct the file path to the repository's datasets' subfolder from the
    # filename at the end of the URL.
    filename = f"../datasets/{url.split('/')[-1]}"
    if verbose:
        print(
            f"Checking if file {filename} is already present or download "
            f"it from {url} otherwise:"
        )
    return download(url, filename, replace=replace, verbose=verbose)
