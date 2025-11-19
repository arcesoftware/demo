import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import spsolve
import sys

# --- Configuration Constants ---
WIDTH, HEIGHT = 1200, 900
RES = 60                       # Parametric grid resolution
INITIAL_CAMERA_Z = -10.0
INITIAL_ROT_X = 20.0
INITIAL_ROT_Y = -30.0
EVO_DT_DEFAULT = 0.02          # Implicit timestep
EVO_SCALE_DEFAULT = 1.0        # Multiplier on Laplacian effect
MIN_AREA_THRESHOLD = 1e-12
BACKGROUND_COLOR = (0.02, 0.02, 0.02, 1.0)
WIRE_COLOR = (0.06, 0.06, 0.06)

# ==============================================================================
# 1. Mesh Geometry Management
# ==============================================================================

class MeshGeometry:
    """Manages vertex positions and face connectivity of the mesh."""
    def __init__(self, n_res=RES):
        self.n_res = n_res
        self.points = self._generate_surface(t=0.0)
        self.faces = self._triangulate(self.points)
        self.n_vertices = len(self.points)

    def _generate_surface(self, t):
        """Generates initial 3D vertex positions (e.g., a parameterized wave)."""
        u = np.linspace(-2.0, 2.0, self.n_res)
        v = np.linspace(-2.0, 2.0, self.n_res)
        uu, vv = np.meshgrid(u, v)
        # Initial wave-like shape
        z = 0.6 * np.sin(uu * 2.0 + t) + 0.6 * np.cos(vv * 2.0 - t)
        pts = np.vstack([uu.ravel(), vv.ravel(), z.ravel()]).T
        return pts

    def _triangulate(self, pts):
        """Creates face connectivity using Delaunay triangulation of the (x, y) plane."""
        # Use only the 2D coordinates for triangulation
        tri = Delaunay(pts[:, :2])
        return tri.simplices

    def reset(self):
        """Resets the mesh to its initial state."""
        self.points = self._generate_surface(t=0.0)
        self.n_vertices = len(self.points)

    def perturb(self, t):
        """Applies a small, gentle parametric perturbation for dynamics."""
        # Gentle Z-perturbation
        self.points[:, 2] += 0.003 * np.sin(self.points[:, 0] * 3.0 + t)

# ==============================================================================
# 2. Geometric Operators (Discrete Differential Geometry)
# ==============================================================================

