"""
Testes automáticos do pipeline de dados, integridade e modelação — Projeto AASE.
Valida critérios de elegibilidade, anti-leakage, regras clínicas e consistência de datasets.
"""

import csv
import math
import statistics
from datetime import date
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_ORIG = REPO_ROOT / "dados_aase_202627"
DATA_PREP = REPO_ROOT / "03_data_preparation"
MODEL_DIR = REPO_ROOT / "04_modeling"


# -----------------------------------------------------------------------------
# 1. FUNÇÕES AUXILIARES DE NORMALIZAÇÃO E TRATAMENTO
# -----------------------------------------------------------------------------

def norm_ep(ep: str) -> str:
    return ep.strip().replace(" ", "").upper()

def parse_data(d: str):
    d = d.strip()
    if "/" in d:
        parts = d.split("/")
        if len(parts) == 3 and len(parts[2]) == 4:
            try:
                return date(int(parts[2]), int(parts[1]), int(parts[0]))
            except (ValueError, TypeError):
                return None
    elif "-" in d:
        parts = d.split("-")
        if len(parts) == 3 and len(parts[0]) == 4:
            try:
                y, m, day = int(parts[0]), int(parts[1]), int(parts[2])
                if m > 12:
                    m, day = day, m
                return date(y, m, day)
            except (ValueError, TypeError):
                return None
    return None

def is_valid_spo2(val) -> bool:
    try:
        f = float(val)
        return math.isfinite(f) and 50.0 <= f <= 100.0
    except (ValueError, TypeError):
        return False

def calc_desat_deficit(val) -> float:
    try:
        f = float(val)
        if 50.0 <= f < 90.0:
            return 90.0 - f
        return 0.0
    except (ValueError, TypeError):
        return 0.0


# -----------------------------------------------------------------------------
# 2. TESTES DE NORMALIZAÇÃO E LIMPEZA
# -----------------------------------------------------------------------------

def test_id_normalization():
    assert norm_ep("ep016") == "EP016"
    assert norm_ep("EP 016") == "EP016"
    assert norm_ep(" EP011") == "EP011"
    assert norm_ep("ep029  ") == "EP029"

def test_date_parsing_formats():
    # Formato DD/MM/YYYY
    assert parse_data("13/02/2024") == date(2024, 2, 13)
    # Formato YYYY-MM-DD
    assert parse_data("2024-02-13") == date(2024, 2, 13)
    # Formato com inversão dia/mês YYYY-DD-MM (mês > 12)
    assert parse_data("2024-13-02") == date(2024, 2, 13)
    # Data inexistente
    assert parse_data("2024-02-31") is None
    # String nula ou vazia
    assert parse_data("") is None

def test_physiological_filtering():
    assert is_valid_spo2(95.0)
    assert is_valid_spo2(50.0)
    assert is_valid_spo2(100.0)
    assert not is_valid_spo2(49.9)
    assert not is_valid_spo2(100.1)
    assert not is_valid_spo2(250.0)
    assert not is_valid_spo2(-5.0)
    assert not is_valid_spo2(None)
    assert not is_valid_spo2("N/A")


# -----------------------------------------------------------------------------
# 3. TESTES DE ELEGIBILIDADE E CASOS-LIMITE (FRONTEIRA)
# -----------------------------------------------------------------------------

def check_eligibility(janela_spo2_vals, futuro_spo2_vals):
    n_j = sum(1 for v in janela_spo2_vals if is_valid_spo2(v))
    n_f = sum(1 for v in futuro_spo2_vals if is_valid_spo2(v))
    return n_j >= 5 and n_f >= 3

def test_eligibility_tc1_exact_thresholds():
    # Exatamente 5 válidos na janela inicial e 3 no futuro -> Elegível
    assert check_eligibility([95.0] * 5, [95.0] * 3)

def test_eligibility_tc2_insufficient_initial():
    # 4 válidos na janela inicial (abaixo de 5) e 3 no futuro -> Inelegível
    assert not check_eligibility([95.0] * 4, [95.0] * 3)

def test_eligibility_tc3_insufficient_future():
    # 5 válidos na janela inicial e 2 no futuro (abaixo de 3) -> Inelegível
    assert not check_eligibility([95.0] * 5, [95.0] * 2)

def test_eligibility_tc4_no_valid_spo2():
    # Episódio com observações mas nenhuma SpO2 fisiologicamente válida -> Inelegível
    assert not check_eligibility([250.0, None, 10.0, 30.0], [None, 300.0])

def test_eligibility_tc5_invalid_records_do_not_count():
    # 6 registos no total mas 2 são inválidos -> 4 válidos -> Inelegível
    assert not check_eligibility([95.0, 94.0, 250.0, 93.0, None, 96.0], [95.0] * 3)


# -----------------------------------------------------------------------------
# 4. TESTES DO CÁLCULO DO ALVO (DÉFICE DE DESSATURAÇÃO)
# -----------------------------------------------------------------------------

def test_target_calculation_threshold_90():
    # SpO2 exatamente igual a 90% não acumula défice
    assert calc_desat_deficit(90.0) == 0.0
    assert calc_desat_deficit(91.0) == 0.0

