import uuid
from openai import OpenAI
from flask import Flask, render_template
from flask import request, redirect, url_for, flash
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

PLOT_DIR=os.getenv("PLOT_FOLDER_NAME")
DRAFTS_DIR=os.getenv("DRAFT_FOLDER_NAME")
def create_plot_directory():
	try:
		current_dir = os.getcwd()
		if not os.path.exists(os.path.join(current_dir, PLOT_DIR)):
			os.makedirs(os.path.join(current_dir, PLOT_DIR))
	except Exception as e:
		print("Error : ",e)

def create_drafts_directory():
	try:
		current_dir = os.getcwd()
		drafts_dir = os.path.join(current_dir, DRAFTS_DIR)
		if not os.path.exists(drafts_dir):
			os.makedirs(drafts_dir)
	except Exception as e:
		print("Error : ",e)

create_plot_directory()
create_drafts_directory()

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


def create_key(key, session):
	session[key] = 'abc'


@app.route('/update_session', methods=['POST'])
def update_session():
	try:
		data = request.form
		if not request.form:
			data = request.get_json()
		print("received_data",data)
		sess_id = data['id']
		print("Session id :", sess_id)
		sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
		session_dict = {}
		with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'r') as f:
			session_dict = json.load(f)
		fields = data.keys()
		print("fields",fields)
		session_dict['session_name'] = data['name'] if 'name' in fields else session_dict['session_name']
		session_dict['session_description'] = data['description'] if 'description' in fields else session_dict['session_description']
		if 'story_params' not in session_dict.keys():
			session_dict['story_params'] = {}
		session_dict['story_params'] = json.loads(
			data['story_params']) if 'story_params' in fields else session_dict['story_params']
		# if 'generated_plot' not in session_dict['plots'].keys():
		# 	session_dict['plots']['generated']=[]
		# session_dict['plots']['generated'].append(json.loads(data['generated_plot']))

		if 'used_plot_id' in fields:
			session_dict['plots']['used'] = data['used_plot_id']

		if 'available_plot' in fields:
			print("""available plot""")
			plot = json.loads(data['available_plot'])
			print("fetched plot",plot)

			# check duplicates based on content
			exists = any(
				existing['plot'] == plot
				for existing in session_dict['plots']['available']
			)

			if not exists:
				plot_dict={
					"plot_id": str(uuid.uuid4()),  # convert to string
					"plot": plot
				}
				session_dict['plots']['available'].append(plot_dict)
				add_plot_to_directory(plot_dict)

		if 'rejected_plot_id' in fields:
			pid = data['rejected_plot_id']           
			
			session_dict['plots']['available'] = [
				p for p in session_dict['plots']['available']
				if p['plot_id'] != pid
			]
			delete_plot_in_directory(pid)

			session_dict['plots']['used'] = "" if session_dict['plots']['used'] == pid else session_dict['plots']['used']
		
		if 'rejected_story_draft_id' in fields:
			did = data['rejected_story_draft_id']
			print(did)
			session_dict['generated_drafts'] = [
				draft_id for draft_id in session_dict['generated_drafts']
				if draft_id != did
			]
			delete_draft_in_directory(did)			
			print(session_dict['generated_drafts'])

		if 'story' in fields:
			draft_id=str(uuid.uuid4())
			draft={
				"draft_id":draft_id,
				"timestamp": str(int(round(time.time() * 1000))),
				"plot": {
					"core_idea": data['core_idea'],
					"protagonist": data['protagonist'],
					"conflict": data['conflict'],
					"stakes": data['stakes'],
					"direction": data['direction'],
					"rough_story_timeline": data['roughStoryTimeline'],
				},
				"draft_title": data['storyTitle'],
				"story": data['story'],
			}
			session_dict['generated_drafts'].append(draft_id)
			create_draft_in_directory(draft)
		
		if 'mode' in fields and data['mode'] == "character":
			print("Updating characters")
			if 'add_char' in fields:
				print("Adding character")
				character = json.loads(data['add_char'])
				session_dict['characters'].append({
					"id": str(uuid.uuid4()),
					"name": character['name'],
					"role": character['role'],
					"personality": character['personality'],
					"description": character['description'],
					"appearance": character['appearance'],
					"background": character['background']
				}) # add characters
			elif 'delete_char_id' in fields:				
				char_id = data['delete_char_id']
				print("Character id to delete:", char_id)
				session_dict['characters'] = [
					c for c in session_dict['characters']
					if c['id'] != char_id
				]
				print("Remaining characters:", session_dict['characters'])
			elif 'update_char_id' in fields:
				char_id = data['update_char_id']
				character = json.loads(data['update_char'])
				up_character = {
					"id": char_id,
					"name": character['name'],
					"role": character['role'],
					"personality": character['personality'],
					"description": character['description'],
					"appearance": character['appearance'],
					"background": character['background']
				}
				session_dict['characters'] = [
					c if c['id'] != char_id else up_character
					for c in session_dict['characters']
				]


		with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'w') as f:
			# convert session_dict to json
			json.dump(session_dict, f)
			flash("Session updated successfully!", "success")
	except Exception as e:
		print(e)
		flash("Error creating session", "error")

	return redirect(url_for('view_session', id=sess_id))


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
		"session_description": data['session_description'],
		"plots": {
			"available": [],
			"used": "",
			"saved": []
		},
		"characters": [],
		"story_params": {
			"mainConflict": "",
			"protagonist": "",
			"openingScene": "",
			"wordsToGenerate": "",
			"storyType": "",
			"storyPerson": "",
			"noOfPlots": "",
		},
		"generated_drafts": []
	}
	create_session_directory()
	sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
	with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'w') as f:
		# convert session_dict to json
		json.dump(session_dict, f)
	flash("Session created successfully!", "success")
	return redirect(url_for('sessions'))

