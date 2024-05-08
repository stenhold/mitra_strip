import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from matplotlib.widgets import Slider, TextBox, Button

# Set up the figure and axis for the animation
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.4)

# Define initial parameters for the simulation
initial_n_particles = 100  # Starting number of particles
prism_length = 10         # Length of the chamber or area
prism_height = 2          # Height of the chamber or area
filter_position = prism_length / 2  # Position of a barrier or filter
initial_tail_transparency = 0.05     # Initial transparency of trails
initial_tail_length = 100           # Maximum length of particle trails. Must be at least as large as number of particles for trails to show up at all. 
initial_frame_rate = 20             # Frames per second in the animation
initial_speed = 0.9                # Initial speed of particles

# Set up the axis for the particles
particles_ax = plt.axes([0.1, 0.4, 0.8, 0.5])
rect = Rectangle((0, 0), prism_length, prism_height, linewidth=1, edgecolor='r', facecolor='lightgray')
particles_ax.add_patch(rect)
particles_ax.set_xlim(-1, prism_length + 1)
particles_ax.set_ylim(-1, prism_height + 1)
particles_ax.set_aspect('equal')

# Create a vertical line to act as a filter or barrier in the simulation
filter_line = particles_ax.plot([filter_position, filter_position], [0, prism_height], 'black', linewidth=4)

# Create interactive controls for the simulation
text_box_ax = plt.axes([0.1, 0.35, 0.15, 0.03])
text_box = TextBox(text_box_ax, 'Number of Particles', initial=str(initial_n_particles))

transparency_slider_ax = plt.axes([0.1, 0.30, 0.22, 0.03])
transparency_slider = Slider(transparency_slider_ax, 'Tail Transparency', 0.01, 0.8, valinit=initial_tail_transparency)

tail_length_slider_ax = plt.axes([0.1, 0.25, 0.22, 0.03])
tail_length_slider = Slider(tail_length_slider_ax, 'Tail Length', 100, 1000, valinit=initial_tail_length)

frame_rate_slider_ax = plt.axes([0.1, 0.20, 0.22, 0.03])
frame_rate_slider = Slider(frame_rate_slider_ax, 'Frame Rate', 10, 100, valinit=initial_frame_rate)

speed_slider_ax = plt.axes([0.1, 0.15, 0.22, 0.03])
speed_slider = Slider(speed_slider_ax, 'Particle Speed', 0.1, 1.0, valinit=initial_speed, valfmt='%.2f')

# Initialize scatter plot for displaying trails
trails_scatter = particles_ax.scatter([], [], alpha=transparency_slider.val)

# Setup buttons to control the simulation
go_button_ax = plt.axes([0.8, 0.35, 0.1, 0.05])
go_button = Button(go_button_ax, 'Go')

stop_button_ax = plt.axes([0.7, 0.35, 0.1, 0.05])
stop_button = Button(stop_button_ax, 'Stop')

reset_button_ax = plt.axes([0.6, 0.35, 0.1, 0.05])
reset_button = Button(reset_button_ax, 'Reset')

# Variables to keep track of dynamic elements in the simulation
scatter = None  # Will hold the scatter plot object for particles
trail_positions = []  # List to store positions for trails
trail_colors = []  # List to store colors for trails
ani = None  # Will hold the animation object

def init_positions(n):
    """Generate initial positions for n particles evenly spaced vertically."""
    positions = np.zeros((int(n), 2))
    positions[:, 1] = np.linspace(0, prism_height, int(n))
    return positions

def update(frame):
    """Update function called by animation that moves particles and manages trails."""
    global positions, colors, trail_positions, trail_colors
    speed = speed_slider.val
    # Update positions based on speed and a small random component for realism
    positions[:, 0] += diffusion_rates * speed + np.random.normal(0, speed / 50, size=len(positions))
    new_positions = positions.copy()
    new_colors = colors.copy()
    for i, pos in enumerate(new_positions):
        if pos[0] >= filter_position and i % 2 == 0:
            new_positions[i, 0] = min(new_positions[i, 0], filter_position)
        if pos[0] >= prism_length:
            new_positions[i, 0] = prism_length
        if pos[0] > filter_position:
            new_colors[i] = '#ff7f50'
    
    scatter.set_offsets(new_positions)
    scatter.set_color(new_colors)

    # Append new positions and colors to trail data
    trail_positions.extend(new_positions.tolist())
    trail_colors.extend(new_colors)

    # Ensure the trail length doesn't exceed the set maximum
    tail_length = int(tail_length_slider.val)
    if len(trail_positions) > tail_length:
        del trail_positions[:len(new_positions)]
        del trail_colors[:len(new_colors)]

    if trail_positions:
        trails = particles_ax.scatter([pos[0] for pos in trail_positions], [pos[1] for pos in trail_positions], c=trail_colors, alpha=transparency_slider.val)
        return scatter, trails
    return scatter,

def go_button_on_clicked(mouse_event):
    """Handler for 'Go' button click that starts the simulation."""
    global ani, positions, diffusion_rates, colors, scatter, trail_positions, trail_colors
    n = int(text_box.text)
    positions = init_positions(n)
    diffusion_rates = np.random.normal(0.075, 0.005, n)
    colors = ['red'] * n
    if scatter and scatter in particles_ax.collections:
        scatter.remove()
    scatter = particles_ax.scatter(positions[:, 0], positions[:, 1], c=colors)
    trail_positions = []
    trail_colors = []
    if ani:
        ani.event_source.stop()
    ani = FuncAnimation(fig, update, frames=np.arange(100), interval=int(1000/frame_rate_slider.val), blit=False)
    ani._start()

def stop_button_on_clicked(mouse_event):
    """Handler for 'Stop' button click that stops the simulation."""
    global ani
    if ani:
        ani.event_source.stop()

def reset_button_on_clicked(mouse_event):
    """Handler for 'Reset' button click that resets the simulation to its initial state."""
    global ani, trail_positions, trail_colors, scatter
    if ani:
        ani.event_source.stop()
    trail_positions = []
    trail_colors = []
    if scatter and scatter in particles_ax.collections:
        scatter.remove()
    particles_ax.clear()
    particles_ax.add_patch(rect)
    particles_ax.plot([filter_position, filter_position], [0, prism_height], 'black', linewidth=5)
    particles_ax.set_xlim(-1, prism_length + 1)
    particles_ax.set_ylim(-1, prism_height + 1)
    particles_ax.set_aspect('equal')

# Link buttons to their handlers
go_button.on_clicked(go_button_on_clicked)
stop_button.on_clicked(stop_button_on_clicked)
reset_button.on_clicked(reset_button_on_clicked)

plt.show()