def test_target_calculation_hypoxemia_deficit():
    # SpO2 de 85% acumula exatamente 90 - 85 = 5.0
    assert abs(calc_desat_deficit(85.0) - 5.0) < 1e-6
    # SpO2 de 80.5% acumula 9.5
    assert abs(calc_desat_deficit(80.5) - 9.5) < 1e-6

def test_target_calculation_zero_desaturation():
    futuro_vals = [94.0, 96.0, 98.0, 95.0]
    total_carga = sum(calc_desat_deficit(v) for v in futuro_vals)
    assert total_carga == 0.0


# -----------------------------------------------------------------------------
# 5. TESTES DE INTEGRIDADE TEMPORAL E ANTI-LEAKAGE
# -----------------------------------------------------------------------------

def test_window_temporal_separation():
    # Separação estrita em delta_h = 24.0
    def assign_window(delta_h):
        return "janela" if delta_h < 24.0 else "futuro"

    assert assign_window(0.0) == "janela"
    assert assign_window(23.999) == "janela"
    assert assign_window(24.0) == "futuro"
    assert assign_window(48.0) == "futuro"

def test_anti_leakage_feature_selection():
    # Colunas proibidas como preditores na regressão
    forbidden_terms = ["futur", "total", "alvo", "target", "pat_", "duracao"]
    with open(DATA_PREP / "dataset_regressao_24h.csv", newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))

    EXCLUIR = {
        "episodio", "carga_dessaturacao_futura", "n_registos_futuro", "n_spo2_futuro_validos",
        "carga_dessaturacao", "desat_count", "desat_pct", "duracao_dias",
        "pat_predominante", "pat_label"
    }
    feature_cols = [c for c in header if c not in EXCLUIR and not c.endswith("_total")]

    assert "carga_dessaturacao_futura" not in feature_cols
    assert "n_registos_futuro" not in feature_cols
    assert "n_spo2_futuro_validos" not in feature_cols
    assert "duracao_dias" not in feature_cols

    for col in feature_cols:
        for term in forbidden_terms:
            assert term not in col.lower(), f"Leakage detectado na coluna: {col}"

def test_train_only_median_imputation():
    # Garante que a imputação usa exclusivamente a mediana do treino
    train_data = [{"feat": 10.0}, {"feat": 20.0}, {"feat": 30.0}]  # mediana = 20.0
    test_data = [{"feat": None}]

    medians = {"feat": statistics.median([r["feat"] for r in train_data if r["feat"] is not None])}
    imputed_test_val = test_data[0]["feat"] if test_data[0]["feat"] is not None else medians["feat"]

    assert imputed_test_val == 20.0, "A imputação deve utilizar a mediana do treino (20.0)"


# -----------------------------------------------------------------------------
# 6. TESTES DE CONSISTÊNCIA DOS DATASETS GERADOS
# -----------------------------------------------------------------------------

def test_dataset_regressao_24h_integrity():
    csv_path = DATA_PREP / "dataset_regressao_24h.csv"
    assert csv_path.exists(), "dataset_regressao_24h.csv deve existir"

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Deve conter exatamente 40 episódios elegíveis
    assert len(rows) == 40, f"Esperados 40 episódios elegíveis, encontrados {len(rows)}"

    # Unicidade de identificadores
    eps = [r["episodio"] for r in rows]
    assert len(eps) == len(set(eps)), "Não podem existir episódios duplicados"

    for r in rows:
        # Critérios de SpO2 válida cumpridos
        assert int(r["n_spo2_validos"]) >= 5, f"Episódio {r['episodio']} viola n_spo2_validos >= 5"
        assert int(r["n_spo2_futuro_validos"]) >= 3, f"Episódio {r['episodio']} viola n_spo2_futuro_validos >= 3"
        # Alvo válido
        target_val = float(r["carga_dessaturacao_futura"])
        assert math.isfinite(target_val) and target_val >= 0.0

def test_dataset_final_integrity():
    csv_path = DATA_PREP / "dataset_final.csv"
    assert csv_path.exists(), "dataset_final.csv deve existir"

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Deve conter exatamente 47 episódios únicos com sinais vitais
    assert len(rows) == 47, f"Esperados 47 episódios, encontrados {len(rows)}"

    com_pat = [r for r in rows if r["pat_label"] != "-1"]
    sem_pat = [r for r in rows if r["pat_label"] == "-1"]

    assert len(com_pat) == 39, f"Esperados 39 episódios com patologia, encontrados {len(com_pat)}"
    assert len(sem_pat) == 8, f"Esperados 8 episódios sem patologia, encontrados {len(sem_pat)}"

def test_metadata_consistency():
    meta_path = DATA_PREP / "metadata.csv"
    assert meta_path.exists(), "metadata.csv deve existir"

    with open(meta_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 6, f"Esperadas 6 classes de patologia predominante, encontradas {len(rows)}"

    pat_counts = {r["pat_nome"]: int(r["n_episodios"]) for r in rows}
    assert pat_counts["Doença das Membranas Hialinas"] == 24
    assert pat_counts["Icterícia Neonatal"] == 7
    assert pat_counts["Citomegalovírus"] == 4
    assert pat_counts["Anemia"] == 2
    assert pat_counts["Refluxo Gastroesofágico"] == 1
    assert pat_counts["Persistência do Canal Arterial"] == 1
    assert sum(pat_counts.values()) == 39
