import re
from Vectorizer import vectorizer


class SentimentAnalyzer:
    # Constants for negations, quantifiers, diminishers, and conjunctions
    NEGATIONS = {"not", "no", "never", "none", "nothing", "neither", "dont",
                 "wont", "cant", "shouldnt", "wouldnt", "wasnt", "isnt",
                 "havent"}

    QUANTIFIERS = {
        'very': 1.41, 'extremely': 1.51, 'really': 1.53, 'too': 1.57,
        'more': 1.48, 'totally': 1.59, 'much': 1.52, 'quite': 1.43,
        'absolutely': 1.57, 'entirely': 1.52, 'completely': 1.63,
        'highly': 1.26, 'definitely': 1.33
    }

    DIMINISHERS = {
        'sometimes': 0.39, 'mildly': 0.84, 'somewhat': 0.45, 'slightly': 0.49,
        'partially': 0.51, 'fairly': 0.52, 'moderately': 0.63, 'sort-of': 0.75,
        'kind-of': 0.57
    }

    CONJUNCTIONS = {"and", "or", "but", "because", "since", "so", "therefore",
                    "due to", "although", "while", "nor", "either",
                    "neither", "unless", "until", "when", "if", "as",
                    "in-case", "provided-that", "even-though", "so-that"}

    def __init__(self, positive_words_file, negative_words_file, model="1.0"):
        """
        Initializes the SentimentAnalyzer with lists of positive and negative words.
        """
        self.__positive_words = self.__load_words_from_file(positive_words_file)
        self.__negative_words = self.__load_words_from_file(negative_words_file)

        # Initialize variables to track the entire conversation
        self.__previous_sentiment_score = 0
        self.__decay_factor = 0.65  # Exponential decay factor for previous sentiment

        self.model = model

    def evaluate_sentiment(self, message):
        """
        Evaluates the sentiment of the given message.
        """
        cleaned_message = self.__clean_message(message)
        sentence_parts = self.__split_sentences(cleaned_message)

        sentiment_vectors = []

        for sentence in sentence_parts:
            part_vector = self.__compute_sentiment(sentence)
            sentiment_vectors.append(part_vector)

        # Combine all sentiment vectors into one
        sentiment_vector = sentiment_vectors[0] if sentiment_vectors else None

        for i in range(1, len(sentiment_vectors)):
            sentiment_vector = vectorizer.combine(sentiment_vector, sentiment_vectors[i])

        return vectorizer.v2s(sentiment_vector) if sentiment_vector else 0

    # ---- HELPER FUNCTIONS ----

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

    def __split_sentences(self, text):
        """
        Splits the input text into parts based on sentence-ending punctuation (.?!)
        and conjunctions, while preserving punctuation.
        """

        sentence_parts = re.split(r'([.?!])', text)

        # Reconstruct sentences by pairing punctuation back with preceding text
        reconstructed_sentences = []
        buffer = ""

        for part in sentence_parts:
            if part in ".?!":
                buffer += part  # Attach punctuation to the sentence
                reconstructed_sentences.append(buffer.strip())
                buffer = ""
            else:
                buffer = part.strip()

        if buffer:  # Catch any leftover part
            reconstructed_sentences.append(buffer)

        # Further split each sentence by conjunctions
        final_parts = []
        for sentence in reconstructed_sentences:
            words = sentence.split()
            conjunction_indices = [0]

            for i, word in enumerate(words):
                if word in self.CONJUNCTIONS:
                    conjunction_indices.append(i + 1)

            conjunction_indices.append(len(words))

            split_sentences = [
                " ".join(words[conjunction_indices[i]:conjunction_indices[i + 1]])
                for i in range(len(conjunction_indices) - 1)
            ]

            final_parts.extend(split_sentences)

        return final_parts

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

        # Remove unwanted punctuation but keep .?!
        message = ''.join([char for char in message if char not in ["'"]])
        message = ' '.join(message.split())

        return message

    @staticmethod
    def __load_words_from_file(file_path):
        """
        Loads a list of words from the given file.
        """
        try:
            with open(file_path, 'r') as file:
                return [line.strip() for line in file.readlines()]
        except IOError:
            raise ValueError(f"Unable to read file at {file_path}")

