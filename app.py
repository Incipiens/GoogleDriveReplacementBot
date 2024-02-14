from flask import Flask, request, jsonify, render_template
import discord
import asyncio
import threading

app = Flask(__name__)

# Initialize Discord client outside the request handling
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@app.route('/')
def index():
    return render_template('index.html')

def start_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    @client.event
    async def on_ready():
        print('Discord client is ready.')

    client.run('') #Replace with client token

# Run Discord client in a background thread
threading.Thread(target=start_discord_bot, daemon=True).start()

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    # Ensure the Discord client is ready before attempting to send
    if not client.is_closed():
        future = asyncio.run_coroutine_threadsafe(send_file_to_discord(file), client.loop)
        result = future.result()  # This waits for the coroutine to finish and returns its result
        print(result)

    
    return jsonify({'message': 'File uploaded successfully!'})

async def send_file_to_discord(file):
    print("Sending file to Discord:", file.filename)
    channel = client.get_channel()  # Replace with channel ID
    message = await channel.send(file=discord.File(file.stream, filename=file.filename))
    print(message)

if __name__ == '__main__':
    app.run(debug=True)