# Plot handling
def add_plot_to_directory(plot):
	try:
		current_dir = os.getcwd()
		with open(os.path.join(current_dir, PLOT_DIR, f'plot_{plot["plot_id"]}.json'), 'w') as f:
			json.dump(plot, f)
	except Exception as e:
		print("Error : ",e)

def fetch_plot_from_directory(plot_id):
	try:
		current_dir = os.getcwd()
		with open(os.path.join(current_dir, PLOT_DIR, f'plot_{plot_id}.json'), 'r') as f:
			plot = json.load(f)
		return plot
	except Exception as e:
		print("Error : ",e)
		return

def update_plot_in_directory(plot_id, plot):
	try:
		current_dir = os.getcwd()
		with open(os.path.join(current_dir, PLOT_DIR, f'plot_{plot_id}.json'), 'w') as f:
			json.dump(plot, f)
		return
	except Exception as e:
		print("Error : ",e)
		return

def get_all_plots():
	try:
		current_dir = os.getcwd()
		plots = []
		for file in os.listdir(os.path.join(current_dir, PLOT_DIR)):
			with open(os.path.join(current_dir, PLOT_DIR, file), 'r') as f:
				plot = json.load(f)
				plots.append(plot)
		return plots
	except Exception as e:
		print("Error : ",e)
		return

def delete_plot_in_directory(plot_id):
	try:
		current_dir = os.getcwd()
		os.remove(os.path.join(current_dir, PLOT_DIR, f'plot_{plot_id}.json'))
	except Exception as e:
		print("Error : ",e)
	return

