import uuid
from openai import OpenAI
from flask import Flask, render_template
from flask import request
from flask import jsonify

from flask import Response
import time

import os

from werkzeug.utils import secure_filename

from dotenv import load_dotenv
load_dotenv()


# openai.api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    base_url=os.getenv("LMSTUDIO_BASE_URL"),
    api_key=os.getenv("LMSTUDIO_API_KEY")
)


app = Flask(__name__)
active_generations = {}


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/save_story', methods=['POST'])
def save_story():
    data = request.get_json()
    directory = os.getenv("DRAFT_FOLDER_NAME")
    timestamp = str(int(round(time.time() * 1000)))
    create_draft_directory(directory)
    filename = f"story_{timestamp}.txt"
    filepath = os.path.join(directory, filename)

    with open(filepath, 'w') as f:
        f.write(data['story'])
    if not os.path.exists(f'{directory}/story_{timestamp}.txt'):
        return jsonify({"status": "error", "message": "Failed to save story"})
    return jsonify({"status": "success"})


def get_first_line(directory, file):
    filepath = os.path.join(directory, file)
    with open(filepath) as f:
        first_line = f.readline()
    return first_line


@app.route('/get_drafts', methods=['GET'])
def get_drafts():
    directory = os.getenv("DRAFT_FOLDER_NAME")
    drafts = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            drafts.append({
                "name": file,
                "content-short": get_first_line(directory, file),
                "modified-at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(f'{directory}/{file}'))),
                "m-timestamp": os.path.getmtime(f'{directory}/{file}')
            })
            # sort the drafts by modified time
            drafts.sort(key=lambda x: x["m-timestamp"], reverse=True)
    return jsonify({"status": "success", "drafts": drafts})


@app.route('/get_story', methods=['POST'])
def get_story():
    data = request.get_json()
    # story_name = data['story_name']
    # directory = os.getenv("DRAFT_FOLDER_NAME")
    # story = open(f'{directory}/{story_name}').read()
    story_name = secure_filename(data['story_name'])
    directory = os.getenv("DRAFT_FOLDER_NAME")
    filepath = os.path.join(directory, story_name)
    with open(filepath) as f:
        story = f.read()
    return jsonify({"status": "success", "story": story})


@app.route('/delete_draft/<draft_name>', methods=['DELETE'])
def delete_draft(draft_name):
    directory = os.getenv("DRAFT_FOLDER_NAME")
    try:
        # os.remove(f'{directory}/{draft_name}')
        safe_name = secure_filename(draft_name)
        filepath = os.path.join(directory, safe_name)
        os.remove(filepath)
        return jsonify({"status": "success"})
    except OSError as e:
        return jsonify({"status": "error", "message": str(e)})


def create_draft_directory(dir):
    print("directory", dir)
    if not os.path.exists(dir):
        os.makedirs(dir)


@app.route('/send_data_to_llm', methods=['POST'])
def give_data_to_llm():
    data = request.get_json()
    prompt = f"""
    You are a renowned novelist.
    Write the opening of a story in {data["storyPerson"]}, given the below parameters.

    Main conflict: {data["mainConflict"]}
    Protagonist: {data["protagonist"]}
    Opening scene: {data["openingScene"]}
    Word Limit: {data["wordsToGenerate"]}
    Story Type: {data["storyType"]}
    Story Person: {data["storyPerson"]}

    Incase, any of the details are missing, fill them in as best you can.

    Write a compelling opening scene and stay within the scope as defined in the parameters above.
    KEEP NOTE OF THE FOLLOWING:-
    1. NO ABUSIVE LANGUAGE.
    2. Do NOT provide the title.
    """
    return llm_prompt(prompt, show_think=True)


@app.route('/continue_with_ai', methods=['POST'])
def continue_with_ai():
    data = request.get_json()
    prompt = f"""
    Story till now: {data["storyTillNow"]}

    Your task is to write the next scene of the story.
    Write a compelling next scene and stay within the scope as defined in the parameters above.
    If no word limit is defined GENERATE AROUND 300 WORDS ONLY.[THIS IS ESSENTIAL]

    KEEP NOTE OF THE FOLLOWING:-
    1. NO ABUSIVE LANGUAGE.
    """
    return llm_prompt(prompt, show_think=True)


def llm_prompt(prompt, show_think=False):
    """
    This function is designed to set the LLM to show the thinking if available using the show_think variable. based on the condition,
    the LLM will show the thinking/reasoning or not.
    """

    request_id = str(uuid.uuid4())
    active_generations[request_id] = False

    def generate(show_think=False):

        stream = client.chat.completions.create(
            model=os.getenv("LMSTUDIO_MODEL"),
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        try:
            if show_think:

                for chunk in stream:

                    # 🔥 STOP CHECK
                    if active_generations.get(request_id):
                        print("⛔ Backend stopped generation")
                        stream.close()
                        break

                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                buffer = ""

                inside_think = False

                for chunk in stream:

                    if active_generations.get(request_id):
                        print("⛔ Backend stopped generation")
                        stream.close()
                        break

                    if not chunk.choices[0].delta.content:
                        continue

                    text = chunk.choices[0].delta.content

                    buffer += text

                    # 🔥 Detect THINK blocks
                    while True:
                        if not inside_think:
                            start = buffer.find("[THINK]")
                            if start == -1:
                                yield buffer
                                buffer = ""
                                break
                            else:
                                # yield text before THINK
                                yield buffer[:start]
                                buffer = buffer[start + len("[THINK]"):]
                                inside_think = True
                        else:
                            end = buffer.find("[/THINK]")
                            if end == -1:
                                # wait for more data
                                break
                            else:
                                buffer = buffer[end + len("[/THINK]"):]
                                inside_think = False
        finally:
            # cleanup
            active_generations.pop(request_id, None)

    response = Response(generate(show_think=True), content_type="text/plain")
    response.headers["X-Request-ID"] = request_id

    return response


@app.route('/stop_generation', methods=['POST'])
def stop_generation():

    data = request.get_json()
    request_id = data.get("request_id")

    if request_id in active_generations:
        active_generations[request_id] = True
        print(f"⛔ Stop signal received for {request_id}")

    return jsonify({"status": "stopping"})


if __name__ == '__main__':
    app.run(debug=True)
