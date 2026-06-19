import json
import os
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_LABELS, DATA_PATH, TRAIN_FILE, LABELS_FILE

_client = Groq(api_key=GROQ_API_KEY)


def load_labeled_examples() -> list[dict]:
    """
    Load the training episodes and merge them with the student's labels.

    Returns a list of dicts, each with:
      - "id"          : episode ID
      - "title"       : episode title
      - "podcast"     : podcast name
      - "description" : episode description
      - "label"       : the label from my_labels.json (may be None if not yet annotated)

    Only returns episodes where the label is a valid, non-null string.
    Episodes with null labels are silently skipped.
    """
    train_path = os.path.join(DATA_PATH, TRAIN_FILE)
    labels_path = os.path.join(DATA_PATH, LABELS_FILE)

    with open(train_path, encoding="utf-8") as f:
        episodes = {ep["id"]: ep for ep in json.load(f)}

    with open(labels_path, encoding="utf-8") as f:
        labels = {entry["id"]: entry["label"] for entry in json.load(f)}

    labeled = []
    for ep_id, ep in episodes.items():
        label = labels.get(ep_id)
        if label in VALID_LABELS:
            labeled.append({**ep, "label": label})

    return labeled


def build_few_shot_prompt(labeled_examples: list[dict], description: str) -> str:
    """
    Build a few-shot classification prompt using the student's labeled training examples.

    TODO — Milestone 2:

    Your prompt needs to:
      1. Describe the task and the four valid labels
      2. Show the labeled training examples so the LLM can learn the pattern
      3. Present the new description and ask for a classification

    The LLM should return a single label from VALID_LABELS (exactly as written)
    plus a brief explanation of its reasoning. Think carefully about the output
    format you request — you'll need to parse it in classify_episode().

    Before writing code, complete specs/classifier-spec.md.
    """
    task_instruction = """You are classifying podcast episodes by their format. Classify the episode into exactly one of these four labels:

- interview: a conversation between a host and one or more guests
- solo: a single host speaking from memory, experience, or opinion — no guests, no assembled external sources
- panel: multiple guests with roughly equal speaking time, often debating or discussing a topic together
- narrative: a story assembled from external sources — interviews, archival audio, reporting — with a clear narrative arc

Return only the label and your reasoning. Do not explain the taxonomy."""

    # Build training examples section
    examples_section = ""
    if labeled_examples:
        examples_section = "\n\n--- TRAINING EXAMPLES ---\n"
        for example in labeled_examples:
            examples_section += f"\nTitle: {example['title']}\nDescription: {example['description']}\nLabel: {example['label']}\n"
            examples_section += "---"
    else:
        examples_section = "\n\n(No training examples provided; classify based on task instructions above.)\n"

    # Build the new episode section
    new_episode = f"\n\n--- EPISODE TO CLASSIFY ---\n\nTitle: [Unknown]\nDescription: {description}\nLabel: ?\n"

    # Build the output instruction
    output_instruction = "\nClassify the episode above. Return your answer in the format below:\n\nLabel: <label>\nReasoning: <brief explanation>"

    return task_instruction + examples_section + new_episode + output_instruction


def classify_episode(description: str, labeled_examples: list[dict]) -> dict:
    """
    Classify a single podcast episode description using the few-shot LLM classifier.

    TODO — Milestone 2 (complete after build_few_shot_prompt):

    Steps:
      1. Call build_few_shot_prompt() to construct the prompt
      2. Send it to the LLM via _client.chat.completions.create()
      3. Parse the response to extract a label and reasoning
      4. Validate the label — if it's not in VALID_LABELS, set it to "unknown"
      5. Return a dict with "label" and "reasoning" keys

    Handle the case where the LLM returns something unparseable gracefully —
    don't let a bad response crash the whole evaluation.

    Before writing code, complete specs/classifier-spec.md.
    """
    # Check for empty description
    if not description or not description.strip():
        return {"label": "unknown", "reasoning": "Description is empty"}

    try:
        # Step 1: Build the prompt
        prompt = build_few_shot_prompt(labeled_examples, description)

        # Step 2: Send to the LLM
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        raw_response = response.choices[0].message.content

        # Step 3: Parse the response
        lines = raw_response.split("\n")
        label_line = next(line for line in lines if line.startswith("Label:"))
        reasoning_line = next(line for line in lines if line.startswith("Reasoning:"))

        label = label_line.replace("Label:", "").strip().lower()
        reasoning = reasoning_line.replace("Reasoning:", "").strip()

        # Step 4: Validate the label
        if label not in VALID_LABELS:
            label = "unknown"

        return {"label": label, "reasoning": reasoning}

    except (KeyError, ValueError, IndexError) as e:
        # Parsing failed
        print(f"Parse error for description: {description[:50]}... — {str(e)}")
        return {"label": "unknown", "reasoning": f"Parse error: {str(e)}"}

    except Exception as e:
        # Network error, API error, etc.
        print(f"Classifier error for description: {description[:50]}... — {str(e)}")
        return {"label": "unknown", "reasoning": f"Classifier error: {str(e)}"}
