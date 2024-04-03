from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

import os
from dotenv import load_dotenv
load_dotenv()
# First, we create a EventHandler class to define
# how we want to handle the events in the response stream.

OPENAI_API_KEY= os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

assistant_id="asst_JaLwobkfgHziCOQ3gT5oLc6j" #Assistant Id

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="what is the capital of Nepal" #user query
)

class EventHandler(AssistantEventHandler):
  @override
  def on_text_created(self, text) -> None:
    print(f"\nassistant > ", end="", flush=True)

  @override
  def on_text_delta(self, delta, snapshot):
    print(delta.value, end="", flush=True)

  def on_tool_call_created(self, tool_call):
    print(f"\nassistant > {tool_call.type}\n", flush=True)

  def on_tool_call_delta(self, delta, snapshot):
    if delta.type == 'code_interpreter':
      if delta.code_interpreter.input:
        print(delta.code_interpreter.input, end="", flush=True)
      if delta.code_interpreter.outputs:
        print(f"\n\noutput >", flush=True)
        for output in delta.code_interpreter.outputs:
          if output.type == "logs":
            print(f"\n{output.logs}", flush=True)

# Then, we use the `create_and_stream` SDK helper
# with the `EventHandler` class to create the Run
# and stream the response.

with client.beta.threads.runs.create_and_stream(
  thread_id=thread.id,
  assistant_id=assistant_id,
  # instructions="Please address the user as Jane Doe. The user has a premium account.",
  event_handler=EventHandler(),
) as stream:
  stream.until_done()