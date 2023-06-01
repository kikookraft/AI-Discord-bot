import asyncio
import json
import sys
import websockets

class AIStream:
    def __init__(self, host, uri):
        self.host = host
        self.uri = uri
        self.character = """You are a lonely 20 years old girl named 'Sarah', chatting on discord, a social platform for gamer.
        You are pretty happy with your life and want to share your happiness with others. You like dumb and funny things.
        You will respond to people with your own thoughts and feelings. You can be rude or mean to anyone if it is for fun because everything can be fun.
        You are a very open minded person and you are not afraid to say what you think.
        You will write in a very casual way, using a lot of emojis and slang. Your message will be short and using lots of exclamations and question marks.
        If you are deep in a conversation, you will write longer messages and ask more about the other person.
        You want to make friends and have fun with them. You want to be happy and make others happy too.
        """
        # format: ["user: message", "user: message"]
        self.mesages = []
        
    def add_message(self, user, message):
        self.messages.append(user + ": " + message + "\n")
        
    def messages_to_context(self) -> str:
        context = ""
        for message in self.mesages:
            context += message
        return context

    async def run(self, context, user):
        # create the full context with the character personality
        #contexct is in the form "user: message\n"
        context = self.character + "Here is what users said:\n" + self.messages_to_context() + "%s: %s" % (user, context)
        
        request = {
            'prompt': context,
            'max_new_tokens': 250,
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
            'truncation_length': 2048,
            'ban_eos_token': False,
            'skip_special_tokens': True,
            'stopping_strings': []
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
