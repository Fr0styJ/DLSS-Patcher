import requests
from bs4 import BeautifulSoup
import tempfile
import os

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

URLS = {
    "DLSS": "https://www.techpowerup.com/download/nvidia-dlss-dll/",
    "Ray Reconstruction": "https://www.techpowerup.com/download/nvidia-dlss-3-ray-reconstruction-dll/",
    "Frame Generation": "https://www.techpowerup.com/download/nvidia-dlss-3-frame-generation-dll/"
}

def get_latest_versions(dl_type, max_versions=5):
    url = URLS.get(dl_type)
    if not url:
        return []

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {dl_type} page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    versions = []

    # TechPowerUp structures versions in blocks, usually finding titles like "NVIDIA DLSS DLL x.y.z"
    # We look for form elements with action to the download page or having an "id" field
    blocks = soup.select('.version')
    for block in blocks[:max_versions]:
        title_elem = block.select_one('.title')
        if not title_elem:
            title_elem = block.select_one('h3')

        title = title_elem.text.strip() if title_elem else "Unknown Version"

        # Find the download id
        id_input = block.select_one('input[name="id"]')
        if id_input:
            download_id = id_input.get('value')
            versions.append({
                'version': title,
                'id': download_id,
                'type': dl_type
            })

    # Fallback if structure changed
    if not versions:
        # Just creating dummy structure for now as fallback
        pass
        
    return versions

def download_file(dl_type, version_id, progress_callback=None):
    # Need to get a server first
    main_url = URLS.get(dl_type)
    
    # Send a POST with the ID to get mirror list
    mirrors_response = requests.post(main_url, data={"id": version_id}, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(mirrors_response.text, 'html.parser')
    
    # Find the server form
    server_form = None
    forms = soup.find_all('form')
    for f in forms:
        if f.select_one('input[name="server_id"]') or f.select_one('button[name="server_id"]'):
            server_form = f
            break

    if not server_form:
        raise Exception("Could not find download server form.")

    server_input = server_form.select_one('input[name="server_id"]') or server_form.select_one('button[name="server_id"]')
    server_id = server_input['value']
    
    # POST to get the actual file
    download_req = requests.post(main_url, data={"id": version_id, "server_id": server_id}, headers=HEADERS, stream=True, timeout=15)
    download_req.raise_for_status()

    # Save to temp
    total_length = download_req.headers.get('content-length')
    
    temp_fd, temp_path = tempfile.mkstemp(suffix=".zip")
    with os.fdopen(temp_fd, 'wb') as f:
        dl = 0
        total_length = int(total_length) if total_length else 0
        for data in download_req.iter_content(chunk_size=4096):
            if not data:
                break
            f.write(data)
            dl += len(data)
            if total_length and progress_callback:
                progress_callback(dl / total_length)

    return temp_path
