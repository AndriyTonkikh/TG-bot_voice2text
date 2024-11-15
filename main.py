import soundfile as sf
import math
import speech_recognition as speg
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram import types
import librosa
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Налаштування Key Vault
VAULT_URL = "https://telegramtokentas.vault.azure.net/    "
SECRET_NAME = "TelegramBotToken"

# Отримання токена з Key Vault
credential = DefaultAzureCredential()
client = SecretClient(vault_url=VAULT_URL, credential=credential)
TOKEN = client.get_secret(SECRET_NAME).value

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)
lang = None


@dp.message_handler(Command("Start"))
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    global lang
    markup = types.ReplyKeyboardMarkup(row_width=1)
    but1 = types.KeyboardButton(text="/Ua")
    but2 = types.KeyboardButton(text="/Eng")
    but3 = types.KeyboardButton(text="/Ru")
    but4 = types.KeyboardButton(text="/Start")
    markup.add(but1, but2, but3, but4)
    await bot.send_message(message.chat.id,
                           f"""Hello, {message.from_user.full_name}! I am ready!
        Choose language: 'Eng' - for English, 'Ru' - for Russian, 'Ua' - for Ukrainian""",
                           reply_markup=markup)


@dp.message_handler(commands=['Ua'])
async def set_ua(message: types.Message):
    global lang
    lang = "uk-UA"
    await message.reply(f"Transcript to Ukrainian")
    await bot.send_message(message.chat.id, "Keyboard removed.", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['Eng'])
async def set_eng(message: types.Message):
    global lang
    lang = "en-GB"
    await message.reply(f"Transcript to English")
    await bot.send_message(message.chat.id, "Keyboard removed.", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['Ru'])
async def set_ru(message: types.Message):
    global lang
    lang = "ru-RU"
    await message.reply(f"Transcript to Russian")
    await bot.send_message(message.chat.id, "Keyboard removed.", reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(content_types=[types.ContentType.VOICE])
async def voice_message_handler(message: types.Message) -> None:
    """
    This handler receives voice messages and saves them in WAV format
    """
    global lang
    if type(lang) != str:
        await message.answer("Choose language before we start")
    try:
        # get voice file ID and download the voice message
        voice_id = message.voice.file_id

        voice = await bot.get_file(voice_id)

        # get path for saving the voice message in WAV format
        wav_path = f"{voice_id}.wav"

        # save voice message in WAV format
        await bot.download_file(voice.file_path, wav_path)

        voice_audio, sr = librosa.load(wav_path, sr=8000)
        await message.answer("File in processing")
        # convert to mono if necessary
        if voice_audio.ndim > 1:
            voice_audio = librosa.to_mono(voice_audio)

        # apply a pre-emphasis filter to the audio
        voice_audio = librosa.effects.preemphasis(voice_audio)

        chunk_size = 59*8000
        num_chunks = int(math.ceil(len(voice_audio) / float(chunk_size)))
        full_message = []

        for i in range(1, num_chunks):

            start = i * chunk_size
            end = min(len(voice_audio), (i + 1) * chunk_size)
            chunk_audio = voice_audio[start:end]

            # save chunk as a WAV file
            chunk_path = f"chunk{i}.wav"
            sf.write(chunk_path, chunk_audio, samplerate=8000)
            await message.answer(f"Processing {i}/{num_chunks}")
            # recognize speech in chunk
            r = speg.Recognizer()
            with speg.AudioFile(chunk_path) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data, language=lang)
                full_message.append(text)
        stringg = str(full_message)
        string_size = 4000
        string_chunks = [stringg[i:i + string_size] for i in range(0, len(stringg), string_size)]

        # Виводимо кожну частину окремо
        for str_chunk in string_chunks:
            await message.answer(str_chunk)

    except:

        await message.reply("It`s too hard for me to recognize it! \n Sorry")

    finally:
        def cleaner():
            for item in os.listdir():
                if item.endswith('wav'):
                    os.remove(item)
        cleaner()


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp)
