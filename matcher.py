from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(resume_text, job_description):
    """
    Calculate similarity between resume and job description
    using TF-IDF and cosine similarity.
    """

    # Make sure both inputs contain text
    if not resume_text.strip() or not job_description.strip():
        return 0.0

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    # Convert resume and job description into TF-IDF vectors
    tfidf_matrix = vectorizer.fit_transform(
        [
            resume_text,
            job_description
        ]
    )

    # Calculate cosine similarity
    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    # Convert to percentage
    similarity_percentage = round(
        similarity * 100,
        2
    )

    return similarity_percentage