class GeometricOperators:
    """
    Static class for computing discrete geometric operators.
    Uses: Cotangent-Laplace (L) and Lumped Mass (M) matrices.
    """
    @staticmethod
    def build_operators(pts, faces):
        """
        Computes the sparse Cotangent-Laplace Matrix (L) and the diagonal of
        the Lumped Mass Matrix (A).
        """
        n = len(pts)
        rows, cols, vals = [], [], []
        # A will store the area-based diagonal of the Lumped Mass Matrix
        A = np.zeros(n, dtype=np.float64)

        # Build off-diagonal weights W (Cotangent weights)
        W = {}
        for i, f in enumerate(faces):
            # Vertices and their positions
            i0, i1, i2 = f
            p0, p1, p2 = pts[i0], pts[i1], pts[i2]

            # Edges
            e01, e12, e20 = p1 - p0, p2 - p1, p0 - p2

            # Triangle Area (doubled)
            cross_vec = np.cross(e01, -e20)
            twice_area = np.linalg.norm(cross_vec)
            if twice_area < MIN_AREA_THRESHOLD:
                continue
            
            # Triangle Area (for Mass Matrix)
            tri_area = 0.5 * twice_area

            # Cotangent of angles opposite to edges
            # cot(alpha) = (u . v) / |u x v|
            # Note: |u x v| = twice_area

            # cot_0 is opposite edge e12 (p1-p2)
            cot_0 = np.dot(-e20, e01) / twice_area
            # cot_1 is opposite edge e20 (p2-p0)
            cot_1 = np.dot(e12, -e01) / twice_area
            # cot_2 is opposite edge e01 (p0-p1)
            cot_2 = np.dot(-e12, e20) / twice_area

            # Accumulate cotangent weights (1/2 * sum of cotangents of opposite angles)
            # Edge (i1, i2) is opposite i0
            W.setdefault((i1, i2), 0.0); W[(i1, i2)] += cot_0
            W.setdefault((i2, i1), 0.0); W[(i2, i1)] += cot_0

            # Edge (i2, i0) is opposite i1
            W.setdefault((i2, i0), 0.0); W[(i2, i0)] += cot_1
            W.setdefault((i0, i2), 0.0); W[(i0, i2)] += cot_1

            # Edge (i0, i1) is opposite i2
            W.setdefault((i0, i1), 0.0); W[(i0, i1)] += cot_2
            W.setdefault((i1, i0), 0.0); W[(i1, i0)] += cot_2

            # Accumulate Mass Matrix diagonal (Lumped Mass: 1/3 area to each vertex)
            A[i0] += tri_area / 3.0
            A[i1] += tri_area / 3.0
            A[i2] += tri_area / 3.0

        # Construct the sparse L matrix
        diag = np.zeros(n, dtype=np.float64)
        for (i, j), w in W.items():
            if i != j:
                rows.append(i); cols.append(j); vals.append(0.5 * w) # 1/2 factor
                diag[i] -= 0.5 * w # Diagonal is negative row-sum (with 1/2 factor)

        # Add diagonal entries
        for i in range(n):
            rows.append(i); cols.append(i); vals.append(diag[i])

        L_sparse = csr_matrix((vals, (rows, cols)), shape=(n, n))
        
        # Clamp small areas for stability (Mass matrix diagonal)
        A[A < MIN_AREA_THRESHOLD] = MIN_AREA_THRESHOLD
        
        # 
        return L_sparse, A

    @staticmethod
    def compute_mean_curvature_vector(pts, L_sparse, A):
        """Computes the mean curvature normal vector $\mathbf{H}$ using the LBO approximation."""
        # Mean Curvature Vector $\mathbf{H} = -\frac{1}{2} M^{-1} L \mathbf{x}$
        # Here: $\mathbf{H} = \frac{1}{2} \text{Area}^{-1} L \mathbf{x}$ (since L is defined with 1/2 cot factor)
        delta = L_sparse.dot(pts)
        inv2A = 1.0 / (2.0 * A[:, None])
        H_vec = delta * inv2A
        H_mag = np.linalg.norm(H_vec, axis=1)
        return H_vec, H_mag
    
    @staticmethod
    def compute_vertex_normals(pts, faces):
        """Computes area-weighted vertex normals."""
        n = len(pts)
        normals = np.zeros((n, 3), dtype=np.float64)
        for f in faces:
            i, j, k = f
            pi, pj, pk = pts[i], pts[j], pts[k]
            # Face Normal (area-weighted)
            fn = np.cross(pj - pi, pk - pi)
            normals[i] += fn; normals[j] += fn; normals[k] += fn
        
        # Normalize
        norms = np.linalg.norm(normals, axis=1)
        mask = norms > MIN_AREA_THRESHOLD
        normals[mask] /= norms[mask][:, None]
        normals[~mask] = np.array([0.0, 0.0, 1.0]) # Default up for flat/degenerate
        return normals

# ==============================================================================
# 3. Implicit Time Integrator
# ==============================================================================

