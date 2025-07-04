
from pyicub.rest import PyiCubRESTfulClient

robot_name = 'icubSim'
app_name = 'helper'

client = PyiCubRESTfulClient(host='localhost', port=9001)

res = client.run_target(robot_name, app_name, target_name='gpt.query', text='Tell me a fun fact about space.')
print("Set prompt result:", res)

res = client.run_target(robot_name, app_name, target_name='gpt.set_system_prompt',
                        prompt='You are a concise assistant who answers very briefly.')
print("Set prompt result:", res)

res = client.run_target(robot_name, app_name, target_name='gpt.create_session', session_id='rest-session')
print("Create session result:", res)

res = client.run_target(robot_name, app_name, target_name='gpt.switch_session', session_id='rest-session')
print("Switch session result:", res)

res = client.run_target(robot_name, app_name, target_name='gpt.query', text='Who is Alan Turing?')
print("Query result:", res)
