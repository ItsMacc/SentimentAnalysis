#include "vectorizer.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// A function to create a SentimentVector
struct SentimentVector* create(int magnitude, int polarity, double intensity){
    struct SentimentVector* v = (struct SentimentVector*) malloc(sizeof(struct SentimentVector));
    if (v == NULL){
        return NULL;
    }

    v->magnitude = magnitude;
    v->polarity = polarity;
    v->intensity = intensity;

    return v;
};

// A function to convert a scalar to sentiment vector
struct SentimentVector* s2v(int bs, int neg, double mult){
    return create(bs, neg, mult);
};

// A function to convert a sentiment vector to scalar 
double v2s(struct SentimentVector* v) {
    double base_sentiment;

    // Adjust for base-sentiment
    if (v->magnitude == 0) {
        base_sentiment = v->intensity;
    } else {
        base_sentiment = v->magnitude;
    }

    // Calculate score
    double score = base_sentiment * v->polarity * v->intensity;
    return atan(score) * 0.691;
};

//A function to combine 2 sentiment vectors
struct SentimentVector* combine(struct SentimentVector* v1, struct SentimentVector* v2) {
    int new_magnitutde;
    int new_polarity;
    double new_intensity;

    new_magnitutde = v1->magnitude + v2->magnitude;

    // Polarity adjustment
    if (v1->polarity * v2->polarity == 1) {
        new_polarity = v1->polarity;
    } else if(v1->polarity * v2->polarity == -1) {
        new_polarity = -1;
    } else if (v1->polarity == 0 && v2->polarity != 0) {
        new_polarity = v2->polarity;
    } else if (v1->polarity != 0 && v2->polarity == 0) {
        new_polarity = v1->polarity;
    } else {
        new_polarity = 0;
    }

    // Intensity adjustment
    if (v1->intensity >= 1 && v2->intensity >= 1) {
        new_intensity = fmax(v1->intensity, v2->intensity);
    } else if (v1->intensity <= 1 && v2->intensity <= 1) {
        new_intensity =  fmin(v1->intensity, v2->intensity);
    } else {
        double abs_intensity_v1 = fmax(v1->intensity, v2->intensity) - 1;
        double abs_intensity_v2 = fmin(v1->intensity, v2->intensity) - 1;

        new_intensity = abs_intensity_v1 + abs_intensity_v2;
    }

    // Final SentimentVector
    return create(new_magnitutde, new_polarity, new_intensity);
};

// A function to print details about Sentiment Vector
void toString(struct SentimentVector* v) {
    printf("SentimentVector: [magnitutde: %d, polarity: %d, intensity: %.4f]\n", v->magnitude, v->polarity, v->intensity);
};

int main(){
    // struct SentimentVector* v1 = create(1, -1, 1.2);
    // struct SentimentVector* v2 = create(-1, 1, 1);

    // struct SentimentVector* final = combine(v1, v2);
    // toString(final);

    // double score = v2s(final);
    // double s1_score = v2s(v1);
    // double s2_score = v2s(v2);

    // printf("final score is: %.4f\n", score);
    // printf("s1 score is: %.4f\n", s1_score);
    // printf("s2 score is: %.4f\n", s2_score);

    return 0;
};