import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


def get_keywords(
        ngram_fraction, num_ngrams, limit_ngrams=0, limit_games=0, verbose=True):
    # get filenames from directory
    clean_texts = [file for file in os.listdir("data/transcripts/clean") if ".DS_Store" not in file]
    clean_texts.sort()
    if limit_games > 0:
        clean_texts = clean_texts[0:limit_games]  # select only some texts for testing purposes

    ngrams_collector = ["" for _ in range(num_ngrams)]
    for text_idx, text in enumerate(clean_texts, start=1):
        # open texts
        with open(f"data/transcripts/clean/{text}", "r") as f:
            filtered_tokens = f.read()
        # make text to list
        filtered_tokens = filtered_tokens.split(" ")
        # set length of ngrams
        ngram_len, initial_step, step_size = calculate_ngram_step(len(filtered_tokens), ngram_fraction, num_ngrams)
        # lists for collection
        if limit_ngrams > 0:
            num_ngrams = limit_ngrams
        # move ngrams through text
        for i in range(num_ngrams):
            # first step is bigger because the modulo rest of the ngram steps gets added here
            if i == 0:
                start = 0
                end = ngram_len + initial_step
            else:
                start = initial_step + (i * step_size)
                end = start + ngram_len
            current_ngram = filtered_tokens[start:end]
            ngrams_collector[i] += (' '.join(current_ngram) + " ")
            # print progress if needed
            if verbose:
                print(f"\rGame {text_idx:03d}/{len(clean_texts):03d} | ngram {i+1:03d}/{num_ngrams:03d}", end="")
    if verbose:
        print("\n")

    return ngrams_collector


def calculate_ngram_step(text_length, ngram_fraction, num_steps):
    # calculate the optimal step length between ngrams
    ngram_length = text_length // ngram_fraction
    moveable_space = text_length - ngram_length
    step = moveable_space // (num_steps - 1)
    ngram_start = moveable_space % (num_steps - 1)
    return ngram_length, ngram_start, step


def get_frequency_scores_from_ngrams(ngram_texts, num_lines, mode="count"):
    if mode == "count":
        vectorizer = CountVectorizer()
    elif mode == "tfidf":
        vectorizer = TfidfVectorizer()
    else:
        raise ValueError("Wrong mode. Please use 'count' for TF or 'tfidf' for TF-IDF vectorizer.")
    term_matrix = vectorizer.fit_transform(ngram_texts)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = term_matrix.toarray()

    score_collection = [[] for _ in range(num_lines)]

    for tfidf in tfidf_scores:
        sorted_ngram_scores = sorted(zip(feature_names, tfidf), key=lambda x: x[1], reverse=True)
        for idx, verb in enumerate(action_verbs):
            for score in sorted_ngram_scores:
                if score[0] == verb:
                    score_collection[idx].append(score[1])
    return score_collection


def plot_keyword_relevance(freq_scores):
    sns.set_theme()
    sns.set_context("paper")
    custom_palette = sns.color_palette("pastel")
    sns.set_palette(custom_palette)

    for idx, sublist in enumerate(freq_scores):
        print(sublist)
        sublist = np.array(sublist, dtype=float)
        x = np.arange(len(sublist))
        plt.plot(x, sublist, marker='', linestyle='-', linewidth=2, markersize=5, color=custom_palette[idx])

    plt.xlabel("N-Gram Index")
    plt.ylabel("TF-IDF Scores")

    plt.legend(title="Verbs", labels=action_verbs, loc="upper left")

    plt.tight_layout()

    plt.savefig("data/results/plots/lineplot.pdf")


# specify verbs (or tokens) to
action_verbs = ["kill", "fight", "help", "talk", "bring"]

ngrams = get_keywords(10, 100, limit_ngrams=0, limit_games=0, verbose=False)
scores = get_frequency_scores_from_ngrams(ngrams, len(action_verbs), mode="count")
plot_keyword_relevance(scores)