@app.route("/plots/", methods=['GET', 'POST'])
def plot_handler():
    try:
        if request.method == 'GET':
            plots = get_all_plots()
            return jsonify(plots)

        elif request.method == 'POST':
            plot = request.json
            add_plot_to_directory(plot)
            return jsonify({"status": "created"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error"})

@app.route("/plots/<plot_id>", methods=['PUT', 'DELETE'])
def plot_detail_handler(plot_id):
    try:
        if request.method == 'PUT':
            plot = request.json
            update_plot_in_directory(plot_id, plot)
            return jsonify({"status": "updated"})

        elif request.method == 'DELETE':
            delete_plot_in_directory(plot_id)
            return jsonify({"status": "deleted"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error"})

# Draft handling
def create_draft_in_directory(draft):
	try:
		current_dir = os.getcwd()
		if not os.path.exists(os.path.join(current_dir, DRAFTS_DIR)):
			os.makedirs(os.path.join(current_dir, DRAFTS_DIR))
		with open(os.path.join(current_dir, DRAFTS_DIR, f'draft_{draft["draft_id"]}.json'), 'w') as f:
			json.dump(draft, f)
	except Exception as e:
		print("Error : ",e)

def get_all_drafts():
	try:
		current_dir = os.getcwd()
		drafts = []
		for file in os.listdir(os.path.join(current_dir, DRAFTS_DIR)):
			with open(os.path.join(current_dir, DRAFTS_DIR, file), 'r') as f:
				draft = json.load(f)
				drafts.append(draft)
		return drafts
	except Exception as e:
		print("Error : ",e)
		return

def delete_draft_in_directory(draft_id):
	try:
		current_dir = os.getcwd()
		filepath=os.path.join(current_dir, DRAFTS_DIR, f'draft_{draft_id}.json')
		if os.path.exists(filepath):
			os.remove(filepath)
	except Exception as e:
		print("Error : ",e)

def fetch_draft_from_directory(draft_id):
	try:
		current_dir = os.getcwd()
		filepath=os.path.join(current_dir, DRAFTS_DIR, f'draft_{draft_id}.json')
		if not os.path.exists(filepath):
			return
		with open(filepath, 'r') as f:
			draft = json.load(f)
		return draft
	except Exception as e:
		print("Error : ",e)
		return

def update_draft_in_directory(draft_id, draft):
	try:
		current_dir = os.getcwd()
		with open(os.path.join(current_dir, DRAFTS_DIR, f'draft_{draft_id}.json'), 'w') as f:
			json.dump(draft, f)
	except Exception as e:
		print("Error : ",e)

@app.route('/drafts/', methods=['GET','POST'])
def drafts_handler():
	try:
		if request.method == 'POST':
			draft = request.json
			create_draft_in_directory(draft)
			return jsonify({"status": "created"})
		
		elif request.method == 'GET':
			if request.args.get('id'):
				''' To get all drafts for a session '''
				print("recieved id=",request.args.get('id'))
				sess_id = request.args.get('id')
				sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
				with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'r') as f:
					session = json.load(f)
				draft_ids=session['generated_drafts'] # get draft ids from session			
				drafts = []
				for draft_id in draft_ids:
					draft = fetch_draft_from_directory(draft_id)
					drafts.append(draft)
				return jsonify({"status": "success", "drafts": drafts}) # return all drafts for a session
			drafts = get_all_drafts()
			return jsonify(drafts)

	except Exception as e:
		print("Error:", e)
		return jsonify({"status": "error"})

@app.route('/drafts/<draft_id>', methods=['GET','PUT', 'DELETE'])
def draft_detail_handler(draft_id):
	try:
		if request.method == 'GET':
			draft = fetch_draft_from_directory(draft_id)
			return jsonify(draft)
		
		elif request.method == 'PUT':
			draft = request.json
			update_draft_in_directory(draft_id, draft)
			return jsonify({"status": "updated"})
		
		elif request.method == 'DELETE':
			delete_draft_in_directory(draft_id)
			return jsonify({"status": "deleted"})

	except Exception as e:
		print("Error:", e)
		return jsonify({"status": "error"})



@app.route('/get_sessions', methods=['GET'])
def get_sessions():
	sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
	sessions = []
	# sort the sessions by timestamp
	sess_list = os.listdir(sess_dir)
	sess_list.sort(key=lambda x: os.path.getmtime(
		f'{sess_dir}/{x}'), reverse=True)
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
	plots_from_session = session['plots']
	plots = {
		"available": [],
		"used": {},
		"saved": []
	}

	if plots_from_session['available'] != []:
		for plot in plots_from_session['available']:
			plots['available'].append(plot)

	if plots_from_session['used'] != "":
		for plot in plots_from_session['available']:
			if plot['plot_id'] == plots_from_session['used']:
				plots['used'] = plot

	if plots_from_session['saved'] != []:
		for plot in plots_from_session['saved']:
			plots['saved'].append({
				"plot_id": plot['plot_id'],
				"plot": plots_from_session['available'][plot['plot_id']]
			})

	print(plots)
	print("SESSION DATA")
	print(session.keys())
	print(len(session))
	print("SESSION DATA-END")

	return render_template('view_session.html', session=session, plots=plots)


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

@app.route('/get_plots', methods=['GET'])
def get_plots():
	sess_id = request.args.get('id')
	sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
	with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'r') as f:
		session = json.load(f)
	return jsonify({"status": "success", "plots": session['plots']})

#@app.route('/get_story_drafts', methods=['GET'])
def get_story_drafts():
	sess_id = request.args.get('id')
	sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
	with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'r') as f:
		session = json.load(f)
	drafts=[]
	for draft in session['generated_drafts']:
		fetched_draft=fetch_draft_from_directory(draft)
		drafts.append({
			"draft_id": draft['draft_id'],
			"draft": draft['draft']
		})
				
	return jsonify({"status": "success", "story_drafts": session['generated_drafts']})

@app.route('/get_characters', methods=['GET'])
def get_characters():
	sess_id = request.args.get('id')
	sess_dir = os.getenv("STORY_SESSIONS_FOLDER_NAME")
	with open(os.path.join(sess_dir, f'session_{sess_id}.json'), 'r') as f:
		session = json.load(f)
	return jsonify({"status": "success", "characters": session['characters']})

@app.route('/send_data_to_llm', methods=['POST'])
def give_data_to_llm():
	data = request.get_json()
	print(data)
	if not data:
		return jsonify({"status": "error", "message": "No data provided"})
	if data['generate'] == "plots":
		prompt = f"""
			You are an expert story architect.

			Task:
			Generate EXACTLY {data["noOfPlots"]} unique plotlines based on the inputs.

			Each plotline must contain:
			- core_idea: 3–5 sentences describing the premise
			- protagonist: who they are
			- conflict: central struggle
			- stakes: what is at risk
			- direction: where the story is heading
			- rough_story_timeline: a brief outline of the story's progression from start to finish

			Requirements:
			- All plotlines must be clearly different
			- Do not repeat or rephrase ideas
			- Be imaginative but concise
			- Fill missing details creatively

			Inputs:
			Main conflict: {data["mainConflict"]}
			Protagonist: {data["protagonist"]}
			Opening scene: {data["openingScene"]}
			Story Type: {data["storyType"]}
			Narration Style: {data["storyPerson"]}

			Output:
			Return ONLY a valid JSON array with EXACTLY {data["noOfPlots"]} objects.

			Schema (STRICT):
			[
			{{
					"title": "Plotline 1",
					"core_idea": "string",
					"protagonist": "string",
					"conflict": "string",
					"stakes": "string",
					"direction": "string",
					"rough_story_timeline": "string"
			}}
			]

			Field constraints:
			- All values MUST be plain strings
			- Do NOT return nested objects or arrays
			- Do NOT use lists, bullet points, or special formatting inside values

			Critical Rules:
			- Output ONLY JSON (no text before or after)
			- Start response with '[' and end with ']'
			- Use double quotes for all keys and values
			- Do NOT include trailing commas
			- Titles MUST be sequential: "Plotline 1", "Plotline 2", ..., "Plotline {data["noOfPlots"]}"
			- Generate EXACTLY {data["noOfPlots"]} objects (no more, no less)
			- Do not truncate output

			Quality Rules:
			- Avoid repetition of ideas or phrases
			- Each paragraph MUST introduce new information or escalation
			- Prefer specific, observable details over abstract statements
			- Replace vague phrases like "something was wrong" with concrete anomalies
				"""
	elif data['generate'] == "story":
		prompt = f"""
			You are an expert story architect.

			Task:
			Generate an opening story scene STRICTLY based on the provided inputs.

			Requirements:
			- You MUST use ONLY the characters provided in "Available Characters"
			- You MUST use the exact protagonist name provided
			- You MUST NOT create new named characters unless absolutely unavoidable (e.g., crowd, guard, etc. without naming them)
			- If additional presence is needed, refer to them generically (e.g., "a guard", "a student")
			- You MUST NOT change character names, roles, relationships, or traits
			- You MUST preserve the tone, conflict, and direction described
			- Expand the given idea into a full scene without altering its essence
			- Stay faithful to the rough story timeline while enriching details

			Inputs:
			Main conflict: {data["mainConflict"]}
			Protagonist: {data["protagonist"]}
			Core idea: {data["core_idea"]}
			Conflict: {data["conflict"]}
			Stakes: {data["stakes"]}
			Direction: {data["direction"]}
			Available Characters: {data["characters"]}
			Words to Generate: {data["wordsToGenerate"]}
			Story Type: {data["storyType"]}
			Narration Style: {data["storyPerson"]}
			Rough story timeline: {data["roughStoryTimeline"]}

			Output:
			Return ONLY a valid JSON object as per the schema below.

			Schema (STRICT):
			{{
				"story": "string"
			}}

			Field constraints:
			- All values MUST be plain strings
			- Do NOT return nested objects or arrays
			- Do NOT use lists, bullet points, or special formatting inside values

			Critical Rules:
			- Output ONLY JSON (no text before or after)
			- Start response with '{{' and end with '}}'
			- Use double quotes for all keys and values
			- Do NOT include trailing commas
			- Do NOT change input facts (names, places, roles)

			Scene Fidelity Rules (MANDATORY):
			- The opening scene MUST begin EXACTLY in the location described in "Opening scene"
			- The first paragraph MUST visually establish the environment before introducing events
			- The inciting anomaly MUST occur within the scene
			- DO NOT jump to news, aftermath, or large-scale consequences

			Character Usage Rules (MANDATORY):
			- The protagonist MUST appear in the scene
			- At least one additional character from "Available Characters" SHOULD be used if contextually relevant
			- Character actions MUST align with their defined traits/background
			- Do NOT introduce contradictions in behavior

			Causality Rules:
			- Establish a clear cause-effect link between the protagonist’s actions and the anomaly
			- If unclear, subtly hint at the connection within the scene

			Pacing Rules:
			- Focus ONLY on the first critical moment
			- Do NOT resolve the conflict
			- Do NOT escalate to global stakes
			- Follow: observation → anomaly → realization

			Quality Rules:
			- Avoid repetition
			- Each paragraph MUST add new information or escalation
			- Use concrete sensory details instead of vague statements
			- Do NOT restate previously established information unless adding new insight
			- Each paragraph MUST introduce new progression, not rephrasing

			Self-Check (MANDATORY before final output):
			- Does the scene start in the correct location?
			- Are ONLY provided characters used?
			- Is there a clear cause-effect progression?
			- Is pacing limited to a single scene?

			If any answer is NO, revise before output.
		"""
	elif data['generate'] == "continue":
		prompt = f"""
			You are an expert story writer continuing an existing narrative.

			Task:
			Continue the story seamlessly from where it left off.

			Requirements:
			- You MUST continue from the last line of the provided story
			- You MUST NOT restart, summarize, or rewrite earlier parts
			- You MUST preserve tone, pacing, and narrative style
			- You MUST maintain character consistency (names, traits, roles)
			- You MUST NOT introduce contradictions
			- You MUST NOT deviate from the Rough story timeline provided
			- You MUST maintain coherence with the existing plot

			Character Rules (MANDATORY):
			- You MUST use ONLY characters from "Available Characters"
			- You MUST NOT introduce new named characters
			- If additional presence is required, use generic references (e.g., "a guard", "a villager")
			- Existing characters MUST behave according to their defined traits and roles
			- You MUST NOT alter relationships or prior character developments

			Inputs:
			Story so far:
			{data["currentStory"]}

			Available Characters:
			{data["characters"]}

			Words to Generate: {data["wordsToGenerate"]}
			Story Type: {data["storyType"]}
			Narration Style: {data["storyPerson"]}
			Rough story timeline: {data["roughStoryTimeline"]}

			Output:
			Return ONLY a valid JSON object as per the schema below.

			Schema (STRICT):
			{{
				"continuation": "string"
			}}

			Field constraints:
			- Value MUST be a plain string
			- No lists, no formatting, no markdown

			Critical Rules:
			- Output ONLY JSON (no text before or after)
			- Start with '{{' and end with '}}'
			- Do NOT repeat previous story unless absolutely necessary for flow
			- Continue directly from the last sentence
			- Do not truncate output

			Continuity Rules (MANDATORY):
			- You MUST preserve:
			- current physical setting
			- last active action in progress
			- emotional state of protagonist
			- You MUST continue from the EXACT last action, not a general situation
			- The first paragraph MUST directly follow the last sentence logically

			Causality Rules:
			- Every new action MUST be a direct consequence of the previous action
			- No time skips unless explicitly implied in the last line
			- Maintain tight cause-effect chaining

			Pacing Rules:
			- Continue within the SAME scene unless a transition is explicitly triggered
			- Do NOT jump to resolution or large-scale consequences
			- Build progression through: action → reaction → realization

			Quality Rules:
			- Avoid repetition
			- Each paragraph MUST introduce new movement, detail, or escalation
			- Use concrete sensory details instead of vague phrasing
			- Do NOT restate previously established information unless adding new insight
			- Each paragraph MUST introduce new progression, not rephrasing

			Self-Check (MANDATORY before final output):
			- Are ONLY provided characters used?
			- Does the continuation begin exactly where the last line ends?
			- Is the cause-effect chain intact?
			- Are character behaviors consistent?

			If any answer is NO, revise before output.

			Before writing, internally determine:
			- last action taken
			- immediate consequence
			- next logical action

			Then continue.

		"""
	elif data['generate'] == 'character':
		conflict = data.get("conflict", "Unknown conflict")
		stakes = data.get("stakes", "Unknown stakes")
		direction = data.get("direction", "Unknown direction")
		roughStoryTimeline = data.get("roughStoryTimeline", "Unknown timeline")
		prompt = f"""
			You are an expert character designer for narrative storytelling.

			Task:
			Generate a list of characters STRICTLY based on the provided plot.

			You MUST assign roles dynamically based on the story (protagonist, antagonist, supporting, mentor, etc.).
			Do NOT force generic roles — derive them from the plot context.

			Requirements:
			- Characters MUST feel grounded in the plot
			- Each character must have a clear narrative purpose
			- Avoid redundancy (no duplicate personalities or roles)
			- Ensure diversity in behavior, motivation, and perspective
			- Roles must emerge logically from conflict and stakes

			Inputs:			
			Conflict: {conflict}
			Stakes: {stakes}
			Direction: {direction}
			Rough story timeline: {roughStoryTimeline}

			Output:
			Return ONLY a valid JSON array.

			Schema (STRICT):
			[
			{{
				"name": "string",
				"role": "string",
				"personality": "string",
				"description": "string",
				"appearance": "string",
				"background": "string"
			}}
			]

			Field rules:
			- "role" MUST reflect story function (e.g., protagonist, antagonist, ally, mentor, rival, etc.)
			- "personality" must describe behavioral traits (not backstory)
			- "description" must explain what they do in the story
			- "appearance" must be physical and visual only
			- "background" must explain past relevant to current story

			Critical Rules:
			- Output ONLY JSON (no text before or after)
			- Start with '[' and end with ']'
			- Use double quotes for all keys and values
			- Do NOT include trailing commas
			- Do NOT return nested objects or arrays
			- Do NOT include markdown or formatting

			Narrative Integrity Rules:
			- The protagonist MUST be present and consistent with input
			- The antagonist MUST directly relate to the central conflict
			- Supporting characters MUST connect to either protagonist or conflict
			- Each character must influence the story direction

			Quality Rules:
			- Avoid vague traits like "mysterious" without context
			- Prefer specific behavioral and visual details
			- Ensure each character adds new narrative value

			Self-check before output:
			- Does each character serve a clear role?
			- Are roles logically derived from the plot?
			- Is there any redundancy?

			If yes, refine before output.
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

					# STOP CHECK
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

					# Detect THINK blocks
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

	response = Response(generate(show_think=show_think), content_type="text/plain")
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
