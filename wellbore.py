import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI
import json

# -------------------------------
# Constants and initial conditions
# -------------------------------
g = 9.81
P0 = 45e5  # 45 bar abs
T0 = 250 + 273.15  # 250°C
depth0 = 2500  # m
dz = 1.0
N = int(depth0 / dz) + 1
z_vals = np.linspace(depth0, 0, N)

# Reservoir enthalpy (isoenthalpic)
h_res = PropsSI('H', 'P', P0, 'T', T0, 'Water')

# Drift-Flux parameter
C0 = 1.2  # Typical for vertical flow

# -------------------------------
# Arrays
# -------------------------------
P_vals = np.zeros(N)
x_vals = np.zeros(N)
alpha_vals = np.zeros(N)

P_vals[0] = P0

for i in range(1, N):
    P_prev = P_vals[i-1]
    P_safe = max(P_prev, 1e5)  # Floor at 1 bar abs for stability

    # Determine fluid state
    Psat_local = PropsSI('P', 'T', T0, 'Q', 0, 'Water')

    if P_prev > Psat_local:
        x = 0.0  # Before flashing
        alpha = 0.0
        rho_m = PropsSI('D', 'P', P_prev, 'T', T0, 'Water')
    else:
        T_sat = PropsSI('T', 'P', P_prev, 'Q', 0, 'Water')
        hf = PropsSI('H', 'P', P_prev, 'Q', 0, 'Water')
        hg = PropsSI('H', 'P', P_prev, 'Q', 1, 'Water')

        if hg - hf > 0:
            x = (h_res - hf) / (hg - hf)
            x = np.clip(x, 0.0, 1.0)
        else:
            x = 0.0

        rho_L = PropsSI('D', 'P', P_prev, 'Q', 0, 'Water')
        rho_G = PropsSI('D', 'P', P_prev, 'Q', 1, 'Water')

        if x > 0:
            alpha = (C0 * x / rho_G) / (C0 * x / rho_G + (1 - x) / rho_L)
        else:
            alpha = 0.0

        rho_m = alpha * rho_G + (1 - alpha) * rho_L

    x_vals[i] = x
    alpha_vals[i] = alpha

    # Pressure drop
    dP = -rho_m * g * dz
    P_new = P_prev + dP
    P_vals[i] = max(P_new, 1e5)  # Floor limit at 1 bar abs

# -------------------------------
# Plot results
# -------------------------------

plt.figure(figsize=(6, 8))
plt.plot(P_vals / 1e5, z_vals)
plt.gca().invert_yaxis()
plt.xlabel('Pressure (bar)')
plt.ylabel('Depth (m)')
plt.title('Pressure Profile (DFM + isoenthalpic flashing)')
plt.grid(True)
plt.show()

plt.figure(figsize=(6, 8))
plt.plot(alpha_vals, z_vals)
plt.gca().invert_yaxis()
plt.xlabel('Void Fraction α')
plt.ylabel('Depth (m)')
plt.title('Void Fraction Profile (DFM + isoenthalpic flashing)')
plt.grid(True)
plt.show()

plt.figure(figsize=(6, 8))
plt.plot(x_vals, z_vals)
plt.gca().invert_yaxis()
plt.xlabel('Dryness Fraction x')
plt.ylabel('Depth (m)')
plt.title('Dryness Fraction Profile (DFM + isoenthalpic flashing)')
plt.grid(True)
plt.show()



# ... kode wellbore mu tetap ...
# Misal hasil akhirnya:
P_wellhead = 11.3e5  # Pa
x_wellhead = 0.14    # dari hasil DFM
m_dot_total = 1.0    # kg/s asumsi

# Simpan ke file JSON
data = {
    "P_wellhead": P_wellhead,
    "x_wellhead": x_wellhead,
    "m_dot_total": m_dot_total
}

with open("wellbore_output.json", "w") as f:
    json.dump(data, f)

print("wellbore.py selesai: data disimpan ke wellbore_output.json")

import pandas as pd

# Siapkan dictionary data
data = {
    'Depth_m': z_vals,
    'Pressure_bar': [P/1e5 for P in P_vals],
    'Dryness_fraction': x_vals,
    'Void_fraction': alpha_vals
}

# Jika ada enthalpy dan velocity, tambahkan:
if 'h_vals' in locals():
    data['Enthalpy_kJ_kg'] = [h/1000 for h in h_vals]

if 'u_vals' in locals():
    data['Velocity_m_s'] = u_vals

# Convert ke DataFrame
df = pd.DataFrame(data)

# Simpan ke Excel
df.to_excel("wellbore_results.xlsx", index=False)

print("✅ Data profil wellbore disimpan ke wellbore_results.xlsx")
