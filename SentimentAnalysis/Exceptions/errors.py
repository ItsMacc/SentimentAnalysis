class InvalidWordsetError(Exception):
    """Raised when an invalid wordset is provided."""
    def __init__(self, wordset):
        self.wordset = wordset
        super().__init__(f"Invalid wordset: {wordset}. Choose from 'standard', 'extended', or 'custom'.")

class MissingCustomFilesError(Exception):
    """Raised when custom word files are not provided."""
    def __init__(self):
        super().__init__("Please provide file paths for custom positive and negative words.")

class InvalidModelError(Exception):
    """Raised when an invalid model version is provided."""
    def __init__(self, model):
        self.model = model
        self.__models = ["1.0", "2.0", "3.0"]
        super().__init__(f"Invalid model: {model}. Choose from {self.__models}")

class ModelNotSupportedError(Exception):
    """
    Raised when the requested functionality is not supported in the current model.
    Suggests upgrading to a higher model version (e.g., "2.0+").
    """
    def __init__(self, current_model, functionality=None):
        self._models = ["1.0", "2.0", "3.0"]
        self.current_model = current_model
        self.functionality = functionality

        # Construct the error message
        message = (
            f"The current model ({current_model}) does not support "
            f"the requested functionality: {functionality or 'unknown'}. "
            f"Please upgrade your model to {self._models[1:]}."
        )

        super().__init__(message)