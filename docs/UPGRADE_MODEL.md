# Upgrade to a smarter model (better Hindi, Hinglish and code answers)

Qwen 2.5 0.5B is small and fast, but weak at Hindi and long plans. If your laptop has 8 GB RAM or more, try the 1.5B model:

1. Open the Hugging Face page `Qwen/Qwen2.5-1.5B-Instruct-GGUF` and confirm the exact file name (Files tab).
2. In `.env` remove the `#` from the three MODEL lines (repo, file, label).
3. Restart `python run.py`. The file (~1 GB) downloads once into `models/`.

3B (`Qwen/Qwen2.5-3B-Instruct-GGUF`) is better again but slower on CPU. Test speed before the demo.