class ImplicitIntegrator:
    """Implements the Backward-Euler scheme for Mean Curvature Flow."""
    @staticmethod
    def evolve(pts_old, L_sparse, A, dt, scale=EVO_SCALE_DEFAULT):
        """
        Solves the linear system: $(\mathbf{M} - dt \cdot scale \cdot \mathbf{L}) \mathbf{x}^{k+1} = \mathbf{M} \mathbf{x}^k$
        Note: $\mathbf{L}$ is the negative semi-definite discrete Laplacian, $\mathbf{M} = \text{diag}(\mathbf{A})$.
        The standard formulation is $(\mathbf{M} + dt \cdot \mathbf{L}_{\text{positive}}) \mathbf{x}^{k+1} = \mathbf{M} \mathbf{x}^k$
        Since the $\mathbf{L}$ computed here is $\mathbf{L}_{\text{negative}}$ (negative diagonals),
        the LHS becomes: $(\mathbf{M} - dt \cdot scale \cdot \mathbf{L}_{\text{negative}})$.
        """
        n = len(pts_old)
        M_diag = A.copy()
        
        # Left-Hand Side (LHS) Matrix: $\mathbf{A}_{LHS} = \mathbf{M} - dt \cdot scale \cdot \mathbf{L}$
        # M is a diagonal matrix, $\text{diag}(\mathbf{A})$
        lhs_matrix = diags(M_diag, offsets=0, format='csr') - (dt * scale) * L_sparse
        
        # Right-Hand Side (RHS) Vector: $\mathbf{b} = \mathbf{M} \mathbf{x}^k$
        # Since M is diagonal, this is element-wise multiplication
        
        # Solve the sparse linear system for each coordinate (x, y, z)
        try:
            x_new = spsolve(lhs_matrix, M_diag * pts_old[:, 0])
            y_new = spsolve(lhs_matrix, M_diag * pts_old[:, 1])
            z_new = spsolve(lhs_matrix, M_diag * pts_old[:, 2])
        except Exception as e:
            print(f"ERROR: Sparse linear solve failed. Returning previous state. Details: {e}")
            return pts_old

        pts_new = np.vstack([x_new, y_new, z_new]).T
        
        # 
        return pts_new

# ==============================================================================
# 4. Visualization and Main Loop
# ==============================================================================

