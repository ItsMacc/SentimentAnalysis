from math import atan
import re

class SentimentAnalyzer:
    def __init__(self, positive_words_file, negative_words_file):
        # Initialize lists of positive and negative words
        self.__positive_words = self.__load_words_from_file(positive_words_file)
        self.__negative_words = self.__load_words_from_file(negative_words_file)

        # Initialize common negations, quantifiers, and diminishers
        self.__negations = [
            "not", "no", "never", "none", "nothing", "neither",
            "dont", "wont", "cant", "shouldnt", "wouldnt", "wasnt", "isnt",
            "havent"
        ]

        self.__quantifiers = {
            "really": 1.2, "at-all": 1.25, "absolutely": 1.3, "totally": 1.27,
            "very": 1.12, "entirely": 1.35, "quite": 1.15, "extremely": 1.32,
            "highly": 1.4, "definitely": 1.45, "too": 1.25, "completely": 1.45,
            "a lot": 1.34, "more": 1.16, "much" : 1.19
        }

        self.__diminishers = {
            "somewhat": 0.81, "kind-of": 0.74, "a bit": 0.7, "slightly": 0.65,
            "partially": 0.67, "mildly": 0.71, "a-little": 0.75, "fairly": 0.83,
            "moderately": 0.88, "sort-of": 0.8, "not-really": 0.63
        }

        # Initialize common conjunctions
        self.__conjunctions = [
            "and", "or", "but", "because", "since", "so", "therefore",
            "due to", "although", "while", "nor", "either",
            "neither", "unless", "until", "when", "if", "as", "in-case",
            "provided-that", "even-though", "so-that", "thus"
        ]

        # Initialize variables to track the entire conversation
        self.__previous_sentiment_score = 0  # Start with a neutral conversation sentiment
        self.__decay_factor = 0.65  # Exponential decay factor for previous sentiment


    # ---- HELPER FUNCTIONS ----

    # A function to calculate the sentiment of a message
    def evaluate_sentiment(self, message):
        message = self.__clean_message(message)

        sentiment_score = 0
        # Base case: if no conjunctions are present, calculate sentiment directly
        if not any(conjunction in message for conjunction in self.__conjunctions):
            sentiment_score = self.__compute_sentiment(message)
            return sentiment_score

        # If conjunctions are present, split the message and evaluate each part
        sentences = self.__handle_conjunctions(message)
        for sentence in sentences:
            sentiment_score = self.__compute_sentiment(sentence)
            print(sentence, sentiment_score)

        return sentiment_score

    # A function to calculate the sentiment of a sentence
    def __compute_sentiment(self, sentence):
        words = sentence.split()

        # Count positive and negative words in the message
        positive_count = sum(1 for word in words if word in self.__positive_words)
        negative_count = sum(1 for word in words if word in self.__negative_words)

        # Count negations in the message
        negation_count = sum(1 for word in words if word in self.__negations)

        # Apply quantifiers and diminishers
        quantifier_multiplier = 1
        diminisher_multiplier = 1
        previous_word = None

        for word in words:
            if word in self.__quantifiers:
                if previous_word in self.__negations:
                    quantifier_value = self.__quantifiers[word]
                    # Subtract the excess over 1 for quantifiers
                    quantifier_multiplier *= (1 - (quantifier_value - 1))
                else:
                    quantifier_multiplier *= self.__quantifiers[word]

            if word in self.__diminishers:
                if previous_word in self.__negations:
                    diminisher_value = self.__diminishers[word]
                    # Add the deficit to 1 for diminishers
                    diminisher_multiplier *= (1 + (1 - diminisher_value))
                else:
                    diminisher_multiplier *= self.__diminishers[word]

            previous_word = word

        # Base sentiment calculation
        base_sentiment = positive_count - negative_count
        if base_sentiment == 0:
            base_sentiment = quantifier_multiplier - diminisher_multiplier

        # Adjust sentiment based on negations
        negation_adjustment = self.__adjust_for_negations(base_sentiment, negation_count)

        # Final sentiment score calculation
        sentiment_score = base_sentiment * negation_adjustment * quantifier_multiplier * diminisher_multiplier
        return 0.745 * atan(sentiment_score)

    # A function to account for the negations in the sentence
    @staticmethod
    def __adjust_for_negations(base_sentiment, negation_count):
        if base_sentiment > 0 and negation_count % 2 == 1:
            return -1
        elif base_sentiment < 0 and negation_count % 2 == 1:
            return 0
        else:
            return 1

    # A function to split the sentence into conjunctions
    def __handle_conjunctions(self, sentence):
        words = sentence.split()
        conjunction_indices = [0]  # List to store indices of conjunctions

        for i, word in enumerate(words):
            if word in self.__conjunctions:
                conjunction_indices.append(i + 1)  # Append index after the conjunction

        conjunction_indices.append(len(words))  # Append the final index (end of sentence)

        # Return the sentence parts based on conjunctions
        return [" ".join(words[conjunction_indices[i]:conjunction_indices[i + 1]])
                for i in range(len(conjunction_indices) - 1)]

    # A function to clean the message and remove unecessary characters
    @staticmethod
    def __clean_message(message):
        # Convert the message to lowercase
        message = message.lower()

        # Handle contractions and prevent misinterpretation
        contractions = {
            "wasn't": "wasnt", "can't": "cant", "don't": "dont",
            "didn't": "didnt", "isn't": "isnt", "won't": "wont",
            "haven't": "havent", "shouldn't": "shouldnt",
            "wouldn't": "wouldnt", "couldn't": "couldnt",
            "you're": "youre", "i'm": "im", "he's": "hes",
            "she's": "shes", "it's": "its", "they're": "theyre"
        }

        for contraction, replacement in contractions.items():
            message = message.replace(contraction, replacement)

        # Remove unwanted punctuation (except for spaces between words)
        message = ''.join([char for char in message if char not in ["'"]])

        # Remove extra spaces
        message = ' '.join(message.split())

        # Handle multi-word quantifiers/diminishers phrases
        message = message.replace("a little", "a-little")
        message = message.replace("a lot", "a-lot")
        message = message.replace("kind of", "kind-of")
        message = message.replace("a bit", "a-bit")
        message = message.replace("sort of", "sort-of")
        message = message.replace("not really", "not-really")

        # Handle multi-word conjunctions
        message = message.replace("in case", "in-case")
        message = message.replace("provided that", "provided-that")
        message = message.replace("even though", "even-though")
        message = message.replace("so that", "so-that")
        message = message.replace("due to", "due-to")

        return message

    # A function to load all the words from a given file
    @staticmethod
    def __load_words_from_file(file_path):
        if file_path.endswith('.txt'):
            with open(file_path, 'r') as file:
                words = [line.strip() for line in file.readlines()]
            return words
        else:
            return []

    def __log_analysis_details(self):
        pass
