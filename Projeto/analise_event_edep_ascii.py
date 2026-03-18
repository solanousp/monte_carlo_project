from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# CAMINHOS
# ==========================================
arquivo_header = Path("/Users/solanorigotti/EventEdep.header")
arquivo_dados = Path("/Users/solanorigotti/EventEdep.phsp")

saida = Path("/Users/solanorigotti/Documents/TNA5763_MonteCarlo/Projeto/output_event")
saida.mkdir(parents=True, exist_ok=True)


# ==========================================
# PARÂMETROS
# ==========================================
FWHM_REF = 0.07      # 7% em 662 keV
E_REF = 0.662        # MeV
N_CANAIS = 1024
E_MAX = 0.8          # MeV
THRESHOLD = 0.010    # MeV = 10 keV


# ==========================================
# LEITURA
# ==========================================
with open(arquivo_dados, "r", encoding="utf-8") as f:
    linhas = [linha.strip() for linha in f if linha.strip()]

edep = np.array([float(x) for x in linhas], dtype=float)
edep = edep[edep >= 0]

zeros = edep[edep == 0]
nao_zeros = edep[edep > 0]
edep_det = edep[edep > THRESHOLD]


# ==========================================
# ESTATÍSTICAS
# ==========================================
print("=" * 60)
print("ANÁLISE MELHORADA DO EventEdep")
print("=" * 60)
print(f"N total de eventos           : {len(edep)}")
print(f"N com Edep = 0               : {len(zeros)} ({100*len(zeros)/len(edep):.2f}%)")
print(f"N com Edep > 0               : {len(nao_zeros)} ({100*len(nao_zeros)/len(edep):.2f}%)")
print(f"N acima do threshold         : {len(edep_det)} ({100*len(edep_det)/len(edep):.2f}%)")
print(f"Edep total                   : {edep.sum():.6f} MeV")
print(f"Edep média global            : {edep.mean():.6f} MeV")
print(f"Edep média (Edep > 0)        : {nao_zeros.mean():.6f} MeV")
print(f"Edep média (acima threshold) : {edep_det.mean():.6f} MeV")
print(f"Edep máximo                  : {edep.max():.6f} MeV")
print("=" * 60)


# ==========================================
# RESOLUÇÃO
# sigma(E) ~ a * sqrt(E)
# ==========================================
sigma_ref = (FWHM_REF * E_REF) / 2.355
a = sigma_ref / np.sqrt(E_REF)

def sigma_E(E):
    E = np.clip(E, 0.0, None)
    return a * np.sqrt(E)

sigma = sigma_E(edep_det)
edep_borrado = np.random.normal(edep_det, sigma)
edep_borrado = np.clip(edep_borrado, 0.0, None)


# ==========================================
# CONVERSÃO PARA MCA
# ==========================================
ganho = N_CANAIS / E_MAX
canal = edep_borrado * ganho

mask = (canal >= 0) & (canal < N_CANAIS)
edep_det = edep_det[mask]
edep_borrado = edep_borrado[mask]
canal = canal[mask]


# ==========================================
# GRÁFICO 1 - bruto com zeros
# ==========================================
plt.figure(figsize=(9, 5))
plt.hist(edep, bins=300, range=(0, 0.8))
plt.xlabel("Energia depositada por evento (MeV)")
plt.ylabel("Contagens")
plt.title("Espectro bruto por evento (incluindo zeros)")
plt.tight_layout()
plt.savefig(saida / "01_bruto_com_zeros.pdf")
plt.show()


# ==========================================
# GRÁFICO 2 - bruto sem zeros
# ==========================================
plt.figure(figsize=(9, 5))
plt.hist(nao_zeros, bins=300, range=(0, 0.8))
plt.xlabel("Energia depositada por evento (MeV)")
plt.ylabel("Contagens")
plt.title("Espectro bruto por evento (Edep > 0)")
plt.tight_layout()
plt.savefig(saida / "02_bruto_sem_zeros.pdf")
plt.show()


# ==========================================
# GRÁFICO 3 - bruto sem zeros em log
# ==========================================
plt.figure(figsize=(9, 5))
plt.hist(nao_zeros, bins=300, range=(0, 0.8), log=True)
plt.xlabel("Energia depositada por evento (MeV)")
plt.ylabel("Contagens (log)")
plt.title("Espectro bruto por evento (Edep > 0, log)")
plt.tight_layout()
plt.savefig(saida / "03_bruto_sem_zeros_log.pdf")
plt.show()


# ==========================================
# GRÁFICO 4 - espectro detectado (threshold)
# ==========================================
plt.figure(figsize=(9, 5))
plt.hist(edep_det, bins=300, range=(0, 0.8))
plt.xlabel("Energia depositada detectável (MeV)")
plt.ylabel("Contagens")
plt.title(f"Espectro após threshold ({THRESHOLD*1000:.0f} keV)")
plt.tight_layout()
plt.savefig(saida / "04_threshold.pdf")
plt.show()


# ==========================================
# GRÁFICO 5 - com resolução
# ==========================================
plt.figure(figsize=(9, 5))
plt.hist(edep_borrado, bins=300, range=(0, 0.8))
plt.xlabel("Energia medida (MeV)")
plt.ylabel("Contagens")
plt.title("Espectro com resolução experimental")
plt.tight_layout()
plt.savefig(saida / "05_com_resolucao.pdf")
plt.show()


# ==========================================
# GRÁFICO 6 - MCA
# ==========================================
plt.figure(figsize=(9, 5))
plt.hist(canal, bins=N_CANAIS, range=(0, N_CANAIS))
plt.xlabel("Canal MCA")
plt.ylabel("Contagens")
plt.title("Espectro final tipo experimental")
plt.tight_layout()
plt.savefig(saida / "06_mca.pdf")
plt.show()


# ==========================================
# GRÁFICO 7 - zoom até 550 keV
# ==========================================
plt.figure(figsize=(9, 5))
plt.hist(edep_det, bins=250, range=(0, 0.55))
plt.xlabel("Energia depositada detectável (MeV)")
plt.ylabel("Contagens")
plt.title("Zoom da região Compton")
plt.tight_layout()
plt.savefig(saida / "07_zoom_compton.pdf")
plt.show()


# ==========================================
# EXPORTAÇÃO
# ==========================================
pd.DataFrame({
    "Edep_detectavel_MeV": edep_det,
    "E_measured_MeV": edep_borrado,
    "Canal_MCA": canal
}).to_csv(saida / "eventedep_detectado.csv", index=False)

hist, edges = np.histogram(canal, bins=N_CANAIS, range=(0, N_CANAIS))
centros = 0.5 * (edges[:-1] + edges[1:])

pd.DataFrame({
    "canal": centros,
    "counts": hist
}).to_csv(saida / "eventedep_mca_melhorado.csv", index=False)

print(f"\nArquivos salvos em:\n{saida}")