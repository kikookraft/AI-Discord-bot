import asyncio
import json
import sys
import websockets

class AIStream:
    def __init__(self, host, uri):
        self.host = host
        self.uri = uri
        # format: ["user: message", "user: message"]
        self.mesages = []
        
    def add_message(self, user, message):
        formatted_message = f"{user}: {message}\n"
        self.messages.append(formatted_message)
        
    def messages_to_context(self) -> str:
        context = ""
        for message in self.mesages:
            context += message
        return context

    async def run(self, context):
        # create the full context with the character personality
        #contexct is in the form "user: message\n"
        
        request = {
            'prompt': context,
            'max_new_tokens': 200,
            'do_sample': True,
            'temperature': 1.3,
            'top_p': 0.1,
            'typical_p': 1,
            'epsilon_cutoff': 0,  # In units of 1e-4
            'eta_cutoff': 0,  # In units of 1e-4
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.18,
            'top_k': 40,
            'min_length': 0,
            'no_repeat_ngram_size': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
            'seed': -1,
            'add_bos_token': True,
            'truncation_length': 1024,
            'ban_eos_token': False,
            'skip_special_tokens': True,
            'stopping_strings': ["You", "You:", "You: ", "you", "you:"]
        }
        
        async with websockets.connect(self.uri, ping_interval=None) as websocket:
            await websocket.send(json.dumps(request))

            # yield context  # Remove this if you just want to see the reply

            while True:
                incoming_data = await websocket.recv()
                incoming_data = json.loads(incoming_data)

                match incoming_data['event']:
                    case 'text_stream':
                        yield incoming_data['text']
                    case 'stream_end':
                        return

    async def print_response_stream(self, prompt):
        async for response in self.run(prompt, "user"):
            print(response, end='')
            sys.stdout.flush()

class bot_context:
    def __init__(self):
        self.mentionned = False
        self.mentionned_message_id = None
        self.mentionned_channel_id = None
        self.mentionned_timestamp = None
        
    def set_mentionned(self, message_id, channel_id, timestamp):
        self.mentionned = True
        self.mentionned_message_id = message_id
        self.mentionned_channel_id = channel_id
        self.mentionned_timestamp = timestamp
        
    def is_mentionned(self):
        return self.mentionned

if __name__ == '__main__':
    prompt = "Hello how are you ?\n"
    stream = AIStream('localhost:9999', 'ws://localhost:9999/api/v1/stream')
    asyncio.run(stream.print_response_stream(prompt))
