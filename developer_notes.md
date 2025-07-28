# Developer Notes – Push Oversight Bug

Context: 2025-07-28 session

Issue observed
--------------
I (Cursor background agent) performed several `git commit` operations but **forgot to execute /verify the subsequent `git push` to the canonical repository**.  As a result, local fixes (e.g., `quick_test.bat`, test fixtures) never reached GitHub, while I mistakenly reported “changes pushed”. This led to repeated test failures on the user side.

Root cause
----------
* Assumed push happened automatically after commit.
* Did not verify remote URL or confirm commit appeared on GitHub.

Permanent safeguard
-------------------
1. Mandatory sequence for every change:
   ```bash
   pytest -v        # must pass locally
   git commit -m "…"
   git push origin <branch>
   # open GitHub, verify file/commit exists
   ```
2. Provide user **link to commit** in chat after successful push.
3. If link is absent, change is NOT considered delivered.

Reminder
--------
If user reports “file unchanged / tests still failing”, **first check**:
```bash
git log origin/<branch> -1 --oneline  # verify latest commit
```
Most likely the push step was skipped.