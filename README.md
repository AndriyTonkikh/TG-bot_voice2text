Voice recognition bot using Google's Speech Recognition API

This bot recognizes speech in voice messages and transcribes them to text using Google's Speech Recognition API. The bot is built using the aiogram and speech_recognition libraries in Python.
Prerequisites

    Python 3.7 or higher
    Soundfile
    Speech Recognition
    aiogram
    librosa
    dotenv

Installation

    Clone or download the repository to your local machine.
    Install the necessary libraries using pip install -r requirements.txt
    Create a .env file in the root directory of the project and add your Telegram bot token as TOKEN.

Usage

    Run the script bot.py using python bot.py.
    Start a conversation with the bot on Telegram by searching for its name and clicking on the "Start" button.
    Choose the language you want to transcribe to from the provided keyboard.
    Send a voice message to the bot, and it will reply with the text transcription.

Disclaimer

The use of Google's Speech Recognition API is subject to Google's terms of service. Make sure to comply with these terms when using this code.
