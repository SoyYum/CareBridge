from evaluation import precision_at_k, recall_at_k, reciprocal_rank, ndcg_at_k

def test_metrics():
    got, relevant = ["a", "x", "b"], {"a", "b"}
    assert precision_at_k(got, relevant, 3) == 2/3
    assert recall_at_k(got, relevant, 3) == 1.0
    assert reciprocal_rank(got, relevant) == 1.0
    assert round(ndcg_at_k(got, relevant, 3), 4) == 0.9197
