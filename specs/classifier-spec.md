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
You are classifying podcast episodes by their format. Classify the episode
into exactly one of these four labels:

- interview: a conversation between a host and one or more guests
- solo: a single host speaking from memory, experience, or opinion — no guests,
  no assembled external sources
- panel: multiple guests with roughly equal speaking time, often debating or
  discussing a topic together
- narrative: a story assembled from external sources — interviews, archival
  audio, reporting — with a clear narrative arc

Return only the label and your reasoning. Do not explain the taxonomy.
```

---

**How should labeled examples be formatted in the prompt?**

```
Each example should include the episode title, a brief excerpt or the full
description, and the correct label. Separate examples with a blank line or
a delimiter like "---". Include all fields that help the model see why the
label was applied — title and description are both useful; other fields
(like episode ID) are not needed.
```

---

**Example block sketch (write one concrete example):**

```
Title: {title}
Description: {description}
Label: {label}
```

---

**How should the new episode (to be classified) be presented?**

```
Present it in the same format as the labeled examples, but omit the Label
line and replace it with an instruction to classify. For example:

Title: {title}
Description: {description}
Label: ?

Then add a line like: "Classify the episode above. Return your answer in
the format below:" followed by the output format you chose.
```

---

**What output format should you request from the LLM?**

```
Use a simple structured format:

Label: <label>
Reasoning: <brief explanation>

Why this format:
- Easy for the LLM to produce (doesn't require JSON escaping)
- Trivial to parse with split() and simple string operations
- Clear, human-readable for debugging
- Robust: even if formatting is slightly off (extra spaces, etc.),
  we can extract with startswith() and strip()

Alternative considered — JSON: More structured but overkill here.
This is two fields, not a complex nested object. JSON adds no value
and makes parsing more fragile if the LLM adds explanation text.
```

---

**Edge cases to handle in the prompt:**

```
1. Empty labeled_examples:
   - Still include the task instruction and label definitions
   - Add a note: "(No training examples provided; classify based on task
     instructions above.)"
   - This becomes a zero-shot attempt, which is less accurate but won't crash
   - The LLM still has the taxonomy, so it can make a reasonable guess

2. Very short description (e.g., title only):
   - Format as-is. The taxonomy is clear enough that even one sentence
     helps the LLM decide
   - Edge case: blank/null description
     → Return {"label": "unknown", "reasoning": "Description is empty"}
     from classify_episode() without calling the LLM

3. Format robustness:
   - Always include both title and description in the prompt, even if
     one is very short
   - This gives the LLM more signal
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
Call build_few_shot_prompt(labeled_examples, description) and store the
returned string in a variable (e.g., prompt). Pass through both arguments
exactly as received — no modification needed before calling.
```

---

**Step 2 — Send to the LLM:**

```
Call _client.chat.completions.create() with:
  - model: the model name from config (LLM_MODEL)
  - messages: a list with one dict — {"role": "user", "content": prompt}
    (system-design.md shows an optional system message too — either shape works)
  - max_tokens: a reasonable limit (e.g., 200–300) to keep responses concise

Extract the response text from:
  response.choices[0].message.content
```

---

**Step 3 — Parse the response:**

```
Given the "Label: X\nReasoning: Y" format, parse as follows:

1. Split response by newlines: lines = response.split('\n')
2. Find the line starting with "Label:":
   - label_line = next(line for line in lines if line.startswith('Label:'))
   - label = label_line.replace('Label:', '').strip().lower()
3. Find the line starting with "Reasoning:":
   - reasoning_line = next(line for line in lines if line.startswith('Reasoning:'))
   - reasoning = reasoning_line.replace('Reasoning:', '').strip()

Why this approach:
- Handles extra whitespace gracefully (strip() cleans it up)
- Case-insensitive (lowercase the label before validation)
- Doesn't assume line order (uses startswith to find each field)
- Fails explicitly if either field is missing (exception caught in Step 5)
```

---

**Step 4 — Validate the label:**

```
if label.lower() not in VALID_LABELS:
    label = "unknown"

Why "unknown" and not raise an error:
- The evaluation loop calls this function 20 times
- One bad response shouldn't crash the entire evaluation
- "unknown" tells the caller "we tried but couldn't classify confidently"
- It's a valid return value that downstream code can handle (e.g., exclude
  from accuracy metrics, log it for debugging)

Debug note: Log which episodes returned "unknown" — if it's more than 1-2,
your prompt or output format may need tuning.
```

---

**Step 5 — Handle errors gracefully:**

```
Wrap the entire classify_episode logic in a try-except block:

try:
    prompt = build_few_shot_prompt(labeled_examples, description)
    # ... send to LLM ...
    # ... parse response ...
    # ... validate label ...
    return {"label": label, "reasoning": reasoning}

except (KeyError, ValueError, IndexError) as e:
    # Parsing failed (e.g., missing "Label:" line, no label found)
    return {"label": "unknown", "reasoning": f"Parse error: {str(e)}"}

except Exception as e:
    # Network error, API error, etc.
    return {"label": "unknown", "reasoning": f"Classifier error: {str(e)}"}

Why this approach:
- Catches parsing errors (IndexError, ValueError from next() if line not found)
- Catches API/network errors without crashing the evaluation loop
- Always returns a valid dict with "label" and "reasoning"
- Includes error details in reasoning for debugging

Important: Don't silence errors completely. Log them (print or logging module)
so you can spot patterns (e.g., "5 episodes failed with 'parse error'").
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

---

## Implementation Notes

*Fill this in after implementing and testing both functions.*

**Test: what does the raw LLM response look like for one episode?**

```
Episode tested: [title]
Raw response text: [paste it here]
```

**How did you parse the label out of the response?**

```
[describe the string operations — strip, split, lower, etc.]
```

**Did any episodes return `"unknown"`? If so, why?**

```
[yes / no — if yes, what did the raw response look like?]
```

**One thing about the output format that surprised you:**

```
[your answer here]
```
