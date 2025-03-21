import re
from Vectorizer import vectorizer


class SentimentAnalyzer:
    # Constants for negations, quantifiers, diminishers, and conjunctions
    NEGATIONS = {"not", "no", "never", "none", "nothing", "neither", "dont",
                 "wont", "cant", "shouldnt",
                 "wouldnt", "wasnt", "isnt", "havent"}

    QUANTIFIERS = {
        "really": 1.2, "at-all": 1.25, "absolutely": 1.3, "totally": 1.27,
        "very": 1.12, "entirely": 1.35, "quite": 1.15, "extremely": 1.32,
        "highly": 1.4, "definitely": 1.45, "too": 1.25, "completely": 1.45,
        "a lot": 1.34, "more": 1.16, "much": 1.19
    }

    DIMINISHERS = {
        "somewhat": 0.81, "kind-of": 0.74, "a bit": 0.7, "slightly": 0.65,
        "partially": 0.67, "mildly": 0.71, "a-little": 0.75, "fairly": 0.83,
        "moderately": 0.88, "sort-of": 0.8, "not-really": 0.63
    }

    CONJUNCTIONS = {"and", "or", "but", "because", "since", "so", "therefore",
                    "due to", "although",
                    "while", "nor", "either", "neither", "unless", "until",
                    "when", "if", "as",
                    "in-case", "provided-that", "even-though", "so-that",
                    "thus"}

    def __init__(self, positive_words_file, negative_words_file):
        """
        Initializes the SentimentAnalyzer with lists of positive and negative words.
        """
        self.__positive_words = self.__load_words_from_file(positive_words_file)
        self.__negative_words = self.__load_words_from_file(negative_words_file)

        # Initialize variables to track the entire conversation
        self.__previous_sentiment_score = 0
        self.__decay_factor = 0.65  # Exponential decay factor for previous sentiment

    def evaluate_sentiment(self, message):
        """
        Evaluates the sentiment of the given message.
        """
        cleaned_message = self.__clean_message(message)
        sentiment_vector = self.__compute_sentiment(cleaned_message)

        return vectorizer.v2s(sentiment_vector)

    def __compute_sentiment(self, sentence):
        """
        Computes the sentiment of a sentence, considering positive and negative words,
        negations, quantifiers, and diminishers.
        """
        words = sentence.split()
        positive_count = sum(1 for word in words if word in self.__positive_words)
        negative_count = sum(1 for word in words if word in self.__negative_words)
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

    @staticmethod
    def __clean_message(message):
        """
        Cleans the message by removing unwanted characters and converting it to lowercase.
        """
        message = message.lower()

        # Handle contractions
        contractions = {
            "wasn't": "wasnt", "can't": "cant", "don't": "dont",
            "didn't": "didnt",
            "isn't": "isnt", "won't": "wont", "haven't": "havent",
            "shouldn't": "shouldnt",
            "wouldn't": "wouldnt", "couldn't": "couldnt", "you're": "youre",
            "i'm": "im",
            "he's": "hes", "she's": "shes", "it's": "its", "they're": "theyre"
        }

        for contraction, replacement in contractions.items():
            message = message.replace(contraction, replacement)

        # Remove unwanted punctuation
        message = ''.join([char for char in message if char not in ["'"]])
        message = ' '.join(message.split())

        # Handle multi-word quantifiers/diminishers
        replacements = {
            "a little": "a-little", "a lot": "a-lot", "kind of": "kind-of",
            "a bit": "a-bit", "sort of": "sort-of", "not really": "not-really",
            "in case": "in-case", "provided that": "provided-that",
            "even though": "even-though", "so that": "so-that",
            "due to": "due-to"
        }

        for old, new in replacements.items():
            message = message.replace(old, new)

        return message

    @staticmethod
    def __load_words_from_file(file_path):
        """
        Loads a list of words from the given file.
        """
        if file_path.endswith('.txt'):
            try:
                with open(file_path, 'r') as file:
                    return [line.strip() for line in file.readlines()]
            except IOError:
                raise ValueError(f"Unable to read file at {file_path}")
        return []

    def __log_analysis_details(self):
        pass
