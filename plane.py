import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from scipy.spatial import Delaunay
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import spsolve
import sys

# ==============================================================================
# --- Configuration Constants ---
# ==============================================================================
WIDTH, HEIGHT = 1200, 900
RES = 60                       # Parametric grid resolution
INITIAL_CAMERA_Z = -10.0
INITIAL_ROT_X = 20.0
INITIAL_ROT_Y = -30.0
EVO_DT_DEFAULT = 0.02          # Implicit timestep
EVO_SCALE_DEFAULT = 1.0        # Multiplier on Laplacian effect
MIN_AREA_THRESHOLD = 1e-12     # For numerical stability

BACKGROUND_COLOR = (0.02, 0.02, 0.02, 1.0)
WIRE_COLOR = (0.06, 0.06, 0.06)

# CINEMATIC SETTINGS
CINEMATIC_ROT_SPEED = 0.2      # Continuous rotation speed (degrees/frame)
CINEMATIC_PAN_FACTOR = 0.1     # Amplitude of side-to-side camera movement
CINEMATIC_ZOOM_FACTOR = 0.5    # Amplitude of zoom in/out movement

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
        tri = Delaunay(pts[:, :2])
        return tri.simplices

    def reset(self):
        """Resets the mesh geometry to its initial state."""
        self.points = self._generate_surface(t=0.0)
        self.n_vertices = len(self.points)

    def perturb(self, t):
        """Applies a small, gentle parametric perturbation for dynamics."""
        self.points[:, 2] += 0.003 * np.sin(self.points[:, 0] * 3.0 + t)

# ==============================================================================
# 2. Geometric Operators
# ==============================================================================

class GeometricOperators:
    """Static class for computing discrete geometric operators (L and M)."""
    @staticmethod
    def build_operators(pts, faces):
        """Computes the sparse Cotangent-Laplace Matrix (L) and the Lumped Mass diagonal (A)."""
        n = len(pts)
        rows, cols, vals = [], [], []
        A = np.zeros(n, dtype=np.float64)
        W = {} # (i,j) -> cotangent weight sum

        for f in faces:
            i0, i1, i2 = f
            p0, p1, p2 = pts[i0], pts[i1], pts[i2]
            
            e01, e12, e20 = p1 - p0, p2 - p1, p0 - p2
            cross_vec = np.cross(e01, -e20)
            twice_area = np.linalg.norm(cross_vec)
            
            if twice_area < MIN_AREA_THRESHOLD: continue
            tri_area = 0.5 * twice_area

            # Compute cotangents of angles opposite to edges
            cot_0 = np.dot(-e20, e01) / twice_area # Opposite i0 (edge e12)
            cot_1 = np.dot(e12, -e01) / twice_area # Opposite i1 (edge e20)
            cot_2 = np.dot(-e12, e20) / twice_area # Opposite i2 (edge e01)

            # Accumulate cotangent weights (W) and Mass matrix diagonal (A)
            for (i, j, cot) in [ (i1, i2, cot_0), (i2, i0, cot_1), (i0, i1, cot_2) ]:
                W.setdefault((i, j), 0.0); W[(i, j)] += cot
                W.setdefault((j, i), 0.0); W[(j, i)] += cot

            A[i0] += tri_area / 3.0
            A[i1] += tri_area / 3.0
            A[i2] += tri_area / 3.0

        # Construct sparse L matrix from weights
        diag = np.zeros(n, dtype=np.float64)
        for (i, j), w in W.items():
            if i != j:
                # Store off-diagonal $\frac{1}{2}(\cot\alpha + \cot\beta)$
                rows.append(i); cols.append(j); vals.append(0.5 * w)
                diag[i] -= 0.5 * w # Accumulate negative row-sum for diagonal

        for i in range(n):
            rows.append(i); cols.append(i); vals.append(diag[i])

        L_sparse = csr_matrix((vals, (rows, cols)), shape=(n, n))
        A[A < MIN_AREA_THRESHOLD] = MIN_AREA_THRESHOLD
        
        # 
        return L_sparse, A

    @staticmethod
    def compute_mean_curvature_vector(pts, L_sparse, A):
        """Computes the mean curvature normal vector $\mathbf{H}$."""
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
            fn = np.cross(pts[j] - pts[i], pts[k] - pts[i])
            normals[i] += fn; normals[j] += fn; normals[k] += fn
        
        norms = np.linalg.norm(normals, axis=1)
        mask = norms > MIN_AREA_THRESHOLD
        normals[mask] /= norms[mask][:, None]
        normals[~mask] = np.array([0.0, 0.0, 1.0])
        return normals

# ==============================================================================
# 3. Implicit Time Integrator
# ==============================================================================

