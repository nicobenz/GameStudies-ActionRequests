import os
import numpy as np
import spacy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity


def get_topics(
        ngram_fraction, ngram_steps, num_topics, topic_len,
        vectorizer_type="tfidf", limit_ngrams=0, limit_games=0, verbose=True):
    # get filenames from directory
    clean_texts = [file for file in os.listdir("data/transcripts/clean") if ".DS_Store" not in file]
    clean_texts.sort()
    if limit_games > 0:
        clean_texts = clean_texts[0:limit_games]  # select only some texts for testing purposes

    if vectorizer_type == "tfidf":
        vectorizer = TfidfVectorizer()
    elif vectorizer_type == "count":
        vectorizer = CountVectorizer()
    else:
        raise ValueError("Vectorizer not recognised. Viable options are 'count' or 'tfidf'.")

    document_topics = []
    for text_idx, text in enumerate(clean_texts, start=1):
        # open texts
        with open(f"data/transcripts/clean/{text}", "r") as f:
            filtered_tokens = f.read()
        # make text to list
        filtered_tokens = filtered_tokens.split(" ")
        # set length of ngrams
        ngram_length = len(filtered_tokens)//ngram_fraction
        step = 0  # this is used for ngram movement later
        # lists for collection
        topics_in_text = []
        # move ngrams through text
        loop_length = len(filtered_tokens)
        if limit_ngrams > 0:
            loop_length = (ngram_length + limit_ngrams) - 1
        num_iterations = (loop_length - ngram_length) + 1  # for status print during loop
        #loop_length = ngram_length + 9  # reduce amount of ngrams for testing purpose
        while step + ngram_length <= loop_length:
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
            if verbose:
                print(f"\rGame {text_idx:03d}/{len(clean_texts):03d} | ngram {step:03d}/{num_iterations:03d}", end="")
        document_topics.append(topics_in_text)
    print("\n")
    topic_collection = [["" for i in range(num_topics)] for j in range(len(document_topics[0]))]
    #print("games ", len(document_topics))
    #print("ngrams", len(document_topics[0]))
    for game in document_topics:
        for idx, ngram in enumerate(game):
            for jdx, top in enumerate(ngram):
                topic_collection[idx][jdx] += (' '.join(top["topics"]) + " ")

    mean_topics = []
    for ngram_level in topic_collection:
        topics_per_ngram = []
        for topic_level in ngram_level:
            ngram_mean = get_topic_from_text(vectorizer, topic_level, 1, topic_len)
            topics_per_ngram.append(ngram_mean)
        mean_topics.append(topics_per_ngram)
    return mean_topics


def get_topic_from_text(model, input_text, num_topics, topic_len):
    input_text = input_text.split(" ")
    input_text = [t for t in input_text if t != ""]  # remove empty strings

    X = model.fit_transform(input_text)
    lda_model = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda_model.fit(X)

    feature_names = model.get_feature_names_out()
    topics_in_mean_ngram = []
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
        topics_in_mean_ngram.append(topic_dict)
    return topics_in_mean_ngram


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


topics_over_ngrams = get_topics(5, 1, 3, 20,
                    vectorizer_type="count", limit_ngrams=1, limit_games=10)
for idx, topics in enumerate(topics_over_ngrams, start=1):
    print(f"{idx:03d}:")
    for jdx, top in enumerate(topics, start=1):
        print(f"  {jdx:03d}, weight {round(sum(top[0]['weights']), 2)}, tokens: {', '.join(top[0]['topics'])}")
#track_topics(topics)
