class ReleasePackage:
    def __init__(self):
        self._artifacts=[]
    def build(self,version):
        self._artifacts.append(f'atlas-v{version}.exe')
        return self._artifacts
    def list_artifacts(self):
        return self._artifacts
    def get_latest(self):
        return self._artifacts[-1] if self._artifacts else None
