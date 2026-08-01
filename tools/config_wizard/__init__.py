class ConfigWizard:
    def __init__(self):
        self._config={'db_url':'sqlite:///atlas.db','log_level':'INFO','port':8000}
    def get_config(self):
        return self._config
    def update(self,k,v):
        self._config[k]=v
        return True
    def validate(self):
        return all(v is not None for v in self._config.values())
