import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from matplotlib.widgets import Slider, TextBox, Button

# Setup the figure and axis
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.4)

# Parameters
initial_n_particles = 50
prism_length = 10
prism_height = 2
filter_position = prism_length / 2
initial_tail_transparency = 0.1
initial_tail_length = 400
initial_frame_rate = 50
initial_speed = 0.1

# Axis for the particles
particles_ax = plt.axes([0.1, 0.4, 0.8, 0.5])
rect = Rectangle((0, 0), prism_length, prism_height, linewidth=1, edgecolor='r', facecolor='lightgray')
particles_ax.add_patch(rect)
particles_ax.set_xlim(-1, prism_length + 1)
particles_ax.set_ylim(-1, prism_height + 1)
particles_ax.set_aspect('equal')
filter_line = particles_ax.axvline(x=filter_position, color='black', linewidth=2)

# Controls for simulation parameters
text_box_ax = plt.axes([0.1, 0.35, 0.15, 0.03])
text_box = TextBox(text_box_ax, 'Number of Particles', initial=str(initial_n_particles))

transparency_slider_ax = plt.axes([0.1, 0.30, 0.22, 0.03])
transparency_slider = Slider(transparency_slider_ax, 'Tail Transparency', 0.01, 0.5, valinit=initial_tail_transparency)

tail_length_slider_ax = plt.axes([0.1, 0.25, 0.22, 0.03])
tail_length_slider = Slider(tail_length_slider_ax, 'Tail Length', 100, 1000, valinit=initial_tail_length)

frame_rate_slider_ax = plt.axes([0.1, 0.20, 0.22, 0.03])
frame_rate_slider = Slider(frame_rate_slider_ax, 'Frame Rate', 10, 100, valinit=initial_frame_rate)

speed_slider_ax = plt.axes([0.1, 0.15, 0.22, 0.03])
speed_slider = Slider(speed_slider_ax, 'Particle Speed', 0.1, 1.0, valinit=initial_speed, valfmt='%.2f')

# Buttons to control simulation
go_button_ax = plt.axes([0.8, 0.35, 0.1, 0.05])
go_button = Button(go_button_ax, 'Go')

stop_button_ax = plt.axes([0.7, 0.35, 0.1, 0.05])
stop_button = Button(stop_button_ax, 'Stop')

reset_button_ax = plt.axes([0.6, 0.35, 0.1, 0.05])
reset_button = Button(reset_button_ax, 'Reset')

# Global variables for dynamics
scatter = None
trail_positions = []
trail_colors = []
ani = None  # Animation handle

def init_positions(n):
    positions = np.zeros((int(n), 2))
    positions[:, 1] = np.linspace(0, prism_height, int(n))
    return positions

def update(frame):
    global positions, colors, trail_positions, trail_colors
    speed = speed_slider.val
    positions[:, 0] += diffusion_rates * speed + np.random.normal(0, speed / 10, size=len(positions))
    for i, pos in enumerate(positions):
        if pos[0] >= filter_position and i % 2 == 0:
            positions[i, 0] = min(positions[i, 0], filter_position)
        if pos[0] >= prism_length:
            positions[i, 0] = prism_length
        if pos[0] > filter_position:
            colors[i] = '#ff7f50'
    
    scatter.set_offsets(positions)
    scatter.set_color(colors)

    tail_length = int(tail_length_slider.val)
    if len(trail_positions) > tail_length:
        del trail_positions[:len(positions)]
        del trail_colors[:len(colors)]

    trail_positions.append(positions.copy().tolist())  # Append current positions to trail positions
    trail_colors.append(colors.copy())  # Append current colors to trail colors

    if trail_positions:
        trails = particles_ax.scatter([pos[0] for pos in trail_positions[-1]], [pos[1] for pos in trail_positions[-1]], c=trail_colors[-1], alpha=transparency_slider.val)
        return scatter, trails
    return scatter,

def go_button_on_clicked(mouse_event):
    global ani, positions, diffusion_rates, colors, scatter, trail_positions, trail_colors
    n = int(text_box.text)
    positions = init_positions(n)
    diffusion_rates = np.random.rand(n) * 0.1 + 0.05
    colors = ['red'] * n
    trail_positions = []  # Clear previous trails when starting new animation
    trail_colors = []
    if scatter:
        scatter.remove()
    scatter = particles_ax.scatter(positions[:, 0], positions[:, 1], c=colors)
    if ani:
        ani.event_source.stop()
    ani = FuncAnimation(fig, update, frames=np.arange(100), interval=int(1000/frame_rate_slider.val), blit=False)
    ani._start()

def stop_button_on_clicked(mouse_event):
    global ani
    if ani:
        ani.event_source.stop()

def reset_button_on_clicked(mouse_event):
    global ani, trail_positions, trail_colors, scatter
    if ani:
        ani.event_source.stop()
    trail_positions = []
    trail_colors = []
    if scatter:
        scatter.remove()
    particles_ax.clear()
    particles_ax.add_patch(rect)
    particles_ax.axvline(x=filter_position, color='black', linewidth=2)
    particles_ax.set_xlim(-1, prism_length + 1)
    particles_ax.set_ylim(-1, prism_height + 1)
    particles_ax.set_aspect('equal')

go_button.on_clicked(go_button_on_clicked)
stop_button.on_clicked(stop_button_on_clicked)
reset_button.on_clicked(reset_button_on_clicked)

plt.show()
