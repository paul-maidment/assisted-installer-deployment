import uuid
import requests
import tarfile
import os

class RemoteTarFile:

    def __init__(self, url, tmp_dir="/tmp"):
        response = requests.get(url, stream=True)
        file = tarfile.open(fileobj=response.raw, mode="r|*")
        self._temp_dir = os.path.join(tmp_dir, str(uuid.uuid4()))
        os.mkdir(self._temp_dir)
        file.extractall(path=self._temp_dir)
        self._find_and_extract_archives(self._temp_dir)

    def _find_and_extract_archives(self, root_path):
        paths = os.listdir(root_path)
        for path in paths:
            fullPath = os.path.join(root_path, path)
            extension = os.path.splitext(path)[1]
            if os.path.isdir(fullPath):
                self.find_and_extract_archives(fullPath)
            elif extension.lower() == ".gz":
                destination = os.path.join(root_path, path.replace(extension, "").replace(".tar", "").replace(".gz", ""))
                os.mkdir(destination)
                tar_file = tarfile.open(fullPath)
                tar_file.extractall(destination)
                tar_file.close()
                os.remove(fullPath)

if __name__ == "__main__":
    url = "http://assisted-logs-collector.usersys.redhat.com/files/2023-02-28_16-38-31_034e3ca1-121e-4a8b-9112-d86f25ec30fc/cluster_034e3ca1-121e-4a8b-9112-d86f25ec30fc_logs.tar"
    remoteTarFile = RemoteTarFile(url)
