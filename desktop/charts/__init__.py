from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class BaseChart(FigureCanvas):
    def __init__(self, figsize=(5,3), dpi=100):
        self.fig = Figure(figsize=figsize, dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)

class FrequencyChart(BaseChart):
    def plot(self, data, labels=None):
        self.ax.clear(); self.ax.bar(range(len(data)), data, color="#5470c6")
        self.ax.set_title("Number Frequency")
        if labels: self.ax.set_xticks(range(len(data))); self.ax.set_xticklabels(labels, rotation=45, fontsize=8)
        self.draw()

class GapChart(BaseChart):
    def plot(self, data, labels=None):
        self.ax.clear(); self.ax.bar(range(len(data)), data, color="#91cc75")
        self.ax.set_title("Gap Distribution")
        if labels: self.ax.set_xticks(range(len(data))); self.ax.set_xticklabels(labels, rotation=45, fontsize=8)
        self.draw()

class ROICurve(BaseChart):
    def plot(self, data):
        self.ax.clear(); self.ax.plot(data, color="#ee6666", linewidth=2)
        self.ax.fill_between(range(len(data)), data, alpha=0.1, color="#ee6666")
        self.ax.set_title("ROI Curve"); self.ax.axhline(y=0, color="gray", linestyle="--")
        self.draw()

class DrawdownCurve(BaseChart):
    def plot(self, data):
        self.ax.clear(); self.ax.fill_between(range(len(data)), data, alpha=0.3, color="#fc8452")
        self.ax.set_title("Drawdown Curve"); self.ax.axhline(y=0, color="gray", linestyle="--")
        self.draw()

class RankingChart(BaseChart):
    def plot(self, labels, values):
        self.ax.clear(); self.ax.barh(range(len(values)), values, color="#73c0de")
        self.ax.set_yticks(range(len(values))); self.ax.set_yticklabels(labels)
        self.ax.set_title("Strategy Ranking"); self.draw()
