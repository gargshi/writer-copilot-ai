import uuid
from openai import OpenAI
from flask import Flask, render_template
from flask import request, redirect, url_for,flash
from flask import jsonify

from flask import Response
import time

import os
import json

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

app.secret_key = os.getenv("APP_SECRET_KEY")


@app.route('/')
def sessions():
    return render_template('sessions.html')


@app.route('/story')
def story():
    return render_template('index.html')


def create_session_directory():
    sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
    if not os.path.exists(sess_dir):
        os.makedirs(sess_dir)


@app.route('/update_session', methods=['POST'])
def update_session():
    try:
        data = request.form
        print(data)
        timestamp = data['timestamp']
        sess_id = data['id']
        sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
        session_dict = {}
        with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'r') as f:
            session_dict = json.load(f)
        session_dict['session_name'] = data['name']
        session_dict['session_description'] = data['description']
        with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'w') as f:
            # convert session_dict to json
            json.dump(session_dict, f)
            flash("Session updated successfully!", "success")
    except Exception as e:
        print(e)
        flash("Error creating session", "error")
    
    return redirect(url_for('sessions'))


@app.route('/create_session', methods=['POST'])
def create_session():
    data = request.form
    print(data)
    timestamp = str(int(round(time.time() * 1000)))
    sess_id = str(uuid.uuid4())
    session_dict = {
        "session_id": sess_id,
        "timestamp": timestamp,
        "session_name": data['session_name'],
        "session_description": data['session_description']
    }
    create_session_directory()
    sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
    with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'w') as f:
        # convert session_dict to json
        json.dump(session_dict, f)
    flash("Session created successfully!", "success")
    return redirect(url_for('sessions'))


@app.route('/get_sessions', methods=['GET'])
def get_sessions():
    sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
    sessions = []
    # sort the sessions by timestamp
    sess_list=os.listdir(sess_dir)
    sess_list.sort(key=lambda x: os.path.getmtime(f'{sess_dir}/{x}'), reverse=True)
    for file in sess_list:
        if file.endswith(".json"):
            with open(os.path.join(sess_dir, file), 'r') as f:
                sessions.append(json.load(f))
    return jsonify({"status": "success", "sessions": sessions})

@app.route('/session/<id>', methods=['GET'])
def view_session(id):
    sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
    with open(os.path.join(sess_dir, f'session_{id}.json'), 'r') as f:
        session = json.load(f)
    return render_template('view_session.html', session=session)





@app.route('/delete_session', methods=['POST'])
def delete_session():
    try:
        data = request.get_json()
        print(data)
        sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
        filepath = os.path.join(sess_dir, f'session_{data["id"]}.json')
        os.remove(filepath)
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "success"})





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
    if not os.path.exists(directory):
        return jsonify({"status": "error", "message": "No drafts found"})
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
    # prompt = f"""
    # You are a renowned novelist.
    # Generate atmost 5 plotlines of a story in {data["storyPerson"]}, given the below parameters.

    # Main conflict: {data["mainConflict"]}
    # Protagonist: {data["protagonist"]}
    # Opening scene: {data["openingScene"]}
    # Word Limit: {data["wordsToGenerate"]}
    # Story Type: {data["storyType"]}
    # Story Person: {data["storyPerson"]}

    # Incase, any of the details are missing, fill them in as best you can.

    # Write a compelling opening scene and stay within the scope as defined in the parameters above.
    # KEEP NOTE OF THE FOLLOWING:-
    # 1. NO ABUSIVE LANGUAGE.
    # 2. Do NOT provide the title.
    # """
    prompt = f"""
        You are a renowned novelist and story architect.

        Your task is to generate up to 5 distinct and compelling plotlines based on the given inputs.

        Each plotline should:
        - Be 3–5 sentences long
        - Clearly describe the core idea, conflict, and direction of the story
        - Be unique from the others (no repetition or minor variations)
        - Be engaging and imaginative

        Inputs:
        Main conflict: {data["mainConflict"]}
        Protagonist: {data["protagonist"]}
        Opening scene: {data["openingScene"]}
        Story Type: {data["storyType"]}
        Narration Style (Person): {data["storyPerson"]}

        Instructions:
        - If any detail is missing, creatively fill in the gaps
        - Do NOT write full scenes or dialogues
        - Do NOT include a title
        - Do NOT use abusive or inappropriate language
        - Focus only on high-level story ideas (plotlines)

        Return in STRICTLY valid  JSON Format as below:
        [
            {{
                "title": "Plotline 1",
                "core_idea": "...",
                "protagonist": "...",
                "conflict": "...",
                "stakes": "...",
                "direction": "..."
            }},
            {{
                "title": "Plotline 2",
                "core_idea": "...",
                "protagonist": "...",
                "conflict": "...",
                "stakes": "...",
                "direction": "..."
            }},
            {{
                "title": "Plotline 3",
                "core_idea": "...",
                "protagonist": "...",
                "conflict": "...",
                "stakes": "...",
                "direction": "..."
            }},
            ...
        ]

        Rules:
        - Do NOT include markdown (** or -)
        - Do NOT include explanations
        - Do NOT include text outside JSON
        - Ensure valid JSON syntax
        ...

        Keep the response concise and structured.
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

