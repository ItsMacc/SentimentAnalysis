import pandas as pd
from collections import defaultdict
import numpy as np
from scipy.stats import ttest_ind

# Load IMDb dataset
df = pd.read_csv("IMDB Dataset.csv")

# Convert sentiment labels to numerical values
df['sentiment'] = df['sentiment'].map({'positive': 1, 'negative': 0})

# Define quantifiers and diminishers
quantifiers = [
    "really", "at-all", "absolutely", "totally", "very", "entirely", "quite",
    "extremely", "highly", "definitely", "too", "completely", "a lot", "more", "much"
]

diminishers = [
    "somewhat", "kind-of", "a bit", "slightly", "partially", "mildly", "a-little",
    "fairly", "moderately", "sort-of", "not-really", "sometimes"
]

def calculate_weights(dataframe, qnts, dims, min_freq=10, alpha=0.05):
    """
    Calculate weights for quantifiers and diminishers based on their weighted sentiment impact.
    """
    quantifier_scores = defaultdict(lambda: [[], []])  # [positive_sentiments, negative_sentiments]
    diminisher_scores = defaultdict(lambda: [[], []])  # [positive_sentiments, negative_sentiments]

    for _, row in dataframe.iterrows():
        text = row['review']
        sentiment = row['sentiment']
        words = text.lower().split()

        for word in words:
            if word in qnts:
                quantifier_scores[word][0 if sentiment == 1 else 1].append(sentiment)
            if word in dims:
                diminisher_scores[word][0 if sentiment == 1 else 1].append(sentiment)

    def weighted_impact(scores, freq_min, alph):
        pos_sentiments, neg_sentiments = scores
        total_count = len(pos_sentiments) + len(neg_sentiments)

        if total_count < freq_min:
            return None

        if pos_sentiments and neg_sentiments:
            _, p_value = ttest_ind(pos_sentiments, neg_sentiments, equal_var=False)
            if p_value > alph:
                return None

        mean_sentiment = (np.sum(pos_sentiments) + np.sum(neg_sentiments)) / total_count
        return float(mean_sentiment)

    qnts_weights = {word: weighted_impact(scores, min_freq, alpha) for word, scores in quantifier_scores.items()}
    dims_weight = {word: weighted_impact(scores, min_freq, alpha) for word, scores in diminisher_scores.items()}

    qnts_weights = {k: v for k, v in qnts_weights.items() if v is not None}
    dims_weight = {k: v for k, v in dims_weight.items() if v is not None}

    return qnts_weights, dims_weight

# Calculate weights
quantifier_weights, diminisher_weights = calculate_weights(df, quantifiers, diminishers, min_freq=5, alpha=0.06)

# Normalize weights
q = {word: round(float(1 + (1 - score)), 2) for word, score in
     quantifier_weights.items()}
d = {word: round(float(1 - score), 2) for word, score in
     diminisher_weights.items()}