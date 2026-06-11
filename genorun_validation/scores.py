import pandas as pd

def compute_sdiv(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    required = ["pca_score", "admixture_score", "ibd_score", "roh_score"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for S_div: {missing}")
    return (weights.get("pca", 0.30) * df["pca_score"] + weights.get("admixture", 0.30) * df["admixture_score"] + weights.get("ibd", 0.25) * df["ibd_score"] + weights.get("roh", 0.15) * df["roh_score"])
