# LaTeX Notation Reference

Common LaTeX expressions for scientific figure labels.

## Greek Letters

```python
# Lowercase
r'$\alpha, \beta, \gamma, \delta, \epsilon$'
r'$\rho, \mu, \sigma, \tau, \phi, \omega$'
r'$\eta, \theta, \lambda, \nu, \xi, \pi$'

# Uppercase
r'$\Gamma, \Delta, \Lambda, \Omega, \Phi, \Pi$'
```

## Dimensionless Groups

```python
# Reynolds number
r'$Re = \frac{\rho U L}{\mu}$'

# Weber number
r'$We = \frac{\rho U^2 L}{\gamma}$'

# Oh: viscous versus inertial-capillary stresses
r'$Oh = \frac{\mu}{\sqrt{\rho \gamma R}}$'

# Bond number
r'$Bo = \frac{\rho g R^2}{\gamma}$'

# Capillary number
r'$Ca = \frac{\mu U}{\gamma}$'

# Deborah number
r'$De = \frac{\lambda U}{L}$'

# Weissenberg number
r'$Wi = \lambda \dot{\gamma}$'

# Elasticity number
r'$El = \frac{Wi}{Re}$'
```

## Vectors and Tensors

```python
# Bold for vectors
r'$\boldsymbol{u}$'
r'$\boldsymbol{F}$'

# Vector norm
r'$\|\boldsymbol{u}\|$'
r'$|\boldsymbol{v}|$'

# Calligraphic for tensors
r'$\boldsymbol{\mathcal{D}}$'
r'$\boldsymbol{\sigma}$'

# Nabla operator
r'$\nabla \cdot \boldsymbol{u} = 0$'
r'$\nabla p$'
r'$\nabla^2 u$'
```

## Subscripts and Superscripts

```python
# Subscripts
r'$U_j$'          # Jet velocity
r'$R_0$'          # Initial radius
r'$t_c$'          # Critical time
r'$\rho_d$'       # Droplet density

# Superscripts
r'$t^*$'          # Dimensionless time
r'$U^*$'          # Dimensionless velocity
r'$x^{2/5}$'      # Power law
r'$y^{-3/4}$'     # Negative exponent

# Combined
r'$U_j^*$'        # Dimensionless jet velocity
r'$R_0^2$'        # Squared initial radius
```

## Fractions

```python
# Simple fractions
r'$\frac{U_j}{\sqrt{\gamma/\rho R}}$'

# Nested fractions (use \dfrac for display style)
r'$\dfrac{\rho U^2 L}{\gamma}$'

# Inline-style (for tight spaces)
r'$U_j/U_c$'
r'$t/\tau$'
```

## Square Roots and Powers

```python
r'$\sqrt{\rho\gamma R}$'
r'$\sqrt[3]{V}$'           # Cube root
r'$x^{2/5}$'
r'$y^{-3/4}$'
```

## Special Functions

```python
r'$\max(F(t))$'
r'$\min(\epsilon)$'
r'$\sin(\theta)$'
r'$\exp(-t/\tau)$'
r'$\log_{10}(Re)$'
r'$\ln(We)$'
```

## Common Symbols

```python
r'$\sim$'         # Scales as
r'$\propto$'      # Proportional to
r'$\approx$'      # Approximately equal
r'$\pm$'          # Plus/minus
r'$\times$'       # Multiplication
r'$\cdot$'        # Dot product
r'$\partial$'     # Partial derivative
r'$\infty$'       # Infinity
```

## Example Labels

```python
# Axis labels
ax.set_xlabel(r'$Oh = \frac{\mu}{\sqrt{\rho\gamma R}}$', fontsize=40)
ax.set_ylabel(r'$U_j/\sqrt{\gamma/\rho R}$', fontsize=40)

# Legend entries
label=r'Theory: $y \sim x^{2/5}$'
label=r'$Oh = Oh_c$'

# Colorbar
cbar.set_label(r'$\|\boldsymbol{u}\|$', fontsize=30)

# Title (rarely used in publications)
ax.set_title(r'Phase diagram: $We$-$Oh$ space', fontsize=40)
```
