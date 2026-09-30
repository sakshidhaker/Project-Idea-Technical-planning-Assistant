from backend.main import app, start_background_model

if __name__ == "__main__":
    start_background_model()          # downloads / loads Qwen in the background
    app.run(debug=True, use_reloader=False, threaded=True)
