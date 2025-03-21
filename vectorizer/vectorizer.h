#ifndef VECTORIZER_H
#define VECTORIZER_H

#include <stdlib.h>
#include <math.h>

/**
 * A 3-Dimensional representation of a sentiment.
 *
 * The SentimentVector struct encapsulates the three key components of a sentiment:
 * - Magnitude: Represents the strength or weight of the sentiment.
 * - Polarity: Indicates the direction of the sentiment (positive, negative, or neutral).
 * - Intensity: Represents the degree of emphasis applied to the sentiment.
 */
struct SentimentVector {
    int magnitude;
    int polarity;
    double intensity;
};

// A function to create a sentiment vector
struct SentimentVector* create(int magnitutde, int polarity, double intensity);

// A function to convert a scalar to sentiment vector
struct SentimentVector* s2v(int bs, int neg, double mult);

// A function to convert a sentiment vector to scalar 
double v2s(struct SentimentVector* v);

// A function to combine 2 sentiment vectors
struct SentimentVector* combine(struct SentimentVector* v1, struct SentimentVector* v2);

// A function to compute the effective strength
double compute_effective_strength(struct SentimentVector* v);

// A function to print details about Sentiment Vector
void toString(struct SentimentVector* v);

#endif