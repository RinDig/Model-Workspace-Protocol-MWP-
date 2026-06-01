# Principles

The Design Principles section in the README describes the architecture: one stage / plain text / layered context / edit surface / configure once. Those are the *what*. This file is the *why*. Three principles that motivate every pattern in `CONVENTIONS.md` and the 5 architectural choices in the README.

If you are deciding whether something belongs in ICM (a new stage, a new pattern, a new workspace), check it against these three. If a choice violates any of them, choose differently.

---

## Principle 1: Dialogue Is the Control Mechanism

The person running the workflow steers it through conversation and through editing the files in `output/` folders. Not through configuration objects, not through orchestration code, not through agent-to-agent negotiation. A human, talking to one agent, looking at files between stages.

This is the entire reason ICM exists. CrewAI, LangChain, AutoGen, and the other frameworks orchestrate *agents*. ICM orchestrates *with a person in the loop*. The agent reads the right files, does the next chunk of work, presents it, and waits for the human to redirect or proceed. The folder structure is plumbing; the dialogue is the engine.

**What this looks like in a stage:**

- Every creative stage has at least one `[Checkpoint]` step in its Process where the agent stops and presents to the human.
- The output of every stage is a file the human can open, edit, and save. The next stage picks up whatever they left there.
- The `setup` trigger is a single conversational pass, not a config form. The user answers in plain language.
- The `status` trigger reports back to the human; it does not auto-advance.

**What it does not look like:**

- A stage that runs end-to-end without ever checking with the human.
- Agents passing data through structured messages with no readable artifact in between.
- A questionnaire whose answers are validated mechanically before the user is allowed to proceed.
- Multi-agent debates resolving themselves before a human sees anything.

If a workspace ever feels like it is running *around* the human rather than *with* them, it is violating this principle.

---

## Principle 2: Code Does What Is Mechanical. Dialogue Does What Is Judgment.

Some operations in a workflow are deterministic. Phrase-matching a transcript to find a beat boundary. Extracting a delimited block from a markdown file. Filling a sequence's `durationInFrames` with the next sequence's start frame minus the current one. These operations have a right answer. Asking a model to do them at runtime is slow, expensive, and unreliable.

Other operations are not deterministic. Writing the next sentence so it sounds like the brand. Choosing which beat to keep when a cut goes long. Deciding whether a finding is real enough to ship. These operations require taste, context, and the ability to redirect. Asking a script to do them is impossible.

Every stage divides cleanly along this seam. The mechanical work belongs in `skills/[name]/scripts/`. The judgment work belongs in Process steps and Checkpoints.

**The test:** "Could a Python function do this reliably given the inputs?"

- Yes -> it goes in a script. The CONTEXT.md Process step says "run `scripts/extract-block.py`."
- No -> it stays in the Process step as a sentence describing what the agent should attempt, and a Checkpoint follows where the human reviews.

**Why this matters:**

- Dialogue cycles are the most expensive resource in the system. Spending them on mechanical work means less attention left for the work that actually needs judgment.
- Mechanical work that lives in scripts is testable. You can run `scripts/find-beats.py transcript.json` and verify the output by eye. You cannot do that with a paragraph of "the agent finds the beat boundaries by matching phrases."
- Mechanical scripts encode the exact failure modes you have hit (`fp16=False` on CPU, substring matching with `.rstrip(".,!?")`). That knowledge survives across runs and across team members.
- Judgment work stays where humans can see it land. Process steps are not abstract; they describe what the agent attempts, and Checkpoints catch where attempts can fail.

**Smell tests:**

- A CONTEXT.md Process step that says "the agent matches the transcript against the beat list" should probably be a script call. If it has any chance of producing wrong output the human cannot easily verify, it definitely should.
- A CONTEXT.md Process step that says "write the script following voice rules" is correctly in dialogue. No script can do that.
- A `skills/X/scripts/` file that requires an LLM call to do its job is in the wrong place. Scripts are for things models do not need to be in the loop for.

