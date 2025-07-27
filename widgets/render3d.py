import numpy as np
import math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial.transform import Rotation as R

class Render3D(FigureCanvas):
    def __init__(self, parent=None):
        # Initialize the FigureCanvas with a Figure
        self.fig = Figure()
        super().__init__(self.fig)
        self.ax = self.figure.add_subplot(111, projection='3d')

        # Setup the 3D axes
        self.ax.set_xlim([-20, 20])
        self.ax.set_ylim([-20, 20])
        self.ax.set_zlim([-20, 20])
        self.ax.set_xlabel('X (forward)')
        self.ax.set_ylabel('Y (left)')
        self.ax.set_zlabel('Z (up)')
        self.ax.view_init(elev=20, azim=-30)

        # Initialize quiver arrows with dummy directions
        self.x_arrow = self.ax.quiver(0, 0, 0, 1, 0, 0, color='r', length=20, normalize=True)
        self.y_arrow = self.ax.quiver(0, 0, 0, 0, 1, 0, color='g', length=20, normalize=True)
        self.z_arrow = self.ax.quiver(0, 0, 0, 0, 0, 1, color='b', length=20, normalize=True)

        # Set up 3d model dimensions
        self.cube_vertices = np.array([
            [-1, -1, -1],
            [ 1, -1, -1],
            [ 1,  1, -1],
            [-1,  1, -1],
            [-1, -1,  1],
            [ 1, -1,  1],
            [ 1,  1,  1],
            [-1,  1,  1]
        ]) * 4  # Scale cube size

        self.cube_faces = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [2, 3, 7, 6],
            [1, 2, 6, 5],
            [0, 3, 7, 4]
        ]

        self.rendered_cube_patches = []
        

    def update_orientation(self, pitch, roll, yaw):
            # Convert angles to rotation
            rotation = R.from_euler('xyz', [math.radians(pitch), math.radians(roll), math.radians(yaw)])
            x_axis = rotation.apply([1, 0, 0])  # forward
            y_axis = rotation.apply([0, 1, 0])  # left
            z_axis = rotation.apply([0, 0, 1])  # up

            # Update quiver arrow directions
            self.x_arrow.remove()
            self.y_arrow.remove()
            self.z_arrow.remove()

            self.x_arrow = self.ax.quiver(0, 0, 0, x_axis[0], x_axis[1], x_axis[2], color='r', length=20, normalize=True)
            self.y_arrow = self.ax.quiver(0, 0, 0, y_axis[0], y_axis[1], y_axis[2], color='g', length=20, normalize=True)
            self.z_arrow = self.ax.quiver(0, 0, 0, z_axis[0], z_axis[1], z_axis[2], color='b', length=20, normalize=True)

            # Apply rotation to cube vertices
            rotated_vertices = rotation.apply(self.cube_vertices)

            # Remove previously drawn cube faces
            for patch in self.rendered_cube_patches:
                patch.remove()
            self.rendered_cube_patches.clear()
            
            for face_indices in self.cube_faces:
                face_coords = [rotated_vertices[i] for i in face_indices]
                poly = Poly3DCollection([face_coords], facecolor='#CD7F32', edgecolor='k', alpha=0.4)
                self.ax.add_collection3d(poly)
                self.rendered_cube_patches.append(poly)

            self.draw()