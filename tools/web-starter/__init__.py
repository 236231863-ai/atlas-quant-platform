class WebStarter:
    def __init__(self): self._port=8000; self._host='127.0.0.1'
    def configure(self,host='127.0.0.1',port=8000): self._host=host; self._port=port
    def start(self): return f'Web server at http://{self._host}:{self._port}'
    def health_check(self): return True
