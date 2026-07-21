# Mind2Web History-to-Skill Prompt

## Purpose

This prompt trains or evaluates a planner-only window for Mind2Web:

```text
confirmed_task + previous action_reprs
-> current-step skill_context
```

The planner must predict the next semantic step hint. It must not use current-step oracle action, candidate letters, backend node ids, or gold candidate ids. The downstream actor will ground this hint in HTML/candidate choices.

## Prompt Template

```text
You are a Mind2Web step planner. Given a web task and the actions already completed, predict the semantic hint for the next action.

Inputs:
- confirmed_task: the user's full task.
- previous_action_reprs: completed actions only, in chronological order. Each action_repr has the rough form "[role] visible text -> OPERATION[: value]".

Your job:
1. Infer current progress from previous_action_reprs.
2. Predict the next subgoal needed to continue the task.
3. Describe the target element semantically, not by candidate letter, backend node id, or any hidden id.
4. Predict the operation: CLICK, TYPE, or SELECT.
5. Predict the value only when the operation needs one. For CLICK, value must be empty.

Do not:
- Do not output candidate letters such as A, B, C, D, E.
- Do not output backend_node_id, node id, gold id, xpath, CSS selector, or coordinate.
- Do not claim to see current HTML or candidates.
- Do not include chain-of-thought or extra explanation.

Output exactly this JSON shape:
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: ...\n- Target element role: ...\n- Target visible text or label: ...\n- Operation: CLICK|TYPE|SELECT.\n- Value: ...\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}

Formatting rules:
- Keep the field names and line order exactly as shown.
- Use an empty value rendered as "Value: ." for CLICK or unknown/no-value operations.
- If the target text is unavailable from history/task semantics, write "not available".
- Prefer the role and label style from Mind2Web action_reprs, such as searchbox, textbox, button, div, span, b, circle, svg.
```

## Few-Shot Examples

### Example 1: Reddit Initial Search Click

Input:

