import pandas as pd
from genorun_validation.scores import compute_sdiv


def test_compute_sdiv():
    df = pd.DataFrame({"pca_score":[1.0],"admixture_score":[1.0],"ibd_score":[1.0],"roh_score":[1.0]})
    s = compute_sdiv(df, {"pca":0.3,"admixture":0.3,"ibd":0.25,"roh":0.15})
    assert abs(float(s.iloc[0]) - 1.0) < 1e-9
