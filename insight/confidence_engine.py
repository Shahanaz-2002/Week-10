from config import TOP_K


class ConfidenceEngine:

    def compute_confidence(self, retrieved_cases: list) -> dict:

        # 🔹 No cases
        if not retrieved_cases:
            return {
                "confidence_score": 0.0
            }

        # 🔹 Extract similarity values 
        similarities = []

        for case in retrieved_cases:
            try:
                sim = float(case.get("similarity", 0.0)) 
                similarities.append(sim)
            except Exception:
                continue

        # 🔹 Safety check
        if not similarities:
            return {
                "confidence_score": 0.0
            }

        # 🔹 Average similarity
        avg_similarity = sum(similarities) / len(similarities)

        # 🔹 Support ratio (how many cases retrieved vs expected)
        support_ratio = len(retrieved_cases) / TOP_K if TOP_K > 0 else 0

        # 🔹 Final confidence score
        confidence_score = (0.75 * avg_similarity) + (0.25 * support_ratio)

        # 🔹 Clamp to [0,1] (safety)
        confidence_score = max(0.0, min(1.0, confidence_score))

        return {
            "confidence_score": round(confidence_score, 3)
        }