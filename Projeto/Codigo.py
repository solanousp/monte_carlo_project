import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# carregar
df = pd.read_csv("/Applications/topas/EdepCrystal.csv", comment="#", header=None)

# transformar em vetor 1D
spectrum = df.iloc[0].values

# eixo de energia (igual ao que você definiu no TOPAS)
Emin = 0.0
Emax = 0.7  # MeV
nbins = len(spectrum)

energy = np.linspace(Emin, Emax, nbins)

# plot
plt.figure(figsize=(8,5))
plt.plot(energy * 1000, spectrum)  # keV

plt.xlabel("Energia (keV)")
plt.ylabel("Contagens")
plt.title("Espectro Cs-137 - GAGG:Ce")

plt.grid(alpha=0.3)
plt.xlim(0, 700)
plt.savefig("/Users/solanorigotti/Documents/TNA5763_MonteCarlo/Projeto/output/Cs137_energy_Spectrum.pdf")
plt.show()