#ifndef VECTORIZER_H
#define VECTORIZER_H

#include <stdlib.h>
#include <math.h>

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

//A function to combine 2 sentiment vectors
struct SentimentVector* combine(struct SentimentVector* v1, struct SentimentVector* v2);

// A function to print details about Sentiment Vector
void toString(struct SentimentVector* v);

#endif