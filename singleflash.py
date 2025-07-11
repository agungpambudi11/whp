import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

# -------------------------------
# Constants
# -------------------------------
h_res = PropsSI('H', 'P', 45e5, 'T', 250+273.15, 'Water')  # Reservoir enthalpy (J/kg)
m_dot_total = 1.0  # Total mass flow (kg/s)

# Cooling Tower setup
T_wb = 25 + 273.15  # 25°C wet bulb
approach = 7  # K
T_cond = T_wb + approach  # condenser temp ~32°C
P_cond = PropsSI('P', 'T', T_cond, 'Q', 0, 'Water')  # condenser pressure from cooling tower

# Separator pressure range
P_sep_bar = np.linspace(3, 12, 20)  # bar abs
P_sep_Pa = P_sep_bar * 1e5  # convert to Pa

steam_mass = []
brine_mass = []
power_output = []
dryness_fraction = []
steam_fraction_percent = []
ssc_values = []

for P_sep in P_sep_Pa:
    h_f_sep = PropsSI('H', 'P', P_sep, 'Q', 0, 'Water')
    h_g_sep = PropsSI('H', 'P', P_sep, 'Q', 1, 'Water')

    x_sep = (h_res - h_f_sep) / (h_g_sep - h_f_sep)
    x_sep = max(0.0, min(1.0, x_sep))

    dryness_fraction.append(x_sep)

    m_dot_steam = x_sep * m_dot_total
    m_dot_brine = m_dot_total - m_dot_steam

    ejector_fraction = 0.03  # 3% steam to ejector
    m_dot_steam_net = m_dot_steam * (1 - ejector_fraction)

    steam_mass.append(m_dot_steam)
    brine_mass.append(m_dot_brine)

    steam_fraction = 100 * m_dot_steam_net / m_dot_total
    steam_fraction_percent.append(steam_fraction)

    if m_dot_steam_net > 0:
        h_turb_out = PropsSI('H', 'P', P_cond, 'Q', 1, 'Water')
        delta_h_turb = h_g_sep - h_turb_out
        W_turb = m_dot_steam_net * delta_h_turb / 1000  # kW
    else:
        W_turb = 0

    power_output.append(W_turb)

    if W_turb > 0:
        ssc = m_dot_steam_net / W_turb  # kg/kWh
    else:
        ssc = np.nan  # avoid division by zero

    ssc_values.append(ssc)

# -------------------------------
# Plot 1: Separator pressure vs mass flowrates
# -------------------------------
plt.figure(figsize=(8, 6))
plt.plot(P_sep_bar, steam_mass, label='Gross Steam mass (kg/s)')
plt.plot(P_sep_bar, brine_mass, label='Brine mass (kg/s)')
plt.xlabel('Separator Pressure (bar abs)')
plt.ylabel('Mass Flowrate (kg/s)')
plt.title('Separator Pressure vs Mass Flowrates')
plt.legend()
plt.grid(True)
plt.show()

# -------------------------------
# Plot 2: Separator pressure vs turbine power output
# -------------------------------
plt.figure(figsize=(8, 6))
plt.plot(P_sep_bar, power_output, marker='o')
plt.xlabel('Separator Pressure (bar abs)')
plt.ylabel('Power Output (kW)')
plt.title('Separator Pressure vs Turbine Power Output (w/ ejector + cooling tower)')
plt.grid(True)
plt.show()

# -------------------------------
# Plot 3: Separator pressure vs dryness fraction
# -------------------------------
plt.figure(figsize=(8, 6))
plt.plot(P_sep_bar, dryness_fraction, marker='s', color='purple')
plt.xlabel('Separator Pressure (bar abs)')
plt.ylabel('Dryness Fraction x_sep')
plt.title('Separator Pressure vs Dryness Fraction')
plt.grid(True)
plt.show()

# -------------------------------
# Plot 4: Separator pressure vs Steam fraction (%)
# -------------------------------
plt.figure(figsize=(8, 6))
plt.plot(P_sep_bar, steam_fraction_percent, marker='d', color='green')
plt.xlabel('Separator Pressure (bar abs)')
plt.ylabel('Steam Fraction (%)')
plt.title('Separator Pressure vs Steam Yield Efficiency (%)')
plt.grid(True)
plt.show()

# -------------------------------
# Plot 5: Separator pressure vs Specific Steam Consumption (kg/kWh)
# -------------------------------
plt.figure(figsize=(8, 6))
plt.plot(P_sep_bar, ssc_values, marker='^', color='orange')
plt.xlabel('Separator Pressure (bar abs)')
plt.ylabel('Specific Steam Consumption (kg/kWh)')
plt.title('Separator Pressure vs Specific Steam Consumption')
plt.grid(True)
plt.show()

import pandas as pd

# Buat dictionary data hasil simulasi
data = {
    'Separator_Pressure_bar': P_sep_bar,
    'Steam_mass_kg_s': steam_mass,
    'Brine_mass_kg_s': brine_mass,
    'Power_output_kW': power_output,
    'Dryness_fraction': dryness_fraction,
    'Steam_fraction_percent': steam_fraction_percent,
    'SSC_kg_per_kWh': ssc_values
}



# -------------------------------
# Constants
# -------------------------------
h_cond = PropsSI('H', 'P', 0.45e5, 'Q', 0, 'Water')  # condenser at 0.45 bar abs

P_sep = 3e5  # Separator pressure: 3 bar abs
m_dot_values = np.arange(1, 301, 10)  # 1 kg/s to 300 kg/s with step 10 kg/s

h_sep = PropsSI('H', 'P', P_sep, 'Q', 1, 'Water')  # Separator steam enthalpy

h_wh = 1085.75e3  # Wellhead enthalpy (J/kg) — adjust if needed
steam_fraction = 0.28  # Steam yield at separator 3 bar abs (example value)
ejector_penalty = 0.03  # 3% steam penalty for ejector

W_t_results = []

# -------------------------------
# Loop over mass flow rate
# -------------------------------
for m_dot in m_dot_values:
    m_steam = m_dot * steam_fraction
    m_net = m_steam * (1 - ejector_penalty)
    delta_h = h_sep - h_cond  # J/kg
    W_t = m_net * delta_h / 1000  # Convert to kW
    W_t_results.append(W_t)

# -------------------------------
# Plot Mass Flow Rate vs Power Output
# -------------------------------
plt.figure(figsize=(7, 5))
plt.plot(m_dot_values, W_t_results, marker='o')
plt.xlabel('Mass Flow Rate (kg/s)')
plt.ylabel('Power Output (kW)')
plt.title('Power Output vs Mass Flow Rate at Separator Pressure 3 bar abs')
plt.grid(True)
plt.show()

# -------------------------------
# Save results to Excel
# -------------------------------
output_df = pd.DataFrame({
    'Mass Flow Rate (kg/s)': m_dot_values,
    'Power Output (kW)': W_t_results
})

# Convert ke DataFrame
df = pd.DataFrame(data)

# Simpan ke Excel file
df.to_excel("singleflash_results.xlsx", index=False)

print("✅ Data hasil simulasi disimpan ke singleflash_results.xlsx")
