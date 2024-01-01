# Base image with the latest Python version
FROM python:latest

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy your Python code
COPY . .

# Expose port for web interactions (if applicable)
EXPOSE 8080  # Adjust as needed

# Set command to start the bot
CMD ["python", "bot.py"]  # Replace 'bot.py' with your actual Python file name
