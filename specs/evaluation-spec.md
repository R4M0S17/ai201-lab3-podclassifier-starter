# Evaluation Spec — Pod Classifier

Complete this spec **before** writing any code for Milestone 3.

Use Plan or Ask mode to think through each blank field. When you're done,
your answers here become the blueprint for `compute_accuracy()` and
`compute_per_class_accuracy()` in `evaluate.py`.

---

## Background: What is evaluation?

After building a classifier, we need to know how well it works. Evaluation answers:
- **Overall:** What fraction of episodes did we classify correctly?
- **Per-class:** Are we better at some labels than others?

Both functions take the same inputs: a list of predicted labels and a list of
ground-truth labels, in the same order.

---

## compute_accuracy(predictions, ground_truth)

### What it does
Returns the fraction of predictions that exactly match the ground truth.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`, one per episode. |
| `ground_truth` | `list[str]` | The correct labels, in the same order as `predictions`. |

### Output

| Return value | Type | Description |
|---|---|---|
| accuracy | `float` | A value between 0.0 and 1.0. |

---

### Spec fields — fill these in before writing code

**Formula:**

```
Accuracy = (number of correct predictions) / (total number of predictions)

A prediction is correct when it exactly matches the ground-truth label.
You divide by the total number of test episodes.
```

---

**Step-by-step logic:**

```
1. Check if lists are empty — if so, return 0.0
2. Initialize a counter for correct predictions to 0
3. Loop over each (predicted, ground_truth) pair using zip()
4. If predicted == ground_truth, increment the correct counter
5. Divide correct count by total count (len of lists)
6. Return the accuracy as a float between 0.0 and 1.0
```

---

**Edge case — what if both lists are empty?**

```
Return 0.0

Why: Mathematically, 0/0 is undefined. But practically, an empty test set
means no classifications were made, so we return 0.0 to indicate "no success"
rather than claiming perfect accuracy on zero examples.
```

---

**Worked example:**

```
predictions  = ["interview", "solo", "panel", "interview"]
ground_truth = ["interview", "solo", "solo",  "narrative"]

Matching pairs:
  Index 0: "interview" == "interview" ✓
  Index 1: "solo" == "solo" ✓
  Index 2: "panel" != "solo" ✗
  Index 3: "interview" != "narrative" ✗

Correct: 2
Total: 4
Accuracy = 2 / 4 = 0.5
```

---

## compute_per_class_accuracy(predictions, ground_truth)

### What it does
Returns accuracy broken down by each label. For each label in `VALID_LABELS`,
reports how many episodes with that ground-truth label were classified correctly.

### Inputs

| Parameter | Type | Description |
|---|---|---|
| `predictions` | `list[str]` | Labels predicted by `classify_episode()`. |
| `ground_truth` | `list[str]` | Correct labels, in the same order. |

### Output

A `dict` keyed by label. Each value is a dict with three keys:

```python
{
    "interview": {"correct": int, "total": int, "accuracy": float},
    "solo":      {"correct": int, "total": int, "accuracy": float},
    "panel":     {"correct": int, "total": int, "accuracy": float},
    "narrative": {"correct": int, "total": int, "accuracy": float},
}
```

---

### Spec fields — fill these in before writing code

**What does "correct" mean for a given class?**

```
For the "interview" class (or any class), an episode counts as correct if:
  - The ground-truth label IS "interview" (it's actually an interview)
  - AND the predicted label IS "interview" (we predicted it correctly)

In other words: both ground truth and prediction must match the class label
for it to count as a correct prediction for that class.
```

---

**What does "total" mean for a given class?**

```
"total" is the number of episodes whose ground-truth label IS that class,
regardless of what we predicted.

Example: if ground_truth has 3 episodes labeled "interview", then the
"interview" class has total=3 (even if we mispredicted some of them).

In other words: total is the size of each class in the ground truth.
```

---

**Step-by-step logic:**

```
1. Initialize a dict with all labels from VALID_LABELS:
   {label: {"correct": 0, "total": 0} for label in VALID_LABELS}

2. Loop over each (predicted, truth) pair using zip(predictions, ground_truth):

3. For each pair:
   - For the label that matches the ground_truth:
     * Increment total by 1 (this episode belongs to this class)
     * If predicted also matches this label, increment correct by 1

4. After the loop, for each label in the dict:
   - If total > 0: compute accuracy = correct / total
   - If total == 0: set accuracy = 0.0

5. Return the dict with all per-class stats
```

---

**Edge case — what if a class has no examples in ground_truth (total == 0)?**

```
Set accuracy to 0.0

Why: The docstring says "0.0 if total is 0". This avoids division by zero
and indicates "no correct predictions for this class" (because there were
no ground-truth examples of this class to classify).
```

---

**Worked example:**

```
predictions  = ["interview", "interview", "solo", "panel", "panel"]
ground_truth = ["interview", "solo",      "solo", "panel", "narrative"]

Analysis by class:
  interview (truth): index 0. Predicted "interview" ✓ → correct=1, total=1
  solo (truth):      indices 1, 2. Predicted ["interview", "solo"]. 
                     Correct: index 2 only → correct=1, total=2
  panel (truth):     index 3. Predicted "panel" ✓ → correct=1, total=1
  narrative (truth): index 4. Predicted "panel" ✗ → correct=0, total=1

label       correct  total  accuracy
----------  -------  -----  --------
interview   1        1      1.0
solo        1        2      0.5
panel       1        1      1.0
narrative   0        1      0.0
```

---

## Reflection questions (discuss at the checkpoint)

1. Your overall accuracy might be decent even if one class has very low accuracy.
   Why is per-class accuracy a more informative metric than overall accuracy alone?

2. If `panel` episodes consistently get misclassified as `interview`, what does
   that tell you about your training labels or your prompt?

3. You labeled 20 training episodes and evaluated on 20 test episodes (5 per class).
   How might the evaluation results change if you had labeled 100 training episodes?
   What if you had 200 test episodes?
