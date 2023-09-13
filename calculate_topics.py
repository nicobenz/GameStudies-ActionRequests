import os
import numpy as np
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity


def get_topics(ngram_fraction, ngram_steps, num_topics, topic_len, vectorizer_type="tfidf"):
    # get filenames from directory
    clean_texts = [file for file in os.listdir("data/transcripts/clean") if ".DS_Store" not in file]
    clean_texts.sort()
    clean_texts = [clean_texts[3]]  # select only first text for testing purposes

    document_topics = []
    for text in clean_texts:
        # open texts
        with open(f"data/transcripts/clean/{text}", "r") as f:
            filtered_tokens = f.read()
        # make text to list
        filtered_tokens = filtered_tokens.split(" ")
        # set length of ngrams
        ngram_length = len(filtered_tokens)//ngram_fraction
        step = 0  # this is used for ngram movement later
        step = len(filtered_tokens) - (ngram_length+5)  # reduce to only a couple ngrams for testing purposes
        # prepare ngram for topic modelling
        if vectorizer_type == "tfidf":
            vectorizer = TfidfVectorizer()
        elif vectorizer_type == "count":
            vectorizer = CountVectorizer()
        else:
            raise ValueError("Vectorizer not recognised. Viable options are 'count' or 'tfidf'.")
        # lists for collection
        topics_in_text = []
        # move ngrams through text
        while step + ngram_length <= len(filtered_tokens):
            current_ngram = filtered_tokens[step:step+ngram_length]

            # fit model
            X = vectorizer.fit_transform(current_ngram)
            lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
            lda_model.fit(X)

            # get feature names and loop over
            feature_names = vectorizer.get_feature_names_out()
            topics_in_ngram = []
            for topic_idx, topic in enumerate(lda_model.components_):
                # get first {topic_len} tokens with highest probability
                top_indices = topic.argsort()[::-1][:topic_len]
                top_words = [feature_names[i] for i in top_indices]
                # calculate weights
                probabilities = (topic / topic.sum())[top_indices]
                token_weights = [probabilities[i] for i in range(len(top_words))]
                # combine to dict
                topic_dict = {
                    "topics": top_words,
                    "weights": token_weights
                }
                topics_in_ngram.append(topic_dict)
            topics_in_text.append(topics_in_ngram)
            # increment step for next ngram movement
            step += ngram_steps
        document_topics.append(topics_in_text)
    return document_topics


def track_topics(topic_list):
    # load spacy model for vectorisation
    nlp = spacy.load('en_core_web_md')
    mapped_topics = []
    # loop over every list of topic tokens and check all topics of next ngram for similarity (might switched position)
    for document in topic_list:
        for i in range(len(document)):
            for j in range(len(document[0])):
                cosine_sims = []
                for k in range(len(document[0])):
                    if i+1 < len(document):
                        current_document = document[i][j]["topics"]
                        current_weights = document[i][j]["weights"]

                        next_document = document[i+1][k]["topics"]
                        next_weights = document[i+1][k]["weights"]

                        vector_1 = get_vector(nlp, current_document, current_weights)
                        vector_2 = get_vector(nlp, next_document, next_weights)

                        cosine_sim = cosine_similarity(vector_1, vector_2)[0][0]
                        cosine_sim = round(float(cosine_sim), 3)
                        cosine_sims.append(cosine_sim)
                print(cosine_sims)
            print("---")


def get_vector(nlp_object, tokens, weights):
    vector_template = np.zeros(nlp_object.vocab.vectors.shape[1], dtype="float32")

    division_count = 0
    for token, weight in zip(tokens, weights):
        vector = nlp_object(token).vector
        if np.all(vector == 0):
            pass
        else:
            weighted_vector = vector * weight
            division_count += 1
            vector_template += weighted_vector

    if division_count > 0:
        vector_template /= division_count

    return vector_template.reshape(1, -1)


topics = get_topics(5, 1, 3, 20, vectorizer_type="count")

track_topics(topics)