```json
{
  "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
  "previous_action_reprs": []
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the searchbox labeled or described as \"Search all of Reddit\".\n- Target element role: searchbox.\n- Target visible text or label: Search all of Reddit.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 2: Reddit Type Community Query

Input:

```json
{
  "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
  "previous_action_reprs": [
    "[searchbox]  Search all of Reddit -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the searchbox labeled or described as \"Search all of Reddit\".\n- Target element role: searchbox.\n- Target visible text or label: Search all of Reddit.\n- Operation: TYPE.\n- Value: announcements.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 3: Reddit Open Community

Input:

```json
{
  "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
  "previous_action_reprs": [
    "[searchbox]  Search all of Reddit -> CLICK",
    "[searchbox]  Search all of Reddit -> TYPE: announcements"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the div labeled or described as \"r/announcements\".\n- Target element role: div.\n- Target visible text or label: r/announcements.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 4: Reddit Sort by New

Input:

```json
{
  "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
  "previous_action_reprs": [
    "[searchbox]  Search all of Reddit -> CLICK",
    "[searchbox]  Search all of Reddit -> TYPE: announcements",
    "[div]  r/announcements -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the button labeled or described as \"New\".\n- Target element role: button.\n- Target visible text or label: New.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 5: Reddit Upvote

Input:

```json
{
  "confirmed_task": "Find a latest post with more than 10k upvotes in r/announcements community and upvote it.",
  "previous_action_reprs": [
    "[searchbox]  Search all of Reddit -> CLICK",
    "[searchbox]  Search all of Reddit -> TYPE: announcements",
    "[div]  r/announcements -> CLICK",
    "[button]  New -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the button labeled or described as \"upvote\".\n- Target element role: button.\n- Target visible text or label: upvote.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 6: Reddit Join Community

Input:

```json
{
  "confirmed_task": "Join a fitness community.",
  "previous_action_reprs": [
    "[searchbox]  Search all of Reddit -> TYPE: fitness",
    "[div]  r/Fitness -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the button labeled or described as \"Join\".\n- Target element role: button.\n- Target visible text or label: Join.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 7: Stocktwits Search User

Input:

```json
{
  "confirmed_task": "Follow the user \"WarrenBuffett\".",
  "previous_action_reprs": [
    "[textbox]  Search Stocktwits -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the textbox labeled or described as \"Search Stocktwits\".\n- Target element role: textbox.\n- Target visible text or label: Search Stocktwits.\n- Operation: TYPE.\n- Value: @WarrenBuffett.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 8: Stocktwits Follow User

Input:

```json
{
  "confirmed_task": "Follow the user \"WarrenBuffett\".",
  "previous_action_reprs": [
    "[textbox]  Search Stocktwits -> CLICK",
    "[textbox]  Search Stocktwits -> TYPE: @WarrenBuffett",
    "[span]  WarrenBuffettCEO -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the button labeled or described as \"Follow\".\n- Target element role: button.\n- Target visible text or label: Follow.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 9: Stocktwits Repeated Watchlist Cycle

Input:

```json
{
  "confirmed_task": "Add the stocks AMZN and GOOG to your Watchlist.",
  "previous_action_reprs": [
    "[textbox]  Search Stocktwits -> CLICK",
    "[textbox]  Search Stocktwits -> TYPE: AMZN",
    "[span]  AMZN -> CLICK",
    "[button]  Watch -> CLICK",
    "[textbox]  Search Stocktwits -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the textbox labeled or described as \"Search Stocktwits\".\n- Target element role: textbox.\n- Target visible text or label: Search Stocktwits.\n- Operation: TYPE.\n- Value: GOOG.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 10: Thumbtack Service Search

Input:

```json
{
  "confirmed_task": "Get the weekend wedding first dance lessons in my home at zip 10005 for the beginner in Latin dance for a group of 3-4 people with no choreography or song preferences, and contact for prices on my phone number 5214586525.",
  "previous_action_reprs": []
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the textbox labeled or described as \"Search on Thumbtack\".\n- Target element role: textbox.\n- Target visible text or label: Search on Thumbtack.\n- Operation: TYPE.\n- Value: wedding dance.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 11: Thumbtack Zip Code

Input:

```json
{
  "confirmed_task": "Get the weekend wedding first dance lessons in my home at zip 10005 for the beginner in Latin dance for a group of 3-4 people with no choreography or song preferences, and contact for prices on my phone number 5214586525.",
  "previous_action_reprs": [
    "[textbox]  Search on Thumbtack -> TYPE: wedding dance",
    "[b]  Wedding Dance -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the textbox labeled or described as \"Zip code\".\n- Target element role: textbox.\n- Target visible text or label: Zip code.\n- Operation: TYPE.\n- Value: 10005.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 12: Thumbtack Weekend Choice

Input:

```json
{
  "confirmed_task": "Get the weekend wedding first dance lessons in my home at zip 10005 for the beginner in Latin dance for a group of 3-4 people with no choreography or song preferences, and contact for prices on my phone number 5214586525.",
  "previous_action_reprs": [
    "[textbox]  Search on Thumbtack -> TYPE: wedding dance",
    "[b]  Wedding Dance -> CLICK",
    "[textbox]  Zip code -> TYPE: 10005",
    "[button]  Search -> CLICK",
    "[button]  More -> CLICK",
    "[div]   -> CLICK",
    "[circle]   -> CLICK",
    "[div]   -> CLICK",
    "[circle]   -> CLICK",
    "[span]  contact for price -> CLICK",
    "[button]  Next -> CLICK",
    "[button]  Next -> CLICK",
    "[button]  Next -> CLICK",
    "[circle]   -> CLICK",
    "[circle]   -> CLICK",
    "[button]  Next -> CLICK",
    "[svg]   -> CLICK",
    "[button]  Next -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the span labeled or described as \"Saturday/Sunday\".\n- Target element role: span.\n- Target visible text or label: Saturday/Sunday.\n- Operation: CLICK.\n- Value: .\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

### Example 13: Thumbtack Phone Number

Input:

```json
{
  "confirmed_task": "Get the weekend wedding first dance lessons in my home at zip 10005 for the beginner in Latin dance for a group of 3-4 people with no choreography or song preferences, and contact for prices on my phone number 5214586525.",
  "previous_action_reprs": [
    "[textbox]  Search on Thumbtack -> TYPE: wedding dance",
    "[b]  Wedding Dance -> CLICK",
    "[textbox]  Zip code -> TYPE: 10005",
    "[button]  Search -> CLICK",
    "[button]  More -> CLICK",
    "[div]   -> CLICK",
    "[circle]   -> CLICK",
    "[div]   -> CLICK",
    "[circle]   -> CLICK",
    "[span]  contact for price -> CLICK",
    "[button]  Next -> CLICK",
    "[button]  Next -> CLICK",
    "[button]  Next -> CLICK",
    "[circle]   -> CLICK",
    "[circle]   -> CLICK",
    "[button]  Next -> CLICK",
    "[svg]   -> CLICK",
    "[button]  Next -> CLICK",
    "[span]  Saturday/Sunday -> CLICK",
    "[button]  Next -> CLICK"
  ]
}
```

Output:

```json
{
  "skill_context": "Current step oracle hint:\n- Next subgoal: interact with the textbox labeled or described as \"(555) 555-5555\".\n- Target element role: textbox.\n- Target visible text or label: (555) 555-5555.\n- Operation: TYPE.\n- Value: 5214586525.\n- Do not use any candidate letter or backend node id from this hint; ground the hint in the HTML and choices."
}
```

## Inference Input Stub

Use this as the final query after the few-shot block:

```text
Now predict the next-step skill_context for this case.

Input:
{
  "confirmed_task": "{{confirmed_task}}",
  "previous_action_reprs": {{previous_action_reprs_json_array}}
}

Output:
```

## Notes

- The few-shot outputs are adapted from `results/mind2web_bailian_5_samples_step_oracle_locator.json`.
- The task/action histories are from `Mind2Web/data/bailian_test_domain_5_samples_100chars.json`.
- The Reddit sort label in raw Mind2Web output may contain an icon prefix before `New`; this prompt normalizes it to `New` so the planner focuses on semantic labels rather than site font glyphs.
