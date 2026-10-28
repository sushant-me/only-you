# Submission checklist

Deadline: **4 Nov 2026, 9:00 PM ET = 5 Nov, 7:45 AM NPT**. Do not start this on the last day.

## 1. Publish the repo (30 min, do first)

- [ ] Create an **empty public** GitHub repo, e.g. `only-you-hackathon`
- [ ] From `only-you-hackathon/`: `git remote add origin <url>` → `git push -u origin main`
- [ ] Open the repo URL in a **logged-out** browser: README renders, LICENSE visible, no `.env`
- [ ] `make gen test bench` works from a fresh clone
- [ ] `make judge` runs 105 tests and a 65-check audit, all green

## 2. Record and upload the 3-minute video

- [ ] Rehearse the shot list in `docs/video-3min.md` twice
- [ ] Record screen + voice — or voice-over `docs/demo-3min.mp4` (2:55, captioned, already within the limit)
- [ ] Length **≤ 3:00**; 1920×1080; H.264; under 300 MB
- [ ] Upload **unlisted** to YouTube; check it plays logged out
- [ ] Title: "ONLY YOU — the layer that decides who your agent obeys"
- [ ] Description: one-liner, repo link, benchmark link, honest caveat

## 3. Submit on the CV platform

- [ ] Open the submission form; keep it open in a second tab
- [ ] Paste fields from [`submission-final.md`](submission-final.md) (or `../SUBMISSION-DRAFT.md`):
  - name, one-line, track (Indie), theme (Build for Your World)
  - 60-word and 230-word descriptions
  - 3-minute video URL
  - public repo URL
  - bonus categories: Best Agentic Use-Case; Most Viral; Best Build on Meta Open Weights (contributor-model run committed)
- [ ] Add every teammate (solo = yourself)
- [ ] Screenshot the confirmation page; save the submission URL

## 4. Bonus entries

- [ ] **Agentic**: the task trace is in the video and the repo (`/api/task`); submit under this category
- [ ] **Viral**: post `docs/demo-x-vertical.mp4` on X between 6–8 Nov (`docs/x-post.md`); engagement
      closes 8 Nov 11:59 PM ET
- [ ] **Community**: share the gallery link once voting opens
- [ ] **Open weights**: only if the Muse Glimmer evaluator actually runs — otherwise skip

## 5. After submitting

- [ ] Update `BUILD_LOG.md` with the submission timestamp
- [ ] Email/DM the 12 contacts (`../only-you/docs/job-playbook.md`), attach the video + report
- [ ] Office hours: ask "what would make this a finalist?" and fix the top objection
- [ ] Final: confirm the submission is editable until the deadline and update if the model run lands

## Pre-flight (the morning of)

```bash
cd only-you-hackathon
make audit          # must be 42/42, exit 0
git status          # must be clean
git log --oneline   # event commits visible
```
