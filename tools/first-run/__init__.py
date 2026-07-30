class FirstRunExperience:
    STEPS=['welcome','profile','preferences','tutorial','complete']
    def __init__(self): self._step=0; self._completed=False; self._preferences={}
    def current_step(self): return self.STEPS[self._step] if self._step<len(self.STEPS) else 'done'
    def next(self):
        if self._step<len(self.STEPS)-1: self._step+=1
        else: self._completed=True
    def is_completed(self): return self._completed
    def set_preference(self,k,v): self._preferences[k]=v
