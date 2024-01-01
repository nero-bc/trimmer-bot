import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import subprocess
from loguru import logger

# Replace with your bot token
BOT_TOKEN = '6358741541:AAGghIkZCKDSXeC1Pzg5yaZDzoiZj1SBkvo'

# List of authorized user IDs
AUTHORIZED_USERS = [123456789, 5522433014]  # Replace with actual user IDs
OWNER_ID = 1895952308  # Replace with owner's user ID

# Set up logging
logger.add("trimmer_bot.log", rotation="10 MB")  # Rotate log files every 10 MB

def get_user_input(update, context, input_type):
    """Gets user input and handles potential errors."""
    while True:
        try:
            user_input = update.message.text
            if user_input:
                return user_input
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"Invalid input. Please enter a valid {input_type}.")
        except Exception as e:
            logger.error(f"Error getting user input: {str(e)}")
            context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while getting input. Please try again.")


def trim_media(update, context):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS or user_id == OWNER_ID:
        try:
            file = update.message.video or update.message.audio
            if file:
                file_path = file.get_file().download()

                # Interactively get start and end times
                start_time = get_user_input(update, context, "start_time")
                end_time = get_user_input(update, context, "end_time")

                # Validate input
                try:
                    start_time = int(start_time)
                    end_time = int(end_time)
                    if start_time >= end_time:
                        raise ValueError("End time must be greater than start time.")
                except ValueError as e:
                    logger.error(f"Invalid input: {str(e)}")
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid input. Please enter valid numerical times.")
                    return

                # Construct FFmpeg command based on file type
                if file.video:
                    ffmpeg_command = f"ffmpeg -i {file_path} -ss {start_time} -to {end_time} -c copy trimmed_output.mp4"
                else:
                    ffmpeg_command = f"ffmpeg -i {file_path} -ss {start_time} -to {end_time} -c copy trimmed_output.mp3"  # Adjust for audio

                # Execute FFmpeg command
                logger.debug(f"Executing FFmpeg command: {ffmpeg_command}")
                subprocess.run(ffmpeg_command, shell=True)

                # Send the trimmed file back to user
                logger.info("Sending trimmed file")
                with open("trimmed_output.mp4" if file.video else "trimmed_output.mp3", "rb") as trimmed_file:
                    context.bot.send_video(chat_id=update.effective_chat.id, video=trimmed_file) if file.video else context.bot.send_audio(chat_id=update.effective_chat.id, audio=trimmed_file)

                os.remove(file_path)  # Remove original file
                os.remove("trimmed_output.mp4")  # Remove trimmed file

            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Please send a video or audio file to trim.")

        except Exception as e:
            logger.error(f"Error during trimming: {str(e)}")
            context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred during trimming. Please try again or contact support.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, you're not authorized to use this command.")

def start(update, context):
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_USERS or user_id == OWNER_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm Trimmer Bot. Send me a video or audio file to trim using /trim.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, you're not authorized to use this bot.")

# Create the Updater and dispatcher
updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Add handlers for start and trim commands
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("trim", trim_media))

# Start the bot
updater.start_polling()
updater.idle()




#Procfile
#worker: python bot.py

#requirements.txt
#python-telegram-bot
#loguru
#subprocess
