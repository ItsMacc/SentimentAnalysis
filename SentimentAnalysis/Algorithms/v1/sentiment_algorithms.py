from Vectorizer.v1 import vectorizer


def momentum_based_sentiment(sentiment_vectors, alpha=0.5, beta=0.5):
    """
    Calculates sentiment using a momentum-based approach.

    :param sentiment_vectors: List of sentiment vectors representing past sentiment.
    :param alpha: Immediate weight for the current sentiment (short-term impact).
    :param beta: Momentum factor for the previous sentiment (long-term influence).
    :return: Adjusted sentiment score considering momentum.
    """
    if not sentiment_vectors:
        return 0  # Default value if no input

    prev_score = vectorizer.v2s(sentiment_vectors[0])  # Start with the first sentiment score
    momentum = 0  # Initialize momentum

    for vector in sentiment_vectors[1:]:
        current_score = vectorizer.v2s(vector)
        sentiment_change = current_score - prev_score  # Track sentiment shift

        # Update momentum based on sentiment shift direction
        momentum = beta * momentum + (1 - beta) * sentiment_change

        # Adjust sentiment considering momentum
        adjusted_sentiment = alpha * current_score + (1 - alpha) * (prev_score + momentum)

        prev_score = adjusted_sentiment  # Update previous score

    return prev_score
