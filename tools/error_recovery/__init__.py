class ErrorRecovery:
    def __init__(self):
        self._log=[]
    def diagnose(self):
        return {'status':'ok','issues':[]}
    def recover(self,issue):
        self._log.append(f'Recovered: {issue}')
        return True
    def get_log(self):
        return self._log
