import numpy as np
import matplotlib.pyplot as plt

def figgen(width,height,scale,**kwargs):
    # kwargs = {{}}
    fig = plt.figure(figsize=(width*scale,height*scale),**kwargs)
    return fig
