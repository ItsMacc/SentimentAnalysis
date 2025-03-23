import re
from SentimentAnalysis.Exceptions.errors import *
from SentimentAnalysis.analyzer_2_0 import *
from SentimentAnalysis.Algorithms.sentiment_algorithms import *


class SentimentAnalyzer:
    # Constants for negations, quantifiers, diminishers, and conjunctions
    NEGATIONS = {"not", "no", "never", "none", "nothing", "neither", "dont",
                 "wont", "cant", "shouldnt", "wouldnt", "wasnt", "isnt",
                 "havent"}

    QUANTIFIERS = {
        'very': 1.41, 'extremely': 1.51, 'really': 1.53, 'too': 1.57,
        'more': 1.48, 'totally': 1.59, 'much': 1.52, 'quite': 1.43,
        'absolutely': 1.57, 'entirely': 1.52, 'completely': 1.63,
        'highly': 1.26, 'definitely': 1.33, 'a-lot': 1.55, 'at-all': 1.35
    }

    DIMINISHERS = {
        'sometimes': 0.39, 'mildly': 0.84, 'somewhat': 0.45, 'slightly': 0.49,
        'partially': 0.51, 'fairly': 0.52, 'moderately': 0.63, 'sort-of': 0.75,
        'kind-of': 0.57, 'a bit': 0.8, 'a-little': 0.5, 'not-really': 0.3
    }

    CONJUNCTIONS = {"and", "or", "but", "because", "since", "so", "therefore",
                    "due to", "although", "while", "nor", "either",
                    "neither", "unless", "until", "when", "if", "as",
                    "in-case", "provided-that", "even-though", "so-that"}

    def __init__(self, wordset="standard", positive_words_file=None,
                 negative_words_file=None, model="1.0"):
        """
        Initializes the SentimentAnalyzer with lists of positive and negative LanguageAssets.
        """

        # Validate model
        current_models = ["1.0", "2.0", "3.0"]
        if model not in current_models:
            raise InvalidModelError(model)

        # Validate wordset
        if wordset not in ["standard", "extended", "custom"]:
            raise InvalidWordsetError(wordset)
        else:
            if wordset != "custom":
                positive_words_path = f"LanguageAssets/{wordset}/positive_words.txt"
                negative_words_path = f"LanguageAssets/{wordset}/negative_words.txt"
            else:
                if positive_words_file is None or negative_words_file is None:
                    raise MissingCustomFilesError()
                else:
                    positive_words_path = positive_words_file
                    negative_words_path = negative_words_file

        self.__positive_words = self.__load_words_from_file(positive_words_path)
        self.__negative_words = self.__load_words_from_file(negative_words_path)

        # Initialize model version
        self.model = model

    def evaluate_sentiment(self, message, verbose=False):
        """
        Evaluates the sentiment of the given message.
        """
        sentence_parts = self.__split_sentences(message)
        sentiment_vectors = []

        # Implementing detailed logging
        verbose_log = [f"Proccessing text: '{message}'\n",
                       f"Sentences: {sentence_parts}\n"]

        for sentence in sentence_parts:
            sentence = self.__clean_message(sentence)

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
            1 for word in words if word in self.__positive_words)
        negative_count = sum(
            1 for word in words if word in self.__negative_words)
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
    def __split_sentences(text):
        """
        Splits the input text into parts based on sentence-ending punctuation (.?!)
        and conjunctions, while preserving punctuation. Removes empty sentences.
        """
        sentence_parts = re.split(r'([.?!])', text)
        reconstructed_sentences = []

        for part in sentence_parts:
            if part not in ".!?":
                reconstructed_sentences.append(part.strip())

        return reconstructed_sentences

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
    def __clean_message(message):
        """
        Cleans the message by removing unwanted characters and converting it to lowercase.
        """
        message = message.lower()

        contractions = {
            "wasn't": "wasnt", "can't": "cant", "don't": "dont",
            "didn't": "didnt", "isn't": "isnt", "won't": "wont",
            "haven't": "havent", "shouldn't": "shouldnt", "wouldn't": "wouldnt",
            "couldn't": "couldnt", "you're": "youre", "i'm": "im",
            "he's": "hes", "she's": "shes", "it's": "its", "they're": "theyre"
        }

        for contraction, replacement in contractions.items():
            message = message.replace(contraction, replacement)

        # Replace multi-word quantifiers and diminishers
        message = re.sub(r'\b(a lot)\b', 'a-lot', message)
        message = re.sub(r'\b(a little)\b', 'a-little', message)
        message = re.sub(r'\b(not really)\b', 'not-really', message)
        message = re.sub(r'\b(kind of)\b', 'kind-of', message)
        message = re.sub(r'\b(sort of)\b', 'sort-of', message)
        message = re.sub(r'\b(a bit)\b', 'a-bit', message)

        # Handle conjunctions and 'like a' / 'like an'
        message = re.sub(r'\b(so that)\b', 'so-that', message)
        message = re.sub(r'\b(even though)\b', 'even-though', message)
        message = re.sub(r'\b(provided that)\b', 'provided-that', message)
        message = re.sub(r'\b(in case)\b', 'in-case', message)
        message = re.sub(r'\blike a\b', 'like-a', message)
        message = re.sub(r'\blike an\b', 'like-an', message)

        message = ''.join([char for char in message if char not in ["'","."]])
        message = ' '.join(message.split())

        return message

    @staticmethod
    def __load_words_from_file(file_path):
        """
        Loads a list of LanguageAssets from the given file.
        """
        try:
            with open(file_path, 'r') as file:
                return [line.strip() for line in file.readlines()]
        except IOError:
            raise ValueError(f"Unable to read file at {file_path}")
