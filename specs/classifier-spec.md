# Classifier Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 2.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `build_few_shot_prompt()` and
`classify_episode()` in `classifier.py`.

---

## build_few_shot_prompt(labeled_examples, description)

### What it does
Constructs a prompt string for the LLM that includes the task instructions,
all labeled training examples, and the new episode description to classify.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `labeled_examples` | `list[dict]` | Each dict has `"title"`, `"description"`, `"label"` (and others). These are the examples you labeled in Milestone 1. |
| `description` | `str` | The episode description to classify. |

### Output

| Return value | Type | Description |
|---|---|---|
| prompt | `str` | A complete prompt string ready to send to the LLM. |

---

### Spec fields — fill these in before writing code

**Task instruction (what should the LLM know about the task?):**

```
[blank — describe the classification task and the four valid labels.
 What does each label mean? What should the LLM return?]
```

---

**How should labeled examples be formatted in the prompt?**

```
[blank — sketch out how each example will appear. What information from
 each labeled_example dict should you include? Title? Description? Label?
 What delimiter or structure separates examples?]
```

---

**Example block sketch (write one concrete example):**

```
[blank — write out what a single training example looks like in the prompt.
 Use placeholders like {title}, {description}, {label}.]
```

---

**How should the new episode (to be classified) be presented?**

```
[blank — how do you signal to the LLM that this is the episode to classify,
 not another example? What instruction follows the description?]
```

---

**What output format should you request from the LLM?**

```
[blank — you need to parse the response in classify_episode(). What format
 makes parsing reliable? Think about: a single label on its own line?
 A structured format like "Label: X / Reasoning: Y"? JSON?
 What are the tradeoffs?]
```

---

**Edge cases to handle in the prompt:**

```
[blank — what if labeled_examples is empty? What if the description is very
 short? How does your prompt handle these?]
```

---

## classify_episode(description, labeled_examples)

### What it does
Classifies a single podcast episode description using the few-shot LLM classifier.
Returns a dict with a label and reasoning.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `description` | `str` | The episode description to classify. |
| `labeled_examples` | `list[dict]` | Labeled training examples from `load_labeled_examples()`. |

### Output

| Return value | Type | Description |
|---|---|---|
| result | `dict` | Must have keys `"label"` and `"reasoning"`. `"label"` must be one of `VALID_LABELS` or `"unknown"`. |

---

### Spec fields — fill these in before writing code

**Step 1 — Build the prompt:**

```
[blank — which function do you call? What arguments do you pass?]
```

---

**Step 2 — Send to the LLM:**

```
[blank — what method do you call on _client? What parameters does it need?
 (Hint: see specs/system-design.md — "How the Groq Chat Completions API Works")]
```

---

**Step 3 — Parse the response:**

```
[blank — how do you extract the label and reasoning from the LLM's text output?
 What string operations or parsing logic do you need?
 This depends on the output format you chose in build_few_shot_prompt.]
```

---

**Step 4 — Validate the label:**

```
[blank — what do you do if the LLM returns a label that isn't in VALID_LABELS?
 What should label be set to?]
```

---

**Step 5 — Handle errors gracefully:**

```
[blank — what could go wrong? (Network error? Unparseable response?)
 What should the function return if something fails?
 Hint: the evaluation loop runs 20 calls — one bad response shouldn't crash everything.]
```

---

### Return value structure

```python
{
    "label": str,      # one of VALID_LABELS, or "unknown" if invalid/error
    "reasoning": str,  # brief explanation from the LLM
}
```

---

## Notes on label quality

The classifier is only as good as your labels. If your training examples have
inconsistent or ambiguous labels, the LLM will learn the wrong pattern.

Before implementing the classifier, re-read `data/taxonomy.md` and double-check
any labels you're unsure about. Annotation quality is part of the lab.