class GraphicsEngine:
    """Manages OpenGL rendering and Pygame event loop."""
    def __init__(self, mesh):
        pygame.init()
        pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Implicit Curvature-Driven Mesh Evolution (MCF)")
        
        self.mesh = mesh
        self._init_gl()
        self._init_controls()
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.t_total = 0.0

    def _init_gl(self):
        """Set up OpenGL rendering parameters."""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(*BACKGROUND_COLOR)
        
    def _init_controls(self):
        """Initialize simulation and camera controls."""
        self.evo_enabled = False
        self.evo_dt = EVO_DT_DEFAULT
        self.evo_scale = EVO_SCALE_DEFAULT
        self.camera_z = INITIAL_CAMERA_Z
        self.rotation_x = INITIAL_ROT_X
        self.rotation_y = INITIAL_ROT_Y
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.last_mouse_pos = None

    def _handle_events(self):
        """Processes user input for camera control and simulation state."""
        for ev in pygame.event.get():
            if ev.type == QUIT:
                self.running = False
            
            elif ev.type == KEYDOWN:
                if ev.key == K_p:
                    self.evo_enabled = not self.evo_enabled
                    print(f"Evolution: {'ON' if self.evo_enabled else 'OFF'}")
                elif ev.key in (K_PLUS, K_EQUALS):
                    self.evo_dt *= 1.2
                    print(f"Time Step (dt): {self.evo_dt:.4f}")
                elif ev.key in (K_MINUS, K_UNDERSCORE):
                    self.evo_dt = max(1e-6, self.evo_dt * 0.8)
                    print(f"Time Step (dt): {self.evo_dt:.4f}")
                elif ev.key == K_r:
                    self.mesh.reset()
                    print("Geometry reset.")
            
            # Mouse handling for rotation (Left), pan (Middle), and zoom (Wheel)
            elif ev.type == MOUSEBUTTONDOWN:
                self.last_mouse_pos = ev.pos
            elif ev.type == MOUSEBUTTONUP:
                self.last_mouse_pos = None
            elif ev.type == MOUSEMOTION:
                if ev.buttons[0]: # Left button for rotation
                    self.rotation_x += ev.rel[1] * 0.4
                    self.rotation_y += ev.rel[0] * 0.4
                elif ev.buttons[1] and self.last_mouse_pos: # Middle button for pan
                    self.pan_x += ev.rel[0] * 0.01
                    self.pan_y -= ev.rel[1] * 0.01
                self.last_mouse_pos = ev.pos
            elif ev.type == MOUSEWHEEL:
                self.camera_z += -ev.y * 0.6
    
    def _curvature_laplacian_colors(self, dH):
        """Generates colors based on the sign and magnitude of the Curvature Laplacian ($\Delta \kappa$)."""
        maxabs = np.max(np.abs(dH)) + 1e-9
        dHn = dH / maxabs # Normalized to [-1, 1]
        cols = np.zeros((len(dH), 3), dtype=np.float32)
        
        # Simple Red/Blue diverging colormap: Blue for negative, Red for positive
        cols[:, 0] = np.clip((dHn + 1.0) * 0.5, 0.0, 1.0) # Red channel (0.5 for 0, 1 for +1)
        cols[:, 2] = np.clip(1.0 - (dHn + 1.0) * 0.5, 0.0, 1.0) # Blue channel (1 for -1, 0.5 for 0)
        cols[:, 1] = 1.0 - np.abs(dHn) # Green channel (1 for 0, 0 for +/-1)
        return cols
    
    def _draw_mesh(self, pts, faces, cols):
        """Renders the mesh geometry."""
        # Draw shaded triangles
        glEnable(GL_LIGHTING)
        glShadeModel(GL_SMOOTH)
        
        # Compute and upload normals
        normals = GeometricOperators.compute_vertex_normals(pts, faces)
        
        glBegin(GL_TRIANGLES)
        for tri in faces:
            for i, idx in enumerate(tri):
                glColor3fv(cols[idx])
                glNormal3fv(normals[idx])
                glVertex3fv(pts[idx])
        glEnd()
        
        # Draw wireframe (separate pass)
        glDisable(GL_LIGHTING)
        glColor3fv(WIRE_COLOR)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for tri in faces:
            for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                glVertex3fv(pts[a]); glVertex3fv(pts[b])
        glEnd()

    def run(self):
        """The main simulation and rendering loop."""
        
        while self.running:
            dt_sec = self.clock.tick(60) / 1000.0
            self.t_total += dt_sec * 0.5

            self._handle_events()

            # --- 1. Compute Operators ---
            # Recompute L and A every step because vertex positions (pts) have changed
            L_sparse, A = GeometricOperators.build_operators(self.mesh.points, self.mesh.faces)
            
            # --- 2. Perturbation & Curvature Analysis ---
            self.mesh.perturb(self.t_total)
            
            # Compute Mean Curvature (scalar magnitude) for visualization
            _, H_mag = GeometricOperators.compute_mean_curvature_vector(self.mesh.points, L_sparse, A)
            
            # Compute Curvature Laplacian scalar for color-coding ($\Delta \kappa$)
            # $\Delta \kappa = \mathbf{M}^{-1} \mathbf{L} \kappa$
            LH = L_sparse.dot(H_mag)
            dH = LH / (A + MIN_AREA_THRESHOLD)
            
            # --- 3. Implicit Integration (Evolution) ---
            if self.evo_enabled:
                self.mesh.points = ImplicitIntegrator.evolve(
                    self.mesh.points, L_sparse, A, self.evo_dt, self.evo_scale
                )

            # --- 4. Rendering ---
            cols = self._curvature_laplacian_colors(dH)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Camera transformation
            gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
            glTranslatef(self.pan_x, self.pan_y, self.camera_z)
            glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
            glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

            # Lighting setup (simple fixed light)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, (10.0, 10.0, 10.0, 0.0))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
            glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
            glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

            self._draw_mesh(self.mesh.points, self.mesh.faces, cols)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

# ==============================================================================
# Main Execution Block
# ==============================================================================

if __name__ == "__main__":
    mesh = MeshGeometry(n_res=RES)
    engine = GraphicsEngine(mesh)
    engine.run()
