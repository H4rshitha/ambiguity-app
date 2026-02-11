from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def embedding_fallback(context_text, senses):
    context_embedding = model.encode(context_text, convert_to_tensor=True)

    best_sense = None
    best_score = -1

    for sense in senses:
        try:
            definition = sense.definition()
        except:
            continue

        sense_embedding = model.encode(definition, convert_to_tensor=True)
        similarity = util.cos_sim(context_embedding, sense_embedding).item()

        if similarity > best_score:
            best_score = similarity
            best_sense = sense

    return best_sense, best_score
