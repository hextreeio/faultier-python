import time        
import plotly.graph_objs as go
def update_vline_position(fig, old_x, new_x):
    for shape in fig.layout.shapes:
        if shape.type == 'line' and shape.x0 == old_x and shape.x1 == old_x:
            shape.update(x0=new_x, x1=new_x)
            break

class LivePlot:
    def __init__(self):
        self.fig = go.FigureWidget(data=[go.Scatter(y=[])])
        self.fig.update_layout(yaxis=dict(range=[0, 1]))
        self.fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
        )
        # vline = self.fig.add_vline(x=200, line_width=1, line_dash="dash", line_color="red")
        self.vline_x = 200
        display(self.fig)
    
    def update(self, data):
        """
        Updates the live figure.

        :param data: Takes the data in the format [5, 3, 2, 1, ...]
        """

        self.fig.data[0].y = data

    def update_vline(self, x):
        """
        Updates the vertical marker on the graph.

        :param data: Takes in the X position on which to place the marker.
        """

        update_vline_position(self.fig, old_x=self.vline_x, new_x=x)
        self.vline_x = x


class LiveMarkerPlotOld:
    def __init__(self):
        self.fig = go.FigureWidget(data=[
            go.Scatter(x=[0], y=[0], mode="markers"),
            go.Scatter(x=[0], y=[0], mode="markers")
        ])
        # self.fig.update_layout(yaxis=dict(range=[0, 1]))
        self.fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Delay",
            yaxis_title="Pulse"
        )
        # vline = self.fig.add_vline(x=200, line_width=1, line_dash="dash", line_color="red")
        self.vline_x = 200
        display(self.fig)
    
    def update(self, data):
        """
        Updates the live figure.

        :param data: Takes the scatters in the format [[4000, 8], [3950, 4]]
        """
        
        x_values = [point[0] for point in data[0]]
        y_values = [point[1] for point in data[0]]

        self.fig.data[0].x = x_values
        self.fig.data[0].y = y_values

        x_values = [point[0] for point in data[1]]
        y_values = [point[1] for point in data[1]]

        self.fig.data[1].x = x_values
        self.fig.data[1].y = y_values


class LiveMarkerPlot:
    def __init__(self, gdc, x_range=None, y_range=None):
        """
        Initializes the LiveMarkerPlot.

        :param gdc: The data collection object.
        :param x_range: The range for the x-axis as a tuple (min, max), or None to auto-scale.
        :param y_range: The range for the y-axis as a tuple (min, max), or None to auto-scale.
        """
        self.gdc = gdc

        figure_widget_data = []
        for key in gdc.data:
            if gdc.data[key].render:
                figure_widget_data.append(
                    go.Scatter(x=[], y=[], mode="markers", name=gdc.data[key].name, marker_color=gdc.data[key].color),
                )

        self.fig = go.FigureWidget(data=figure_widget_data)

        # Set up x and y axis ranges if provided
        layout_options = {
            "margin": dict(l=20, r=20, t=20, b=20),
            "xaxis_title": "Delay",
            "yaxis_title": "Pulse"
        }
        if x_range:
            layout_options["xaxis"] = dict(range=x_range)
        if y_range:
            layout_options["yaxis"] = dict(range=y_range)

        self.fig.update_layout(**layout_options)
        self.vline_x = 200
        self.last_update = time.time()
        display(self.fig)


    
    def slow_update(self):
        if((time.time() - self.last_update) < 3):
            return
        self.update()

    def update(self):
        """
        Updates the live figure.

        :param data: Takes the scatters in the format [[4000, 8], [3950, 4]]
        """
        self.last_update = time.time()
        i = 0
        for k in self.gdc.data:
            data = self.gdc.get_data(k)
            if not data.render:
                continue
            x_values = data.delays
            y_values = data.pulses
            self.fig.data[i].x = x_values
            self.fig.data[i].y = y_values
            i += 1
