- uses my own repo see https://github.com/Immrudul/test-repo as used for this project
- oh also i did leak my own api key for now (W trust in datacurve lol), obv wouldn't be the case in other projects


Program flow:


- Run docker compose up --build
- Open http://127.0.0.1:8000/docs#/default/create_trace_traces_post and past in some trace, (use the trace that i’ve given as example both in the readme/codebase or you can use your own)
  - Let’s pretend you’re using the example i gave which is a full E2E implementation
  - The way this works is that we have the URL of the repo that i’ve put up publicly (https://github.com/Immrudul/test-repo)
    - This repo is actually part of a project that i did (open source blindfold rubiks solver:         https://github.com/Immrudul/pochmann-ai)
    - And i’ve introduced an error into this repo on purpose
    - I’ve also created tests for this repo so that we have a test suite we can use
  - On main, the code has an error, but on branch “fixed-bug1”, we have the fixed code
  - When we create the trace, into a docker container we:
    - Git clone the repo
    - Dynamically pull the branch name from the PR in the trace and switch to it
    - Compile and test the fixed code on the branch so that we know its safeto merge
    - Output the result of the tests
      - This fails on main, but passed on the bug-fixed1 branch, feel free to modify that in the trace and play around with it
  - Then we save the results of the tests, run the AI judge and save its output, and fill out our model for any trace and save it to our db finally


Plan:


Important questions to be asked:


1. What level of granularity do we want?

Do we want every keystroke and cursor move, or just higher level edit diffs like each save, commit, or logical changes? This is important because this pretty much determines the volume, structure, and cost of telemetry. Fine grained data like keeping track of every key stroke and mouse movement enables more behavioral modeling, but drastically increases storage and complexity. For now, we’ll stick to the assumption that keeping track of easily trackable events like commits, prs, cli commands, etc.

2. What’s your definition of “reasoning quality”?

Should the AI judge score reasoning on clarity, logical flow, correctness, or human-likeness?
This is critical for designing the evaluation rubric and LLM prompt for the QA judge. For now assuming to cover: 

                "1. Logical Flow - Did the developer move from cause to hypothesis to solution?\n"
                "2. Clarity - Are the steps and rationale easy to follow?\n"
                "3. Efficiency - Did they converge on the root cause quickly?\n"
                "4. Evidence - Did they validate assumptions with tests or diffs?\n"
                "5. Accuracy - Were conclusions and fixes correct?\n\n"

3 .What specific forms of data do we want from the developer?

Pretty safe to assume that we’re taking all the text written in the IDE like any code, terminal commands etc. But what if we wanted things like voice for the dev to explain their thought process (to actually introduce a real chain of thought though process) or screen sharing (so that we can see any external debugging tools the dev goes through like reading docs, searching specific syntax/commands etc) since that's a huge part of being a good developer.

4 .What defines a debugging session

Is it bounded by a single pull request, a branch, or an IDE session? This is important because it establishes session boundaries which are important for labeling and aligning data with “before” and “after” code states. Neutral assumption that 1 PR goes up and is the definition of a debug session. Scrappy and fast paced building involves lots of PRs like “feat: added xyz” or “chore: fixed xyz”. This also keeps it simple, we will take a single PR as the change for now.


5. How much does privacy matter?

Should we strip personally identifiable information such as usernames, file paths, or proprietary repo URLs before upload? Obviously developer telemetry may leak sensitive code or identifiers and its important to keep privacy restrictions in mind, but for now and for simplicity, we won’t worry about any important information being leaked.

Trace:

So after all these assumptions, here’s a final trace example that I’ve been using throughout the dev process of this takehome:

```json
{
  "trace_id": "e97e2a32-2f88-4b5d-bfe4-52a3e918b44b",
  "developer_id": "mrudul",
  "project": {
    "repo_url": "https://github.com/mrudul-suresh/rubiks-cube-solver",
    "branch": "bugfix/fix-solved-append",
    "language": "python"
  },
  "session_metadata": {
    "os": "Windows 11",
    "editor": "VSCode",
    "start_time": "2025-10-27T18:00:00Z",
    "end_time": "2025-10-27T18:15:00Z"
  },
  "events": [
    {
      "type": "file_opened",
      "timestamp": "2025-10-27T18:00:05Z",
      "file_path": "solve.py",
      "summary": "Opened Rubik’s Cube solver file to investigate edge detection logic"
    },
    {
      "type": "comment_added",
      "timestamp": "2025-10-27T18:02:30Z",
      "file_path": "solve.py",
      "content": "Noticed an incorrect pair being marked solved — 'G' and 'O' instead of 'L' and 'F'. Hypothesis: wrong variables appended."
    },
    {
      "type": "file_saved",
      "timestamp": "2025-10-27T18:03:45Z",
      "file_path": "solve.py",
      "diff": "- solved.append(\"G\")\n- solved.append(\"O\")\n+ solved.append(\"L\")\n+ solved.append(\"F\")",
      "summary": "Fixed incorrect variable names in find_already_solved()"
    },
    {
      "type": "terminal_command",
      "timestamp": "2025-10-27T18:05:10Z",
      "command": "pytest -q",
      "output": "E   AssertionError: Edge order mismatch: ['V', 'P', 'Q', 'C', 'K', 'E', 'I', 'G', ...]\n1 failed in 0.01s",
      "summary": "Initial test run shows mismatch before fix"
    },
    {
      "type": "file_saved",
      "timestamp": "2025-10-27T18:06:30Z",
      "file_path": "solve.py",
      "diff": "- solved.append(\"L\")\n- solved.append(\"F\")\n+ solved.append(\"L\")\n+ solved.append(\"F\")  # rechecked logic, confirmed fix",
      "summary": "Minor edit to confirm correct order and ensure tests pass"
    },
    {
      "type": "test_run",
      "timestamp": "2025-10-27T18:08:00Z",
      "command": "pytest -q",
      "output": "1 passed in 0.02s",
      "summary": "All tests passed after correction"
    },
    {
      "type": "commit_created",
      "timestamp": "2025-10-27T18:09:30Z",
      "commit_hash": "c1f9d7b",
      "message": "fix: corrected solved.append variables in find_already_solved()",
      "files_changed": ["solve.py"],
      "summary": "Committed fix for incorrect solved edge identification"
    },
    {
      "type": "pr_created",
      "timestamp": "2025-10-27T18:11:00Z",
      "branch": "bugfix/fix-solved-append",
      "target_branch": "main",
      "description": "Fix incorrect edge detection in find_already_solved function.\n\nBefore: marked G & O as solved instead of L & F.\nAfter: corrected append logic to L & F.\nAll pytest cases now pass successfully.",
      "diff_summary": "1 file changed, 2 insertions(+), 2 deletions(-)",
      "link": "https://github.com/mrudul-suresh/rubiks-cube-solver/pull/12",
      "summary": "Opened PR to merge bug fix into main branch"
    }
  ]
}

It involves keeping track of events like file openings, any dev comments to try as one of the easiest ways to capture dev chain of thought, file saves along with the differences so that we can look at iterative thinking*, terminal commands, any tests that have been run, commits, and the PR created. 

* the iterative thinking for file saves: problems are not evenly distributed throughout a file and solving any problem involving any file does not mean that you’re changing all parts of the file equally. So keeping track of saves shows which parts of the code were most problematic. Also, looking at what was changed many times and what was changed a couple times is valuable information for the problem at hand.


Architecture:

FastAPI Backend

Well first of all, who doesn’t love Python? So the FastAPI backend acts as the core API layer receives traces, triggers validations, integrates AI, and stores results.

Why FastAPI?
- Asynchronous and fast
- Developer friendly, automatic OpenAPI docs, type hints, and Pydantic models make schema validation effortless
- Lightweight containerization: important since we know we have to have everything running in Docker
- Also used FastAPI at Plato, so little more gravitation towards using it again

Docker-in-Docker (DinD) / Docker Socket Mount

We know that we need to do 2 things from the given instructions. 1 being that we need to run the repo tests in a docker container, 2 being that our entire project needs to run in a docker container as well. So clearly, we’re going to require using something like docker in docker. This allows the backend container to spawn new isolated containers to test pull requests dynamically. This is what will make using our separate public repo possible. 

So essentially:
- Environment isolation: Each test runs in a clean container so no side effects between sessions
- Consistency: Ensures every PR/test runs in the same predictable environment (and also each run of this project)
- Scalability: Easy to offload or parallelize testing by spinning up multiple containers

SQLite Database (via SQLAlchemy ORM)

Our db. I actually really love SQLite for small projects and it's enough to get the job done lightweight and fast here without much setup at all.

Why SQLite?

- Lightweight and portable: No external setup and also runs seamlessly inside Docker
- Perfect for local testing and demos: Simple, file-based persistence
- Compatible with SQLAlchemy: Easily upgradeable to PostgreSQL later with minimal code change so even the db is scalable

Groq + OpenAI SDK:

Honestly a free api key that i could use at a pretty abusive rate lol (30 reqs/min i believe) but also

- Drop-in compatibility: Groq’s API is fully OpenAI-compatible so it works with openai Python client directly
- Lower latency: Groq’s inference accelerators deliver sub-second LLM responses.
- Freeeeeeee and fast


Improvements or things to improve on after our implemented MVP:

Of course this project is quite scrappy but I think it turned out pretty cool and it was definitely a good learning experience. Projects like these are the best way to get yourself to sit down and lock in for hours on end (it definitely far more exciting solving new problems than doing outdated university problem sets lol) so you can definitely understand my startup hype

There are definitely a lot of improvements that can be made to the project however and lets look at some:

- Most important: hide api keys lol i did not hide it but i trust datacurve 
- The bonus for ingestion
  - Although this shouldn’t be too hard to add quite quickly pretty soon 
  - We can have some sort of incremental ingestion endpoint (e.g., POST /trace/:id/event) that appends each event to a temporary store (i was thinking of something like S3 perhaps) and then we can have some sort of “finalize” endpoint that concatenates all our json 
    - This also may introduce some complexities about how WE will go through this large amount of data especially when using the AI judge since throwing in a huge amount of context/info might not be a good idea. But i think the first thing that comes to mind is parallel summarizer LLM calls that feed back into the LLM might not be a bad idea but can do some more thinking on context engineering etc
- The url for the test repo currently isn’t dynamic, so making that dynamically pull from the PR event would be a logical next step 
    - But at least for now we do have a full working E2E example so that's why this isn’t higher in priority
- Outputs need to be cleaned up but they do get the job done




