import re
from SentimentAnalysis.Exceptions.errors import *


class SentimentAnalyzerModel:
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

    def __init__(self, model, wordset="standard", positive_words_file=None,
                 negative_words_file=None):
        """
        Initializes the SentimentAnalyzer with lists of positive and negative words.
        """

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

        self.positive_words = self.__load_words_from_file(positive_words_path)
        self.negative_words = self.__load_words_from_file(negative_words_path)

        self.model = model


    def evaluate_sentiment(self, message, verbose=False):
        """
        Evaluates the sentiment of the given message.
        """
        pass

    def detect_sarcasm(self, message, verbose=False):
        """
        Attempts to detect sarcasm in a given message
        """
        if self.model == "1.0":
            raise ModelNotSupportedError(self.model, "Sarcasm Detection")
        pass

    def detect_emotions(self, message, verbose=False):
        """
        Attempts to detect all the emotions in a given message
        """
        if self.model == "1.0":
            raise ModelNotSupportedError(self.model, "Emotion Detection")
        pass

    # ---- HELPER FUNCTIONS ----

    @staticmethod
    def split_sentences(text):
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

    @staticmethod
    def clean_message(message):
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
