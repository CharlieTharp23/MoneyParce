import matplotlib.pyplot as plt
import numpy as np
import io
import base64


class ChartBuilder:
    def __init__(self, x_label, y_label, title):
        self.figure, self.axes = plt.subplots()
        self.axes.set_xlabel(x_label)
        self.axes.set_ylabel(y_label)
        self.axes.set_title(title)

    def add_data(self, x, y, label=None):
        self.axes.plot(x, y, label=label)
        if label:
            self.axes.legend()

    def show(self):
        plt.show()

    def save(self, filename):
        self.figure.savefig(filename)
    
    def render_to_base64(self):
        buffer = io.BytesIO()
        self.figure.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        return graphic


class SpendingOverTimeChart(ChartBuilder):
    def add_data(self, dates, amounts, label=None):
        self.axes.plot(dates, amounts, label=label)
        if label:
            self.axes.legend()

class CategoryBreakdownChart(ChartBuilder):
    def add_data(self, category_totals: dict):
        labels = category_totals.keys()
        amounts = category_totals.values()
        self.axes.pie(amounts, labels=labels, autopct="%1.1f%%")

class IncomeVsExpenseChart(ChartBuilder):
    def add_data(self, labels, amounts):
        x = np.arange(len(labels))
        self.axes.bar(x, amounts)
        self.axes.set_xticks(x)
        self.axes.set_xticklabels(labels)
