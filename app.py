from flask import Flask, request, jsonify, render_template, send_from_directory
import discord
import asyncio
import threading
import io
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

# Initialize Discord client outside the request handling
intents = discord.Intents.default()
client = discord.Client(intents=intents)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/download')
def download():
    # Read the existing data from db.json
    try:
        with open('db.json', 'r') as db_file:
            db_data = json.load(db_file)
            files = db_data.get('files', {})
    except (FileNotFoundError, json.JSONDecodeError):
        files = {}

    # Convert the files dictionary to a list including the number of parts
    files_list = [name for name, info in files.items()]

    return render_template('download.html', files=files_list)


def start_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    @client.event
    async def on_ready():
        print('Discord client is ready.')

    client.run(os.environ['DISCORD_TOKEN'])


# Run Discord client in a background thread
threading.Thread(target=start_discord_bot, daemon=True).start()


@app.route('/uploadFile', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename

    # Ensure the Discord client is ready before attempting to send
    if not client.is_closed():
        future = asyncio.run_coroutine_threadsafe(send_file_to_discord(file), client.loop)
        result = future.result()  # This waits for the coroutine to finish and returns its result
        print(result)

    # Read the existing data from db.json
    try:
        with open('db.json', 'r') as db_file:
            db_data = json.load(db_file)
    except (FileNotFoundError, json.JSONDecodeError):
        db_data = {'files': {}}

    # Increment the parts count for the uploaded file
    if filename in db_data['files']:
        db_data['files'][filename]['parts'] += 1
    else:
        db_data['files'][filename] = {'parts': 1}

    # Write the updated data back to db.json
    with open('db.json', 'w') as db_file:
        json.dump(db_data, db_file, indent=4)

    return jsonify({'message': 'File uploaded successfully!'})

@app.route('/downloadFile/<filename>')
def download_file(filename):
    # Ensure the directory exists
    os.makedirs('partstostitch', exist_ok=True)

    # Remove the files from partstostich after finish
    @app.teardown_request
    def remove_files():
        for file in os.listdir('partstostitch'):
            os.remove(os.path.join('partstostitch', file))

    # Ensure the Discord client is ready before attempting to fetch messages
    if not client.is_closed():
        # Run the coroutine in the same thread as the Discord client's event loop
        future = asyncio.run_coroutine_threadsafe(
            fetch_and_save_files(filename), client.loop
        )
        result = future.result()  # This waits for the coroutine to finish and returns its result
        if result > 1:  # Check if multiple files were downloaded
            # Merge the files
            with open(f'partstostitch/{filename}', 'wb') as merged_file:
                for part_num in range(1, result + 1):
                    part_filename = f'{filename}.part{part_num}'
                    part_path = os.path.join('partstostitch', part_filename)
                    with open(part_path, 'rb') as part_file:
                        merged_file.write(part_file.read())
                    os.remove(part_path)  # Remove the part file after merging
            return send_from_directory('partstostitch', filename, as_attachment=True, mimetype='application/octet-stream')
        elif result == 1:
            # Only one file, no need to merge
            return send_from_directory('partstostitch', filename, as_attachment=True, mimetype='application/octet-stream')
        else:
            # No files were downloaded
            return jsonify({'error': 'No files were found to download'}), 404
    else:
        return jsonify({'error': 'Discord client is not ready'}), 503

async def fetch_and_save_files(filename):
    channel = client.get_channel(int(os.environ['DISCORD_CHANNEL']))
    messages = [message async for message in channel.history()]
    count = 0

    for message in messages:
        for attachment in message.attachments:
            if attachment.filename.startswith(filename):
                file_bytes = await attachment.read()
                file_path = os.path.join('partstostitch', attachment.filename)
                with open(file_path, 'wb') as file:
                    file.write(file_bytes)
                count += 1

    return count


async def send_file_to_discord(file):
    print("Sending file to Discord:", file.filename)
    channel = client.get_channel(int(os.environ['DISCORD_CHANNEL']))
    file_bytes = file.read()
    message = await channel.send(file=discord.File(io.BytesIO(file_bytes), filename=file.filename))
    print(message)


if __name__ == '__main__':
    app.run(debug=True)
