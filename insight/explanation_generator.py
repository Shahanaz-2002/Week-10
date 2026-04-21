class ExplanationGenerator:

    def generate_explanation(self, retrieved_cases: list) -> str:

        # No cases found
        if not retrieved_cases:
            return (
                "No similar cases were found in the database. "
                "The recommendation is based on limited available information."
            )

        case_count = len(retrieved_cases)

        # Extract similarity values 
        similarities = []

        for case in retrieved_cases:
            try:
                sim = float(case.get("similarity", 0.0))  
                similarities.append(sim)
            except Exception:
                continue

        # Safety check
        if not similarities:
            avg_similarity = 0.0
        else:
            avg_similarity = (sum(similarities) / len(similarities)) * 100

        # Use top case
        top_case = retrieved_cases[0]

        category = top_case.get("category", "an unspecified category")
        resolution = top_case.get("resolution_notes", "standard resolution procedures")

        try:
            top_score = float(top_case.get("similarity", 0.0)) * 100  
        except Exception:
            top_score = 0.0

        # Build explanation
        explanation = (
            f"{case_count} similar cases were retrieved from historical data. "
            f"The most relevant case has a similarity score of {top_score:.1f}%, "
            f"falling under category '{category}'. "
            f"On average, retrieved cases show {avg_similarity:.1f}% similarity. "
            f"These cases were commonly resolved by '{resolution}', "
            f"which supports the suggested resolution."
        )

        return explanation