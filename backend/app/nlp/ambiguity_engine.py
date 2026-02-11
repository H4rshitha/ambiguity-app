import string
from collections import defaultdict
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from app.nlp.embedding_fallback import embedding_fallback


lemmatizer = WordNetLemmatizer()

# Expanded POS tag mapping to WordNet

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):  # Adjective
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):  # Verb
        return wordnet.VERB
    elif treebank_tag.startswith('N'):  # Noun
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):  # Adverb
        return wordnet.ADV
    elif treebank_tag in ('MD',):  # Modal verb
        return wordnet.VERB
    elif treebank_tag in ('RP',):  # Particle
        return wordnet.ADV
    elif treebank_tag in ('EX', 'DT', 'PDT', 'WDT'):  # Determiners (default to noun)
        return wordnet.NOUN
    elif treebank_tag in ('PRP', 'PRP$', 'WP', 'WP$'):  # Pronouns (ignore in analysis)
        return None
    else:
        return None

# Expanded stopwords list with important exceptions
STOPWORDS = set([
    'the', 'is', 'and', 'a', 'an', 'to', 'of', 'in', 'that', 'on', 'for',
    'with', 'as', 'by', 'was', 'were', 'it', 'he', 'she', 'they', 'we',
    'this', 'his', 'her', 'from', 'at', 'or', 'not', 'but', 'be', 'been',
    'are', 'you', 'i', 'me', 'my', 'your', 'their', 'our', 'them', 'us',
    'do', 'does', 'did', 'doing', 'so', 'if', 'because', 'while', 'up', 'down',
    'out', 'about', 'into', 'over', 'after', 'again', 'further', 'then', 'once'
])

IMPORTANT_STOPWORDS = {'can', 'not', 'will', 'must', 'should', 'may', 'might', 'shall', 'could', 'would'}

MODAL_VERB_DEFINITIONS = {
    'can': "Used to express ability or possibility.",
    'could': "Used to express conditional possibility or past ability.",
    'may': "Used to express permission or possibility.",
    'might': "Used to express a lower probability.",
    'must': "Used to express necessity or strong obligation.",
    'shall': "Used to express future intention or obligation.",
    'should': "Used to express advisability or expectation.",
    'will': "Used to express future actions or willingness.",
    'would': "Used to express habitual past actions or polite requests."
}

# Tokenize, POS-tag, and lemmatize text

def tokenize_and_lemmatize(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    lemmatized = []
    for word, tag in tagged:
        wn_pos = get_wordnet_pos(tag)
        if wn_pos is None:
            lemmatized.append(word.lower())
        else:
            lemmatized.append(lemmatizer.lemmatize(word.lower(), wn_pos))
    return lemmatized

# Helper function: determine if stopword is contextually useful

def is_important_stopword(word, text):
    tokens = tokenize_and_lemmatize(text)
    for sense in wordnet.synsets(word):
        def_tokens = tokenize_and_lemmatize(sense.definition())
        if any(token in tokens for token in def_tokens):
            return True
    return False

# Extract keywords using basic frequency counting

def extract_keywords(text, top_n=10):
    lemmatized_tokens = tokenize_and_lemmatize(text)
    words = [
        word for word in lemmatized_tokens
        if ((word not in STOPWORDS or word in IMPORTANT_STOPWORDS or is_important_stopword(word, text))
            and word.isalpha())
    ]
    freq = defaultdict(int)
    for word in words:
        freq[word] += 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_words for _ in range(count)][:top_n]

# Find ambiguous words (words with multiple senses in WordNet)

