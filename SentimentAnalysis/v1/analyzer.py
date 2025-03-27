from SentimentAnalysis.model import SentimentAnalyzerModel
from SentimentAnalysis.Algorithms.v1.sentiment_algorithms import *
from Vectorizer.v1 import vectorizer


class SentimentAnalyzerV1(SentimentAnalyzerModel):
    def __init__(self, wordset="standard", positive_words_file=None,
                 negative_words_file=None):
        super().__init__("1.0", wordset, positive_words_file, negative_words_file)

    def evaluate_sentiment(self, message, verbose=False):
        """
        Evaluates the sentiment of the given message.
        """
        sentence_parts = self.split_sentences(message)
        sentiment_vectors = []

        # Implementing detailed logging
        verbose_log = [f"Proccessing text: '{message}'\n",
                       f"Sentences: {sentence_parts}\n"]

        for sentence in sentence_parts:
            sentence = self.clean_message(sentence)

            # Logging details
            verbose_log.append(f"\tCurrent Sentence: {sentence}\n")

            # Check if sentence has conjunctions present
            conjunctions_split = self.__handle_conjunctions(sentence)
            if len(conjunctions_split) > 1:
                # Logging details
                verbose_log.append(f"\t\tConjunctions present:\t"
                                   f"{conjunctions_split}\n")

                v1 = self.__compute_sentiment(conjunctions_split[0])
                v2 = self.__compute_sentiment(conjunctions_split[1])
                combined_score = (vectorizer.combine(v1, v2))
                sentiment_vectors.append(combined_score)

                # Logging details
                verbose_log.append(f"\t\tCombined Score: \t\t"
                                   f"{vectorizer.v2s(combined_score)}\n")
            else:
                sentiment_vector = self.__compute_sentiment(sentence)
                sentiment_vectors.append(sentiment_vector)

                # Logging details
                verbose_log.append(f"\tSentiment score: "
                                   f"{vectorizer.v2s(sentiment_vector)}\n")

        # Calculate the score for all vectors
        score = momentum_based_sentiment(sentiment_vectors)

        # Logging details
        verbose_log.append(f"\nfinal score: {score}")

        # Print details
        if verbose:
            print("".join(verbose_log))

        return score

    # ---- HELPER FUNCTIONS ----

    def __compute_sentiment(self, sentence):
        """
        Computes the sentiment of a sentence, considering positive and negative
        words, negations, quantifiers, and diminishers.
        """
        words = sentence.split()
        positive_count = sum(
            1 for word in words if word in self.positive_words)
        negative_count = sum(
            1 for word in words if word in self.negative_words)
        negation_count = sum(1 for word in words if word in self.NEGATIONS)

        quantifier_multiplier = 1
        diminisher_multiplier = 1
        previous_word = None

        for word in words:
            # Apply quantifiers
            if word in self.QUANTIFIERS:
                quantifier_multiplier *= self.__apply_quantifier(word, previous_word)
            # Apply diminishers
            if word in self.DIMINISHERS:
                diminisher_multiplier *= self.__apply_diminisher(word, previous_word)

            previous_word = word

        base_sentiment = positive_count - negative_count
        negation_adjustment = self.__adjust_for_negations(base_sentiment, negation_count)

        # Return the sentiment vector
        intensity = quantifier_multiplier * diminisher_multiplier
        return vectorizer.s2v(base_sentiment, negation_adjustment, intensity)

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
