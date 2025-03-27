from SentimentAnalysis.model import SentimentAnalyzerModel


class SentimentAnalyzerV2(SentimentAnalyzerModel):
    def __init__(self, wordset="standard", positive_words_file=None,
                 negative_words_file=None):
        super().__init__("2.0", wordset, positive_words_file, negative_words_file)

    def evaluate_sentiment(self, message, verbose=False):
        """
        Evaluates the sentiment of the given message.
        """
        sentence_parts = self.split_sentences(message)
        sentiment_vectors = []

        # Implementing detailed logging
        verbose_log = [f"Proccessing text: '{message}'\n",
                       f"Sentences: {sentence_parts}\n"]

        return 0

    # ---- HELPER FUNCTIONS ----

    def __compute_sentiment(self, sentence):
        """
        Computes the sentiment of a sentence, considering positive and negative
        words, negations, quantifiers, and diminishers.
        """
        pass

    def __apply_quantifier(self, word, previous_word):
        """
        Applies the quantifier adjustment based on the previous word's negation status.
        """
        quantifier_value = self.QUANTIFIERS[word]
        if previous_word in self.NEGATIONS:
            return 1 - (quantifier_value - 1)
        return quantifier_value

    def __apply_diminisher(self, word, previous_word):
        """
        Applies the diminisher adjustment based on the previous word's negation status.
        """
        diminisher_value = self.DIMINISHERS[word]
        if previous_word in self.NEGATIONS:
            return 1 + (1 - diminisher_value)
        return diminisher_value

    def __handle_conjunctions(self, message):
        # Further split each sentence by conjunctions
        words = message.split()
        conjunction_indices = [0]

        for i, w in enumerate(words):
            if w in self.CONJUNCTIONS:
                conjunction_indices.append(i + 1)

        conjunction_indices.append(len(words))

        split_sentences = [" ".join(words[conjunction_indices[i] : conjunction_indices[i+1]])for
                           i in range(len(conjunction_indices) -1)]

        return split_sentences

    @staticmethod
    def __adjust_for_negations(base_sentiment, negation_count):
        """
        Adjusts sentiment based on the number of negations in the sentence.
        """
        if negation_count == 0:
            return 1  # No negation, return positive sentiment

        is_odd_negation = negation_count % 2 == 1
        if base_sentiment > 0 and is_odd_negation:
            return -1  # Positive sentiment becomes negative
        elif base_sentiment < 0 and is_odd_negation:
            return 0  # Negative sentiment becomes neutral
        elif base_sentiment == 0:
            return -1 if is_odd_negation else 1  # Neutral becomes negative if odd negation, else positive

        return 1
