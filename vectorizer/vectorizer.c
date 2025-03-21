#include "vectorizer.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// A function to create a SentimentVector
struct SentimentVector* create(int magnitude, int polarity, double intensity) {
    struct SentimentVector* v = (struct SentimentVector*)malloc(sizeof(struct SentimentVector));
    if (v == NULL) {
        return NULL;
    }

    v->magnitude = magnitude;
    v->polarity = polarity;
    v->intensity = intensity;

    return v;
}

// A function to convert a scalar to sentiment vector
struct SentimentVector* s2v(int bs, int neg, double mult) {
    return create(bs, neg, mult);
}

// A function to convert a sentiment vector to scalar
double v2s(struct SentimentVector* v) {
    double base_sentiment;

    // Adjust for base-sentiment
    if (v->magnitude == 0 && v->intensity != 1) {
        base_sentiment = fabs(1 - v->intensity);
    } else {
        base_sentiment = v->magnitude;
    }

    // Calculate score
    double score = base_sentiment * v->polarity * v->intensity;
    return atan(score) * 0.691;
}


// A function to combine 2 sentiment vectors
struct SentimentVector* combine(struct SentimentVector* v1, struct SentimentVector* v2) {
    int new_magnitude;
    int new_polarity;
    double new_intensity;

    // Compute effective strengths
    double strength_v1 = compute_effective_strength(v1);
    double strength_v2 = compute_effective_strength(v2);

    // Combine polarities
    if (v1->polarity * v2->polarity == 1) {
        // Both polarities are the same
        new_polarity = v1->polarity;
    } else if (v1->polarity * v2->polarity == -1) {
        // Polarities are different
        if (strength_v1 == strength_v2) {
            // If effective strengths are equal, set polarity to neutral
            new_polarity = 0;
        } else {
            // Use the polarity of the sentiment with the higher effective strength
            new_polarity = (strength_v1 > strength_v2) ? v1->polarity : v2->polarity;
        }
    } else if (v1->polarity == 0 && v2->polarity != 0) {
        // One polarity is neutral, use the non-neutral one
        new_polarity = v2->polarity;
    } else if (v1->polarity != 0 && v2->polarity == 0) {
        // One polarity is neutral, use the non-neutral one
        new_polarity = v1->polarity;
    } else {
        // Both polarities are neutral
        new_polarity = 0;
    }

    // Combine magnitudes
    if (v1->polarity * v2->polarity == 1) {
        // Both polarities are the same, add magnitudes
        new_magnitude = v1->magnitude + v2->magnitude;
    } else if (v1->polarity * v2->polarity == -1) {
        // Polarities are different, subtract magnitudes
        new_magnitude = abs(v1->magnitude - v2->magnitude);
    } else {
        // One or both polarities are neutral
        new_magnitude = v1->magnitude + v2->magnitude;
    }

    // Combine intensities
    if (v1->intensity >= 1 && v2->intensity >= 1) {
        // Both are quantifiers, use the maximum intensity
        new_intensity = fmax(v1->intensity, v2->intensity);
    } else if (v1->intensity <= 1 && v2->intensity <= 1) {
        // Both are diminishers, use the minimum intensity
        new_intensity = fmin(v1->intensity, v2->intensity);
    } else {
        // One is a quantifier, the other is a diminisher
        double effective_intensity_v1 = (v1->intensity >= 1) ? (v1->intensity - 1) : (1 - v1->intensity);
        double effective_intensity_v2 = (v2->intensity >= 1) ? (v2->intensity - 1) : (1 - v2->intensity);

        // Use the intensity with the higher effective intensity
        new_intensity = (effective_intensity_v1 > effective_intensity_v2) ? v1->intensity : v2->intensity;
    }

    // Create and return the combined SentimentVector
    return create(new_magnitude, new_polarity, new_intensity);
}

// Function to compute effective strength (magnitude × effective intensity)
double compute_effective_strength(struct SentimentVector* v) {
    double effective_intensity = (v->intensity >= 1) ? (v->intensity - 1) : (1 - v->intensity);
    return v->magnitude * effective_intensity;
}

// A function to print details about Sentiment Vector
void toString(struct SentimentVector* v) {
    printf("SentimentVector: [magnitude: %d, polarity: %d, intensity: %.4f]\n", v->magnitude, v->polarity, v->intensity);
}


int main() {
    // Example usage
    // struct SentimentVector* v1 = create(3, 1, 1.2);
    // struct SentimentVector* v2 = create(3, -1, 1.5);

    // Combine the vectors
    // struct SentimentVector* final = combine(v1, v2);
    // toString(final);

    // Calculate scores
    // double score = v2s(final);
    // double s1_score = v2s(v1);
    // double s2_score = v2s(v2);

    // printf("Final score is: %.4f\n", score);
    // printf("v1 score is: %.4f\n", s1_score);
    // printf("v2 score is: %.4f\n", s2_score);

    // Free memory
    // free(v1);
    // free(v2);
    // free(final);

    return 0;
}