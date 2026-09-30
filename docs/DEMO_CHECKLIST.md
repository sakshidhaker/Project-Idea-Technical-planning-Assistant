# Workshop Demo Checklist and Backup Plan

## One day before
- [ ] `python check_setup.py` shows no [FAIL]
- [ ] Model file is inside `models/` (do not depend on download at the venue)
- [ ] Multilingual embedding model already downloaded once (run the app once with internet)
- [ ] `.env`: change `SECRET_KEY` and the admin password
- [ ] Create 2 demo users; ask 5 sample questions so history is not empty
- [ ] Add 3-4 more knowledge files about the topics you will present
- [ ] Record a 2-minute screen video of the full flow (backup)
- [ ] Copy the whole project folder to a pen drive
- [ ] Charge laptop, keep charger and mobile hotspot

## 30 minutes before
- [ ] Close heavy apps (Chrome tabs, games); plug in charger; set Power mode to Best performance
- [ ] Activate venv, run `python run.py`, open http://127.0.0.1:5000
- [ ] Wait for the GREEN dot in the sidebar
- [ ] Ask one warm-up question (first answer is always the slowest)
- [ ] Allow the microphone in Chrome once (click the lock icon in the address bar)
- [ ] Test one Hindi and one Hinglish question
- [ ] Set browser zoom 110-125 % for the projector, turn on dark theme

## Demo flow (5 minutes)
1. Landing page and intro animation
2. Sign up new user, lands directly in chat
3. Ask: "Give me 5 final year project ideas in machine learning"
4. Ask in Hinglish: "Mujhe Flask me login kaise banana hai?"
5. Tap the mic and speak a question
6. Show streaming, Regenerate, thumbs up/down
7. Chat history and search, then Home button
8. Create Artifact: PDF, download and open it
9. Admin page: users, chats, messages and feedback counts from SQLite
10. Explain pipeline: Prompt, Semantic RAG, Local Qwen, Validation, Answer

## If something goes wrong (backup plan)
| Problem | What to do |
| --- | --- |
| Model still loading (yellow dot) | App answers from the knowledge base; keep talking about the pipeline while it loads |
| Answer is weak or wrong | Press Regenerate, or say: "a 0.5B model is small; better knowledge files or a bigger model improves it" |
| Voice does not work | Type the question. Voice needs Chrome/Edge and internet |
| App will not start | `python check_setup.py`, then show the backup video |
| Port 5000 busy | Change the port in run.py: `app.run(port=5001)` |
| Laptop dies | Pen-drive copy on another laptop, or backup video |

## Questions to prepare for
- Why a local model? Privacy, offline, free, full control
- Why RAG? Grounds answers in your own files; helps small models
- How are passwords stored? Salted hash (werkzeug), never plain text
- Why SQLite? Zero setup, one file, enough for a single machine; can move to PostgreSQL
- Limits? Small model can be wrong, quality depends on the knowledge files, CPU is slower than GPU
- Future work? Bigger model, cloud deployment, PDF upload to the knowledge base, feedback-based improvement

## Deploy notes
- This app runs a local model, so deploy it on a machine with at least 4 GB free RAM (VPS or your own laptop).
- Use `pip install gunicorn` and `gunicorn -w 1 --threads 4 -b 0.0.0.0:8000 "backend.main:app"` (one worker: the model is loaded once).
- Put it behind HTTPS if you want voice input to work from other devices: the browser only allows the microphone on https or localhost.
- Free hosts like Render free tier are too small for the model. For a public demo use a bigger VPS or show it on your laptop with a hotspot.
