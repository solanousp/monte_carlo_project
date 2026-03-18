import re
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


# =========================
# CAMINHOS
# =========================
arquivo_total = Path("/Users/solanorigotti/topas_dev/OpenTOPAS-build/EdepCrystalTotal.csv")
arquivo_spectrum = Path("/Users/solanorigotti/topas_dev/OpenTOPAS-build/EdepCrystalSpectrum.csv")

# número de histórias
N_HISTORIAS = 200000


# =========================
# FUNÇÕES
# =========================
def ler_edep_total(path: Path) -> float:
    with open(path, "r", encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    return float(linhas[-1])


def ler_espectro_topas(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    # linha do cabeçalho dos bins
    linha_bins = None
    for linha in linhas:
        if "Binned by" in linha and "bins of" in linha:
            linha_bins = linha
            break

    if linha_bins is None:
        raise ValueError("Não encontrei a linha com definição de bins.")

    # Exemplo:
    # # Binned by pre-step energy in 200 bins of 0.0035 MeV from 0 MeV to 0.7 MeV
    padrao = r"in\s+(\d+)\s+bins\s+of\s+([0-9eE\.\+\-]+)\s+MeV\s+from\s+([0-9eE\.\+\-]+)\s+MeV\s+to\s+([0-9eE\.\+\-]+)\s+MeV"
    m = re.search(padrao, linha_bins)

    if m is None:
        raise ValueError(f"Não consegui interpretar a linha dos bins:\n{linha_bins}")

    n_bins_fisicos = int(m.group(1))
    bin_width = float(m.group(2))
    e_min = float(m.group(3))
    e_max = float(m.group(4))

    # última linha não comentada = dados
    linha_dados = None
    for linha in reversed(linhas):
        if not linha.startswith("#"):
            linha_dados = linha
            break

    if linha_dados is None:
        raise ValueError("Não encontrei a linha de dados.")

    valores = [float(x.strip()) for x in linha_dados.split(",") if x.strip() != ""]

    if len(valores) % 2 != 0:
        raise ValueError("Quantidade ímpar de valores. Esperava pares (sum, count).")

    pares = np.array(valores).reshape(-1, 2)
    soma_por_bin = pares[:, 0]
    contagem_por_bin = pares[:, 1]

    # TOPAS: bins físicos + underflow + overflow
    n_total_esperado = n_bins_fisicos + 2

    if len(soma_por_bin) != n_total_esperado:
        print(f"[AVISO] Esperava {n_total_esperado} pares "
              f"({n_bins_fisicos} bins + underflow + overflow), "
              f"mas encontrei {len(soma_por_bin)}.")

    # separar
    underflow_sum = soma_por_bin[0]
    underflow_count = contagem_por_bin[0]

    overflow_sum = soma_por_bin[-1]
    overflow_count = contagem_por_bin[-1]

    soma_bins_fisicos = soma_por_bin[1:-1]
    contagem_bins_fisicos = contagem_por_bin[1:-1]

    # bordas e centros dos bins físicos
    edges = np.linspace(e_min, e_max, n_bins_fisicos + 1)
    centros = 0.5 * (edges[:-1] + edges[1:])

    if len(centros) != len(soma_bins_fisicos):
        raise ValueError(
            f"Inconsistência: {len(centros)} centros para "
            f"{len(soma_bins_fisicos)} bins físicos."
        )

    return {
        "n_bins_fisicos": n_bins_fisicos,
        "bin_width": bin_width,
        "e_min": e_min,
        "e_max": e_max,
        "edges": edges,
        "centros": centros,
        "soma_bins_fisicos": soma_bins_fisicos,
        "contagem_bins_fisicos": contagem_bins_fisicos,
        "underflow_sum": underflow_sum,
        "underflow_count": underflow_count,
        "overflow_sum": overflow_sum,
        "overflow_count": overflow_count,
    }


# =========================
# LEITURA
# =========================
edep_total = ler_edep_total(arquivo_total)
dados = ler_espectro_topas(arquivo_spectrum)

centros = dados["centros"]
counts = dados["contagem_bins_fisicos"]
somas = dados["soma_bins_fisicos"]

energia_media_no_bin = np.divide(
    somas,
    counts,
    out=np.zeros_like(somas, dtype=float),
    where=counts > 0
)

edep_media_por_historia = edep_total / N_HISTORIAS

# energia média do eixo de pre-step ponderada por contagem
energia_media_ponderada_bins = np.sum(centros * counts) / np.sum(counts)

# total de entradas no histograma físico
entradas_totais = np.sum(counts)


# =========================
# RESUMO
# =========================
print("=" * 60)
print("RESUMO DA ANÁLISE TOPAS (V2)")
print("=" * 60)
print(f"Arquivo total            : {arquivo_total}")
print(f"Arquivo espectro         : {arquivo_spectrum}")
print(f"N histórias              : {N_HISTORIAS}")
print(f"N bins físicos           : {dados['n_bins_fisicos']}")
print(f"Faixa energética         : {dados['e_min']} a {dados['e_max']} MeV")
print(f"Largura do bin           : {dados['bin_width']} MeV")
print(f"Edep total               : {edep_total:.6f} MeV")
print(f"Edep médio por história  : {edep_media_por_historia:.6f} MeV")
print(f"Entradas totais nos bins : {entradas_totais:.0f}")
print(f"Underflow count          : {dados['underflow_count']:.0f}")
print(f"Overflow count           : {dados['overflow_count']:.0f}")
print(f"Underflow sum            : {dados['underflow_sum']:.6f} MeV")
print(f"Overflow sum             : {dados['overflow_sum']:.6f} MeV")
print(f"E média ponderada (x=count): {energia_media_ponderada_bins:.6f} MeV")
print("=" * 60)


# =========================
# TABELA RESUMIDA
# =========================
idx_max_count = int(np.argmax(counts))
idx_max_sum = int(np.argmax(somas))

print("\nBIN DE MAIOR CONTAGEM")
print(f"Centro do bin  : {centros[idx_max_count]:.6f} MeV")
print(f"Count_in_Bin   : {counts[idx_max_count]:.0f}")
print(f"Sum no bin     : {somas[idx_max_count]:.6f} MeV")

print("\nBIN DE MAIOR SOMA DE ENERGIA")
print(f"Centro do bin  : {centros[idx_max_sum]:.6f} MeV")
print(f"Count_in_Bin   : {counts[idx_max_sum]:.0f}")
print(f"Sum no bin     : {somas[idx_max_sum]:.6f} MeV")


# =========================
# GRÁFICO 1: contagem por bin
# =========================
plt.figure(figsize=(9, 5))
plt.bar(centros, counts, width=dados["bin_width"], align="center")
plt.xlabel("Energia de pre-step (MeV)")
plt.ylabel("Count_in_Bin")
plt.title("TOPAS - EdepCrystalSpectrum (contagem por bin)")
plt.tight_layout()
plt.savefig("Projeto/output/counts_per_bin.pdf")
plt.show()


# =========================
# GRÁFICO 2: soma de energia por bin
# =========================
plt.figure(figsize=(9, 5))
plt.bar(centros, somas, width=dados["bin_width"], align="center")
plt.xlabel("Energia de pre-step (MeV)")
plt.ylabel("Soma de energia depositada no bin (MeV)")
plt.title("TOPAS - EdepCrystalSpectrum (soma por bin)")
plt.tight_layout()
plt.savefig("Projeto/output/energy_sum_per_bin.pdf")
plt.show()


# =========================
# GRÁFICO 3: energia média depositada por entrada
# =========================
plt.figure(figsize=(9, 5))
plt.plot(centros, energia_media_no_bin)
plt.xlabel("Energia de pre-step (MeV)")
plt.ylabel("Energia média depositada por entrada (MeV)")
plt.title("TOPAS - Energia média depositada por entrada em cada bin")
plt.tight_layout()
plt.savefig("Projeto/output/mean_energy_by_entrance.pdf")
plt.show()


# =========================
# SALVAR TABELA LIMPA
# =========================
saida = Path("/Users/solanorigotti/Documents/TNA5763_MonteCarlo/Projeto/output")
saida.mkdir(parents=True, exist_ok=True)

arquivo_out = saida / "EdepCrystalSpectrum_reconstruido.csv"

dados_tabela = np.column_stack([
    centros,
    counts,
    somas,
    energia_media_no_bin
])

np.savetxt(
    arquivo_out,
    dados_tabela,
    delimiter=",",
    header="energia_prestep_MeV,count_in_bin,sum_edep_bin_MeV,edep_media_por_entrada_MeV",
    comments=""
)

print(f"\nTabela reconstruída salva em:\n{arquivo_out}")