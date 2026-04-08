import os
import shutil
import zipfile

def inject_dll(zip_path, target_dir):
    try:
        # First, ensure we have write permissions or handle "In Use"
        # We find files in the target_dir that match the typical pattern (nvngx_dlss*.dll)
        # However, the zip may contain a specific name.
        
        # 1. Inspect zip
        dll_name_in_zip = None
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for zip_info in zip_ref.infolist():
                if zip_info.filename.lower().endswith('.dll') and "nvngx_dlss" in zip_info.filename.lower():
                    dll_name_in_zip = zip_info.filename
                    break
            
            if not dll_name_in_zip:
                raise Exception("No valid DLSS DLL found in the downloaded archive.")

            # Identify target file name based on what's in the zip
            target_file_path = os.path.join(target_dir, os.path.basename(dll_name_in_zip))
            old_file_path = target_file_path[:-4] + ".old"
            
            # 2. Backup existing
            if os.path.exists(target_file_path):
                # If an old backup already exists, remove it first
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except OSError:
                        raise Exception(f"Failed to remove previous backup {old_file_path}. Is it in use?")
                        
                try:
                    os.rename(target_file_path, old_file_path)
                except OSError:
                    raise Exception(f"Failed to backup {target_file_path}. The file might be in use by the game.")

            # 3. Extract new file directly into target dir
            # zip_ref.extract limits to specific file, but might extract dirs too. Better to read and write.
            with zip_ref.open(dll_name_in_zip) as source, open(target_file_path, "wb") as target:
                shutil.copyfileobj(source, target)

        # 4. Verify
        if not os.path.exists(target_file_path):
            raise Exception("Verification failed: newly injected DLL is missing.")
            
        # 5. Cleanup temp zip
        try:
            os.remove(zip_path)
        except OSError:
            pass # Non-critical if temp file fails to remove
            
        return True, "Injection Successful."
        
    except Exception as e:
        return False, str(e)
