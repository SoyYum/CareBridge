import argparse, csv, json, math

def precision_at_k(retrieved, relevant, k):
    return sum(x in relevant for x in retrieved[:k]) / k if k else 0.0

def recall_at_k(retrieved, relevant, k):
    return sum(x in relevant for x in retrieved[:k]) / len(relevant) if relevant else 0.0

def reciprocal_rank(retrieved, relevant):
    for rank, item in enumerate(retrieved, 1):
        if item in relevant: return 1.0 / rank
    return 0.0

def ndcg_at_k(retrieved, relevant, k):
    dcg = sum(1 / math.log2(i + 2) for i, x in enumerate(retrieved[:k]) if x in relevant)
    ideal = min(len(relevant), k)
    idcg = sum(1 / math.log2(i + 2) for i in range(ideal))
    return dcg / idcg if idcg else 0.0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    with open(args.csv_file, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    metrics = {"precision_at_k": [], "recall_at_k": [], "mrr": [], "ndcg_at_k": []}
    for row in rows:
        got = [x for x in row.get("retrieved_chunk_ids", "").split(";") if x]
        relevant = set(x for x in row.get("relevant_chunk_ids", "").split(";") if x)
        metrics["precision_at_k"].append(precision_at_k(got, relevant, args.k))
        metrics["recall_at_k"].append(recall_at_k(got, relevant, args.k))
        metrics["mrr"].append(reciprocal_rank(got, relevant))
        metrics["ndcg_at_k"].append(ndcg_at_k(got, relevant, args.k))
    print(json.dumps({k: round(sum(v)/len(v), 4) if v else None for k, v in metrics.items()}, indent=2))
    print("These metrics evaluate supplied retrieval outputs, not a live RAG run.")

if __name__ == "__main__":
    main()
