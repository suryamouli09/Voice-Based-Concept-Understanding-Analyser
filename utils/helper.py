import json


def load_reference_concepts():

    with open("models/reference_concepts.json", "r") as file:
        concepts = json.load(file)

    return concepts