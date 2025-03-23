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
    return atan(score) * 0.636;
}


// A function to combine 2 sentiment vectors
struct SentimentVector* combine(struct SentimentVector* v1, struct SentimentVector* v2) {
    if (!v1 || !v2) return NULL; // Safety check

    int new_magnitude;
    int new_polarity;
    double new_intensity;

    // Calculate effective intensities
    double eff_intensity1 = compute_effective_intensity(v1);
    double eff_intensity2 = compute_effective_intensity(v2);

    new_intensity = (eff_intensity1 > eff_intensity2) ? v1->intensity : v2->intensity;

    // Case 1: Same polarity
    if (v1->polarity * v2->polarity == 1) {
        new_magnitude = v1->magnitude + v2->magnitude;
        new_polarity = v1->polarity; // Same as input polarities
    }
    // Case 2: Opposite polarity
    else if (v1->polarity * v2->polarity == -1) {
        // Calculate the net magnitude
        new_magnitude = abs(v1->magnitude) + abs(v2->magnitude);

        // Determine the resulting polarity
        if (v1->magnitude * v2->magnitude > 0) {
            new_polarity = 1; // Positive
        } else if (v1->magnitude * v2->magnitude < 0) {
            new_polarity = -1; // Negative
        } else {
            new_polarity = (eff_intensity1 > eff_intensity2) ? v1->polarity : v2->polarity;
        }
    }
    // Case 3: One or both polarities are zero
    else {
        // Combine magnitudes (considering their signs and polarities)
        new_magnitude = v1->magnitude + v2->magnitude;

        // Determine the resulting polarity based on the net magnitude
        if (new_magnitude >= 0) {
            new_polarity = 1; // Positive
        } else if (new_magnitude < 0) {
            new_polarity = -1; // Negative
        }

        // Take the absolute value of the net magnitude
        new_magnitude = abs(new_magnitude);
    }

    return create(new_magnitude, new_polarity, new_intensity);
}

// Function to compute effective strength (magnitude × effective intensity)
double compute_effective_intensity(struct SentimentVector* v) {
    double effective_intensity = (v->intensity >= 1) ? (v->intensity - 1) : (1 - v->intensity);
    return effective_intensity;
}

// A function to print details about Sentiment Vector
char* toString(struct SentimentVector* v) {
    static char result[100];

    snprintf(result, sizeof(result), "SentimentVector: [magnitude: %d, polarity: %d, intensity: %.4f]\n", v->magnitude, v->polarity, v->intensity);

    return result;
}
