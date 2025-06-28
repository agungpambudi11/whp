import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 16

# === 1. Parameter Awal ===
depth_total = 2500  # Kedalaman sumur (m)
steps = 100
depth = np.linspace(depth_total, 0, steps)  # dari reservoir ke permukaan

T_res_C = 250
T_res_K = T_res_C + 273.15
P_res_bar = 45
P_wellhead_bar = 10

# === 2. Profil Tekanan Dinamis ===
P_profile_bar = np.zeros(steps)
x_profile = np.zeros(steps)
T_profile_C = np.zeros(steps)
h_profile_kJkg = np.zeros(steps)
rho_profile = np.zeros(steps)
mu_profile = np.zeros(steps)
v_profile = np.zeros(steps)
energy_gain = np.zeros(steps)
flow_regime = ["Liquid"] * steps

flash_depth = None
flashing = False

for i in range(steps):
    z = depth[i]
    try:
        if i == 0:
            P_prev = P_res_bar
        else:
            P_prev = P_profile_bar[i-1]

        P = P_prev * np.exp(-0.02) * 1e5

        h = PropsSI('H', 'T', T_res_K, 'P', P, 'Water')
        h_l = PropsSI('H', 'P', P, 'Q', 0, 'Water')
        h_v = PropsSI('H', 'P', P, 'Q', 1, 'Water')
        x = (h - h_l) / (h_v - h_l)
        x = np.clip(x, 0, 1)
        x_profile[i] = x

        if x > 0:
            flow_regime[i] = "Two-phase"
        else:
            flow_regime[i] = "Liquid"

        # Properti dua fase
        if x > 0:
            rho_l = PropsSI('D', 'P', P, 'Q', 0, 'Water')
            rho_v = PropsSI('D', 'P', P, 'Q', 1, 'Water')
            mu_l = PropsSI('V', 'P', P, 'Q', 0, 'Water')
            mu_v = PropsSI('V', 'P', P, 'Q', 1, 'Water')

            rho_mix = 1 / ((x / rho_v) + ((1 - x) / rho_l))
            mu_mix = mu_l * (1 - x) + mu_v * x
        else:
            rho_mix = PropsSI('D', 'T', T_res_K, 'P', P, 'Water')
            mu_mix = PropsSI('V', 'T', T_res_K, 'P', P, 'Water')

        rho_profile[i] = rho_mix
        mu_profile[i] = mu_mix * 1000
        h_profile_kJkg[i] = h / 1000
        v_profile[i] = 1 / rho_mix

        if i == 0:
            energy_gain[i] = 0
        else:
            energy_gain[i] = h_profile_kJkg[i] - h_profile_kJkg[0]

        if x > 0 and not flashing:
            flash_depth = z  # Titik flashing ditentukan saat fraksi uap mulai > 0
            flashing = True

        P_profile_bar[i] = P / 1e5
        T_sat_K = PropsSI('T', 'P', P, 'Q', 0, 'Water')
        T_profile_C[i] = T_sat_K - 273.15

    except:
        T_profile_C[i] = np.nan
        x_profile[i] = 0
        P_profile_bar[i] = P_prev
        h_profile_kJkg[i] = np.nan
        rho_profile[i] = np.nan
        mu_profile[i] = np.nan
        v_profile[i] = np.nan
        energy_gain[i] = np.nan

# === 3. Plot dalam 4 canvas ===
def plot_two_graphs(x1, y1, xlabel1, title1,
                    x2, y2, xlabel2, title2,
                    yflash, ylabel, canvas_title):
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(canvas_title, fontsize=16)

    axs[0].plot(x1, y1)
    axs[0].invert_yaxis()
    axs[0].set_xlabel(xlabel1)
    axs[0].set_ylabel(ylabel)
    axs[0].set_title(title1)
    if xlabel1 == "Temperature (°C)":
        axs[0].set_xlim(left=0)
    if yflash is not None:
        axs[0].axhline(yflash, color='red', linestyle='--', label="Onset of Flashing")
        axs[0].legend()

    axs[1].plot(x2, y2)
    axs[1].invert_yaxis()
    axs[1].set_xlabel(xlabel2)
    axs[1].set_title(title2)
    if xlabel2 == "Temperature (°C)":
        axs[1].set_xlim(left=0)
    if yflash is not None:
        axs[1].axhline(yflash, color='red', linestyle='--', label="Onset of Flashing")
        axs[1].legend()

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

# Canvas 1: Pressure & Temperature
plot_two_graphs(
    P_profile_bar, depth, "Pressure (bar)", "Pressure Profile",
    T_profile_C, depth, "Temperature (°C)", "Saturation Temperature",
    flash_depth, "Depth (m)", "Canvas 1: Pressure & Temperature"
)

# Canvas 2: Vapor Quality & Enthalpy
plot_two_graphs(
    x_profile, depth, "Vapor Quality", "Vapor Fraction Profile",
    h_profile_kJkg, depth, "Enthalpy (kJ/kg)", "Enthalpy Profile",
    flash_depth, "Depth (m)", "Canvas 2: Quality & Enthalpy"
)

# Canvas 3: Density & Viscosity
plot_two_graphs(
    rho_profile, depth, "Density (kg/m³)", "Density Profile",
    mu_profile, depth, "Viscosity (mPa·s)", "Viscosity Profile",
    flash_depth, "Depth (m)", "Canvas 3: Density & Viscosity"
)

# Canvas 4: Specific Volume & Energy Gain
plot_two_graphs(
    v_profile, depth, "Specific Volume (m³/kg)", "Specific Volume Profile",
    energy_gain, depth, "Energy Gain (kJ/kg)", "Energy Gain from Reservoir",
    flash_depth, "Depth (m)", "Canvas 4: Volume & Energy Gain"
)