---

## Principle 3: Audits Are Earned, Not Invented

The Audit section of a stage CONTEXT.md lists the quality checks the agent runs before saving to `output/`. Those checks should come from real failures observed in real runs. Not from imagination, not from "best practices," not from what a reasonable workspace might want to check.

When a new workspace is built, its Audit section starts smaller than you would expect. A handful of checks for the most obvious failure modes (empty output, missing citations, wrong file format). The rest gets added as the workspace is run and things go wrong.

**Why this matters:**

- An Audit table full of invented checks is a permission slip for sloppy work. "Clarity: pass" means nothing if the author never defined what unclear output looks like in this domain.
- Real failures, named in the Audit table, prevent the same failure from shipping twice.
- A short Audit table that the agent actually applies is worth more than a long one full of vague checks that the agent skips.

**The voice-driven-animation example:**

The Audit section in that workspace's Stage 03 (Voice) includes "All beats found: every beat in BEATS resolves to a numeric start time." That entry exists because we ran the pipeline, a beat phrase did not match the transcript exactly, the pipeline produced a NULL beat start, and the downstream `timing.ts` silently wrote `NaN`. That happened in a real run. Now every future run audits against it.

The same workspace's Stage 03 also includes "Beat ordering: Beat N's start is strictly less than Beat N+1's start." That entry exists because two beats once shared the same opening phrase and the phrase-matcher returned identical times. The mp4 rendered with one of those beats silently cut.

These are not generic quality checks. They are scars.

**Smell tests:**

- An Audit table with 8 generic-sounding rows ("clarity", "completeness", "consistency", "tone alignment", "structural integrity") was probably invented.
- An Audit table with 3 specific rows ("phrase-match resolves all beats", "no two beats share an opening phrase", "the closing word's end time is within 1s of the audio length") was earned.
- If you cannot point to the specific incident a check came from, the check is decorative.

**How to bootstrap a new workspace:**

If the workspace is brand new and has no real-run history, the Audit section should be minimal. A few obvious checks. Mark the section "Initial audits, expand after first runs." Add entries each time the pipeline produces output the human had to reject. After three or four runs, the Audit table earns its weight.

---

## How These Three Connect

Dialogue is the control mechanism. The mechanical work moves out of dialogue and into scripts so dialogue stays focused on judgment. The judgment work needs audits, and those audits are earned through running the system with the human in the loop.

The 15 patterns in `CONVENTIONS.md` are mechanical realizations of these three principles. The 5 design principles in the README are the same realizations at a higher level. When you read either document, ask which of these three principles each pattern serves. If you find a pattern that does not serve any of them, that pattern should probably be removed.

When you build a new workspace, ask the three questions these principles imply:

1. Where in this workflow will the human stop and steer? (Principle 1 -> Checkpoints)
2. What in this workflow is mechanical, and what is judgment? (Principle 2 -> Scripts vs Process)
3. What have you actually seen go wrong in this domain? (Principle 3 -> Audit entries)

The workspace-builder questionnaire asks these explicitly. New workspaces inherit the principles by birth.

---

## A Short Self-Check for a Workspace

A workspace probably honors these principles if:

- Every creative stage has at least one Checkpoint in its Process.
- Every output folder is a file the human can edit between stages.
- Mechanical operations show up as `scripts/[name].py` call-outs in Process steps, not as English descriptions of what the agent should do.
- The Audit table for each stage is short (3 to 6 rows) and every entry could be traced back to a specific kind of failure.
- The `setup` trigger asks 8 to 15 conversational questions, not 40 dropdowns.

A workspace probably violates them if:

- Stages run end to end without human checkpoints.
- Process steps describe judgment work in passive voice ("the output is generated").
- The Audit section is long and generic.
- The questionnaire has category groupings and a "submit" button.
- The agent never asks the human for clarification.