class ImplicitIntegrator:
    """Implements the Backward-Euler scheme for Mean Curvature Flow."""
    @staticmethod
    def evolve(pts_old, L_sparse, A, dt, scale=EVO_SCALE_DEFAULT):
        """
        Solves the linear system: 
        $(\mathbf{M} - dt \cdot scale \cdot \mathbf{L}) \mathbf{x}^{k+1} = \mathbf{M} \mathbf{x}^k$
        """
        M_diag = A.copy()
        
        # LHS Matrix: $\mathbf{A}_{LHS} = \mathbf{M} - dt \cdot scale \cdot \mathbf{L}$
        # M is $\text{diag}(\mathbf{A})$, L is the negative semi-definite cotangent matrix.
        lhs_matrix = diags(M_diag, offsets=0, format='csr') - (dt * scale) * L_sparse
        
        # RHS Vector: $\mathbf{b} = \mathbf{M} \mathbf{x}^k$ (element-wise multiplication)
        
        try:
            # Solve sparse linear system for x, y, z coordinates independently
            x_new = spsolve(lhs_matrix, M_diag * pts_old[:, 0])
            y_new = spsolve(lhs_matrix, M_diag * pts_old[:, 1])
            z_new = spsolve(lhs_matrix, M_diag * pts_old[:, 2])
        except Exception as e:
            print(f"ERROR: Sparse linear solve failed. Details: {e}")
            return pts_old

        pts_new = np.vstack([x_new, y_new, z_new]).T
        
        # 
        return pts_new

# ==============================================================================
# 4. Visualization and Main Loop
# ==============================================================================

class GraphicsEngine:
    """Manages OpenGL rendering, Pygame event loop, and cinematic control."""
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
        # Camera State (These are reset by 'G')
        self.camera_z = INITIAL_CAMERA_Z
        self.rotation_x = INITIAL_ROT_X
        self.rotation_y = INITIAL_ROT_Y
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.last_mouse_pos = None

    def _handle_events(self):
        """Processes user input."""
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
                    print("Geometry reset (R).")
                elif ev.key == K_g: # NEW: Camera Reset
                    self.camera_z = INITIAL_CAMERA_Z
                    self.rotation_x = INITIAL_ROT_X
                    self.rotation_y = INITIAL_ROT_Y
                    self.pan_x = 0.0
                    self.pan_y = 0.0
                    print("Camera reset (G).")
            
            # Mouse controls for rotation, pan, and zoom...
            # (Remains the same as previous implementation)
            elif ev.type == MOUSEBUTTONDOWN:
                self.last_mouse_pos = ev.pos
            elif ev.type == MOUSEBUTTONUP:
                self.last_mouse_pos = None
            elif ev.type == MOUSEMOTION:
                if ev.buttons[0]:
                    self.rotation_x += ev.rel[1] * 0.4
                    self.rotation_y += ev.rel[0] * 0.4
                elif ev.buttons[1] and self.last_mouse_pos:
                    self.pan_x += ev.rel[0] * 0.01
                    self.pan_y -= ev.rel[1] * 0.01
                self.last_mouse_pos = ev.pos
            elif ev.type == MOUSEWHEEL:
                self.camera_z += -ev.y * 0.6
    
    def _curvature_laplacian_colors(self, dH):
        """Generates colors based on $\Delta \kappa$ for visualization."""
        maxabs = np.max(np.abs(dH)) + 1e-9
        dHn = dH / maxabs
        cols = np.zeros((len(dH), 3), dtype=np.float32)
        
        # Red/Blue diverging colormap (standard for curvature analysis)
        cols[:, 0] = np.clip((dHn + 1.0) * 0.5, 0.0, 1.0) # Red
        cols[:, 2] = np.clip(1.0 - (dHn + 1.0) * 0.5, 0.0, 1.0) # Blue
        cols[:, 1] = 1.0 - np.abs(dHn) # Green (peak at 0)
        return cols
    
    def _draw_mesh(self, pts, faces, cols):
        """Renders the mesh geometry."""
        glEnable(GL_LIGHTING)
        glShadeModel(GL_SMOOTH)
        
        normals = GeometricOperators.compute_vertex_normals(pts, faces)
        
        glBegin(GL_TRIANGLES)
        for tri in faces:
            for idx in tri:
                glColor3fv(cols[idx])
                glNormal3fv(normals[idx])
                glVertex3fv(pts[idx])
        glEnd()
        
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

            # --- CINEMATIC MOVEMENTS (Automated Camera) ---
            # Continuous Turntable Rotation
            self.rotation_y += CINEMATIC_ROT_SPEED * dt_sec * 60.0
            
            # Panoramic and Zoom effect using sine waves
            self.pan_x = CINEMATIC_PAN_FACTOR * np.sin(self.t_total * 0.8) 
            self.camera_z = INITIAL_CAMERA_Z + CINEMATIC_ZOOM_FACTOR * np.cos(self.t_total * 0.6) 

            # --- 1. Compute Operators and Perturb ---
            L_sparse, A = GeometricOperators.build_operators(self.mesh.points, self.mesh.faces)
            self.mesh.perturb(self.t_total)
            
            # --- 2. Curvature Analysis ---
            _, H_mag = GeometricOperators.compute_mean_curvature_vector(self.mesh.points, L_sparse, A)
            
            # Compute Curvature Laplacian scalar $\Delta \kappa$ for visualization colors
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

            # Lighting setup
            glEnable(GL_LIGHTING)
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
