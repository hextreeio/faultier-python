import plotly.graph_objs as go
import serial
import struct
import os
from sys import platform
from IPython.display import clear_output
import random
import time
import matplotlib.pyplot as plt
from tqdm.notebook import trange, tqdm
import pickle

class GlitchData:
    def __init__(self, name, color="gray", alpha=0.3, zorder=1, render=True):
        self.name = name
        self.delays = []
        self.pulses = []
        self.color = color
        self.alpha = alpha
        self.zorder = zorder
        self.render = render
        pass

    def add(self, delay, pulse):
        self.delays.append(delay)
        self.pulses.append(pulse)
    
    def plot_delays(self):
        # Create histogram
        plt.hist(self.delays, bins='auto', color='blue', alpha=0.7, rwidth=0.85)

        # Add title and labels
        plt.title('Distribution of delays')
        plt.xlabel('Delay')
        plt.ylabel('Frequency')

        # Show plot
        plt.grid(axis='y', alpha=0.75)
        plt.show()


    def plot_pulses(self):
        # Create histogram
        plt.hist(self.pulses, bins='auto', color='blue', alpha=0.7, rwidth=0.85)

        # Add title and labels
        plt.title('Distribution of pulses')
        plt.xlabel('Pulse')
        plt.ylabel('Frequency')

        # Show plot
        plt.grid(axis='y', alpha=0.75)
        plt.show()
    

class GlitchDataCollection:
    def __init__(self):
        self.data = {}
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0
        pass

    def add_data(self, key, name, color="gray", alpha=0.3, zorder=1, render=True):
        self.data[key] = GlitchData(name, color=color, alpha=alpha, zorder=zorder, render=render)
    
    def add(self, key, delay, pulse):
        if not self.min_x or self.min_x > delay:
            self.min_x = delay
        if not self.max_x or self.max_x < delay:
            self.max_x = delay
        if not self.min_y or self.min_y > pulse:
            self.min_y = pulse
        if not self.max_y or self.max_y < pulse:
            self.max_y = pulse
        self.data[key].add(delay, pulse)

    def get_data(self, key):
        return self.data[key]

    def plot(self, x=None, y=None):
        if not x:
            x = [self.min_x, self.max_x]
        if not y:
            y = [self.min_y, self.max_y]
            
        fig, ax = plt.subplots()
        for k in self.data.keys():
            glitch_data = self.data[k]
            alpha = 0.3
            zorder = 1
            ax.scatter(glitch_data.delays, glitch_data.pulses, label=glitch_data.name, alpha=glitch_data.alpha, zorder=glitch_data.zorder, c=glitch_data.color, marker="x")
        ax.legend()
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                fancybox=True, shadow=True, ncol=5)
        ax.grid(True)
        plt.xlim(x[0], x[1])
        plt.ylim(y[0], y[1])
        clear_output(wait=True)
        plt.show()

    def save(self, filename):
        f = open(filename, "wb")
        pickle.dump(self, f)

    @staticmethod
    def load(filename):
        f = open(filename, "rb")
        return pickle.load(f)
