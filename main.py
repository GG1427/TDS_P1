import json
import requests

def compute_similarity(vectors: list[list[float]]):
    with open("master_course.json", "r", encoding="UTF-8") as f:
        contents = json.load(f)
    
    counter = 0

    master = []

    for vector in vectors:
        for dict in contents["data"]:
            vectors = dict["vectors"]
            scores = []
            for v in vectors:
                similarity = cosine_similarity(v, vector)
                scores.append(similarity)
            master.append((counter, max(scores)))
            counter += 1

            #print(f"Processed {counter} entries in master_course.json, out of {len(contents['data'])}")

    #print("master_course.json processed")

    with open("master_discourse.json", "r", encoding="UTF-8") as f:
        contents2 = json.load(f)

    counter2 = 0

    master2 = []

    for vector in vectors:
        for dict in contents2["data"]:
            vectors = dict["vectors"]
            scores = []
            for v in vectors:
                similarity = cosine_similarity(v, vector)
                scores.append(similarity)
            master2.append((counter2, max(scores)))
            counter2 += 1

            #print(f"Processed {counter2} entries in master_discourse.json, out of {len(contents2['data'])}")

    #print("master_discourse.json processed")

    master.sort(key=lambda x: x[1], reverse=True)
    master2.sort(key=lambda x: x[1], reverse=True)

    master_text_and_url = [{"text": contents["data"][i[0]]["text"], "url": contents["data"][i[0]]["url"]} for i in master]
    master2_text_and_url = [{"text": contents2["data"][i[0]]["text"], "url": contents2["data"][i[0]]["url"]} for i in master2]

    return master_text_and_url[:2] + master2_text_and_url[:2]


def cosine_similarity(vec1, vec2):
    # Compute dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    # Compute magnitudes
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5
    # Avoid division by zero
    if mag1 == 0 or mag2 == 0:
        return 0
    return dot_product / (mag1 * mag2)


def context():
    with open("query_vector.json", "r", encoding="UTF-8") as f:
        input_data = json.load(f)

    results = compute_similarity([input_data["vector"]])

    print("Top 5 results:")
    for i, result in enumerate(results, start=1):
        print(f"{i}: {result[0:100]}")


def fresh_prompt(question, li):

    results = compute_similarity(li)

    context = ""
    for result in enumerate(results, start=1):
        context += result["text"]
    
    AIPIPE_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE4MjRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.6sV4a8Mz_C3YcDH6AbamRY6crXiY6XHT7Zidb7z7zBA"

    headers = {
            "Authorization": f"{AIPIPE_TOKEN}",
            "Content-Type": "application/json"
    }

    with open("response_template.json", "r", encoding="UTF-8") as f:
        output = json.load(f)

    output["messages"][0]["content"] += context
    output["messages"][1]["content"] = question

    response = requests.post("https://aipipe.org/openai/v1/responses", headers=headers, json=output)

    answer = response.json()["choices"][0]["message"]["content"]

    if "I don't know" in answer:
        ret = {"answer" : answer}
    else:
        ret = {"answer" : answer, "links": results}

    return ret