def get_ambiguous_words(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    ambiguous = []
    for i, (word, tag) in enumerate(tagged):
        wn_pos = get_wordnet_pos(tag)
        if wn_pos is None:
            continue
        lemma = lemmatizer.lemmatize(word.lower(), wn_pos)
        key = (word.lower(), lemma, i)  # track position as well

        senses = wordnet.synsets(lemma, pos=wn_pos)

        if not senses and tag == 'MD' and lemma in MODAL_VERB_DEFINITIONS:
            class FakeSense:
                def __init__(self, lemma):
                    self._lemma = lemma
                def definition(self):
                    return MODAL_VERB_DEFINITIONS.get(self._lemma, "No definition available.")
                def examples(self):
                    return [f"He {self._lemma} do it."]
                def lemmas(self):
                    class Lemma:
                        def name(inner_self): return self._lemma
                        def antonyms(inner_self): return []
                    return [Lemma()]
            senses = [FakeSense(lemma)]

        if len(senses) > 1 or (tag == 'MD' and lemma in MODAL_VERB_DEFINITIONS):
            ambiguous.append(((word.lower(), lemma, i), senses))
    return ambiguous

# Try to guess the sense based on keyword overlap, synonyms, antonyms

def guess_sense(word, senses, context_keywords):
    scores = []
    extended_context = defaultdict(set)
    for kw in context_keywords:
        kw_senses = wordnet.synsets(kw)
        for s in kw_senses:
            extended_context[kw].update(tokenize_and_lemmatize(s.definition()))
            for ex in s.examples():
                extended_context[kw].update(tokenize_and_lemmatize(ex))
            for lemma in s.lemmas():
                extended_context[kw].add(lemma.name().lower())
                for ant in lemma.antonyms():
                    extended_context[kw].add(ant.name().lower())

    for sense in senses:
        if hasattr(sense, 'definition'):
            gloss = sense.definition() + " " + " ".join(sense.examples())
        else:
            gloss = ""
        if hasattr(sense, 'lemmas'):
            for lemma in sense.lemmas():
                if hasattr(lemma, 'synset'):
                    try:
                        gloss += " " + " ".join(lemma.synset().examples())
                    except Exception:
                        pass

        gloss_tokens = tokenize_and_lemmatize(gloss)

        synonyms = set()
        antonyms = set()
        if hasattr(sense, 'lemmas'):
            for lemma in sense.lemmas():
                synonyms.add(lemma.name().lower())
                for ant in lemma.antonyms():
                    antonyms.add(ant.name().lower())

        score = 0
        for kw, context_set in extended_context.items():
            for context_word in context_set:
                if context_word in gloss_tokens:
                    score += 1.5
                if context_word in synonyms:
                    score += 0.5
                if context_word in antonyms:
                    score -= 0.5

        for kw in context_keywords:
            if kw in gloss_tokens:
                score += 2
            if kw in synonyms:
                score += 1
            if kw in antonyms:
                score -= 1

        scores.append((sense, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    top_score = scores[0][1] if scores else 0
    confidence = "Low"
    if top_score >= 4:
        confidence = "High"
    elif top_score >= 2:
        confidence = "Medium"

    if not scores or all(s[1] <= 1 for s in scores):
        return None, "None of the above meanings"

    return scores[0][0], confidence

# Single analysis function (returns results)

def analyze_text(text):
    result = {}
    context_keywords = extract_keywords(text)
    result['text'] = text
    result['context_keywords'] = context_keywords
    result['ambiguous'] = []

    ambiguous_words = get_ambiguous_words(text)
    for (word, lemma, index), senses in ambiguous_words:
        entry = {
            'word': word,
            'index': index,
            'senses': []
        }
        for sense in senses[:3]:
            try:
                entry['senses'].append(sense.definition())
            except Exception:
                continue

        best_sense, confidence = guess_sense(word, senses, context_keywords)
        decision_source = "wordnet"
        # ---- Transformer Fallback ----
        if best_sense is None or confidence in ["Low", "Medium"]:
            fallback_sense, sim_score = embedding_fallback(text, senses)

            if fallback_sense is not None:
                best_sense = fallback_sense
                confidence = "Transformer-Medium"
                decision_source = "transformer"
                entry['fallback_similarity'] = round(sim_score, 3)

        if best_sense:
            try:
                entry['best_sense'] = best_sense.definition()
            except Exception:
                entry['best_sense'] = "No definition found."
            entry['confidence'] = confidence
        else:
            entry['best_sense'] = "None of the above meanings"
            entry['confidence'] = confidence
        entry['decision_source'] = decision_source
        result['ambiguous'].append(entry)
    # ---- Sentence Ambiguity Score ----
    tokens = tokenize_and_lemmatize(text)

    meaningful_tokens = [
        t for t in tokens
        if t.isalpha() and t not in STOPWORDS
    ]

    total_meaningful = len(meaningful_tokens)
    ambiguous_count = len(result['ambiguous'])

    if total_meaningful == 0:
        ambiguity_score = 0
    else:
        ambiguity_score = round(ambiguous_count / total_meaningful, 2)

    result['ambiguity_score'] = ambiguity_score
    return result



