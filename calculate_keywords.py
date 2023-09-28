import os
import json
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import statsmodels.api as sm
from tqdm import tqdm


def get_keywords(
        ngram_fraction, num_ngrams, limit_ngrams=0, limit_games=0, verbose=True):
    # get filenames from directory
    clean_texts = [file for file in os.listdir("data/transcripts/clean") if ".DS_Store" not in file]
    clean_texts.sort()
    if limit_games > 0:
        clean_texts = clean_texts[0:limit_games]  # select only some texts for testing purposes

    with open("data/genre_mapping.json", "r") as f:
        mapping = json.loads(f.read())
    genres = set(mapping.values())
    texts_by_genre = {genre: [] for genre in genres}
    for text in clean_texts:
        text_genre = mapping[text]
        texts_by_genre[text_genre].append(text)
    texts_by_genre["All Genres"] = clean_texts

    collected_texts = {}
    lengths = []
    for label, games in texts_by_genre.items():
        if len(games) < 6:
            pass
        else:
            collected_texts[label] = calculate_ngrams(games, num_ngrams, limit_ngrams, ngram_fraction, verbose)
            lengths.append(len(games))
            if verbose:
                print("\n")

    return collected_texts, lengths


def calculate_ngrams(texts, num_ngrams, limit_ngrams, ngram_fraction, verbose=True):
    ngrams_collector = ["" for _ in range(num_ngrams)]
    for text_idx, text in enumerate(texts, start=1):
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
                print(f"\rGame {text_idx:03d}/{len(texts):03d} | ngram {i + 1:03d}/{num_ngrams:03d}", end="")
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


def plot_keyword_relevance(freq_scores, numbers, save_label="", smoothing="avg", normalise=True):
    sns.set_theme()
    sns.set_context("paper")
    custom_palette = sns.color_palette("pastel")
    sns.set_palette(custom_palette)

    if normalise:
        freq_scores = normalize_scores(freq_scores)

    for idx, sublist in enumerate(freq_scores):
        sublist = np.array(sublist, dtype=float)
        x = np.arange(len(sublist))

        if smoothing == "avg":
            smoothed_sublist = moving_average(sublist, window_size=5)
        elif smoothing == "low":
            smoothed_sublist = lowess_smoothing(sublist, frac=0.2)
        else:
            raise ValueError("Wrong smoothing mode. Please use 'avg' for Moving Average or 'low' for Lowess Smoothing.")

        plt.plot(x[:len(smoothed_sublist)], smoothed_sublist, marker='', linestyle='-', linewidth=2, markersize=5,
                 color=custom_palette[idx])

    plt.title(f"Keyword Development for {save_label} (n={numbers})")
    plt.xlabel("N-Gram Index")
    plt.ylabel("Frequency Scores")

    plt.legend(title="Verbs", labels=action_verbs, loc="upper left")

    plt.tight_layout()

    plt.savefig(f"data/results/plots/lineplot-{'_'.join(save_label.split(' '))}.pdf")
    plt.savefig(f"data/results/plots/lineplot-{'_'.join(save_label.split(' '))}.png", dpi=600)
    plt.clf()


def normalize_scores(frequency_scores):
    normalized_scores = []
    for sublist in frequency_scores:
        sublist = np.array(sublist, dtype=float)
        min_val = np.min(sublist)
        max_val = np.max(sublist)
        scaled_sublist = (sublist - min_val) / (max_val - min_val)
        normalized_scores.append(scaled_sublist)
    return normalized_scores


def moving_average(data, window_size=3):
    weights = np.repeat(1.0, window_size) / window_size
    smoothed_data = np.convolve(data, weights, 'valid')
    return np.concatenate(([data[0]] * (window_size - 1), smoothed_data))


def lowess_smoothing(data, frac=0.3):
    # Apply Lowess smoothing to the data
    lowess = sm.nonparametric.lowess(data, np.arange(len(data)), frac=frac)
    return lowess[:, 1]


# specify verbs (or tokens) to
action_verbs = ["kill", "help", "talk", "find"]  # bring?

labeled_ngrams, num_texts = get_keywords(10, 200, limit_ngrams=0, limit_games=0, verbose=False)
for (labeling, ngrams), num in tqdm(zip(labeled_ngrams.items(), num_texts), total=len(labeled_ngrams)):
    scores = get_frequency_scores_from_ngrams(ngrams, len(action_verbs), mode="count")
    plot_keyword_relevance(scores, num, save_label=labeling, smoothing="low", normalise=True)
