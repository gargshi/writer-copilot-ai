document.addEventListener("DOMContentLoaded", function () {

	let configVars = {
		"SaveAfterEveryGeneration": true,
	}

	const editor = document.querySelector(".editor textarea");
	const status = document.querySelector(".stats.msg");
	const continueButton = document.querySelector("#continueBtn");
	const stopButton = document.querySelector("#stopBtn");
	const startButton = document.querySelector("#startBtn");
	continueButton.style.display = "inline-block";
	stopButton.style.display = "none";
	startButton.style.display = "inline-block";

	let controller = null;
	let currentRequestId = null;

	const test_data = {
		mainConflict: "a war is happening in a certain location.",
		protagonist: "we have a sniper positioned on a rooftop",
		openingScene: "he notices some activity on the road",
		wordsToGenerate: "300",
		storyType: "Short Story",
		storyPerson: "Third Person"
	};

	//load test values in the modal fields
	document.getElementById("mainConflict").value = test_data.mainConflict;
	document.getElementById("protagonist").value = test_data.protagonist;
	document.getElementById("openingScene").value = test_data.openingScene;
	document.getElementById("wordsToGenerate").value = test_data.wordsToGenerate;
	document.getElementById("storyType").value = test_data.storyType;
	document.getElementById("storyPerson").value = test_data.storyPerson;



	/* ---------------------------
	   WORD COUNT
	--------------------------- */

	editor.addEventListener("input", () => updateWordCount(editor.value));

	function updateWordCount(text) {
		if (!text) {
			document.getElementById("totalWords").innerText = 0;
			return;
		}

		const words = text.trim().split(/\s+/).filter(Boolean).length;
		document.getElementById("totalWords").innerText = words;
	}

	// UPDATE BUTTON VISIBILITY
	function updateButtonVisibility(isGenerating) {
		continueButton.disabled = isGenerating;
		stopButton.disabled = !isGenerating;
		startButton.disabled = isGenerating;
	}

	/* ---------------------------
	   MODAL
	--------------------------- */

	window.openModal = function () {
		document.body.style.overflow = "hidden";
		document.getElementById("ideaModal").style.display = "block";
	}

	window.closeModal = function () {
		document.body.style.overflow = "auto";
		document.getElementById("ideaModal").style.display = "none";
	}

	window.onclick = function (event) {
		const modal = document.getElementById("ideaModal");
		if (event.target === modal) closeModal();
	};


	// LOAD STORY INTO EDITOR

	window.loadDraft = async function (story_name) {
		try {
			const response = await fetch('/get_story', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ story_name })
			});

			const data = await response.json();
			if (data.status === "success") {
				editor.value = data.story;
				updateWordCount(editor.value);
				alert("Story fetched successfully!");
				getDrafts();
			}

		} catch (error) {

			console.error("Error loading story:", error);
			alert("Failed to load story.");

		}

	}

	/* ---------------------------
	   SAVE STORY
	--------------------------- */

	window.saveStory = async function () {

		const story = editor.value;

		if (!story.trim()) {
			alert("It seems you haven't written a story.");
			return;
		}

		try {

			const response = await fetch('/save_story', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ story })
			});

			const data = await response.json();
			if (data.status === "success") {
				setTimeout(() => status.innerText = "Story saved successfully!", 3000);
				alert("Story saved successfully!");
				setTimeout(() => status.innerText = "READY", 6000);
				getDrafts();
				// startButton.disabled = false;
				// continueButton.disabled = false;
				// stopButton.disabled = true;
				continueButton.style.display = "inline-block";
				stopButton.style.display = "none";
				startButton.style.display = "inline-block";
			}

		} catch (error) {

			console.error("Error saving story:", error);
			alert("Failed to save story.");

		}

	};

	window.checkGrammar = async function () {
		alert("This feature is not available yet. We are working on it.");
		// const story = editor.value;
		// const response = await fetch('/check_grammar', {
		// 	method: 'POST',
		// 	headers: {
		// 		'Content-Type': 'application/json'
		// 	},
		// 	body: JSON.stringify({ story })
		// });
		// const data = await response.json();
		// if (data.status === "success") {
		// 	editor.value = data.story;
		// 	updateWordCount(editor.value);
		// }
	}

	/* ---------------------------
	   GENERATE STORY (LLM)
	--------------------------- */

	window.sendDataToLLM = async function () {

		const mainConflict = document.getElementById("mainConflict").value || test_data.mainConflict;
		const protagonist = document.getElementById("protagonist").value || test_data.protagonist;
		const openingScene = document.getElementById("openingScene").value || test_data.openingScene;
		const wordsToGenerate = document.getElementById("wordsToGenerate").value || test_data.wordsToGenerate;
		const storyType = document.getElementById("storyType").value || test_data.storyType;
		const storyPerson = document.getElementById("storyPerson").value || test_data.storyPerson;

		/* Update sidebar */

		document.getElementById("mainConflictVal").innerText = mainConflict;
		document.getElementById("protagonistVal").innerText = protagonist;
		document.getElementById("openingSceneVal").innerText = openingScene;
		document.getElementById("wordsToGenerateVal").innerText = wordsToGenerate;
		document.getElementById("storyTypeVal").innerText = storyType;
		document.getElementById("storyPersonVal").innerText = storyPerson;

		controller = new AbortController();

		closeModal();

		try {
			// continueButton.disabled = true;
			// stopButton.disabled = false;
			// startButton.disabled = true;
			continueButton.style.display = "none";
			stopButton.style.display = "inline-block";
			startButton.style.display = "none";

			const response = await fetch('/send_data_to_llm', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					mainConflict,
					protagonist,
					openingScene,
					wordsToGenerate,
					storyType,
					storyPerson
				}),
				signal: controller.signal
			});

			if (!response.body) {
				throw new Error("Streaming not supported");
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			currentRequestId = response.headers.get("X-Request-ID");

			editor.value = "";

			status.innerText = "Generating story...";


			while (true) {

				const { done, value } = await reader.read();

				if (done) break;

				const chunk = decoder.decode(value, { stream: true });

				editor.value += chunk;
				editor.scrollTop = editor.scrollHeight;
				updateWordCount(editor.value);

			}
			await saveStory();

		} catch (error) {

			if (error.name === "AbortError") {
				console.log("⛔ Generation stopped");
				status.innerText = "Stopped";
			} else {
				console.error("AI continuation failed:", error);
				alert("Failed to continue story.");
				status.innerText = "READY";
			}
		}
	};

	window.continueWithAI = async function () {

		const storyTillNow = editor.value;

		if (!storyTillNow.trim()) {
			alert("It seems you haven't written a story.");
			return;
		}
		controller = new AbortController();

		try {

			// continueButton.disabled = true;
			// stopButton.disabled = false;
			// startButton.disabled = true;
			continueButton.style.display = "none";
			stopButton.style.display = "inline-block";
			startButton.style.display = "none";

			const response = await fetch('/continue_with_ai', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ storyTillNow }),
				signal: controller.signal
			});

			if (!response.body) {
				throw new Error("Streaming not supported");
			}

			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			currentRequestId = response.headers.get("X-Request-ID");

			editor.value += "\n - \n";

			status.innerText = "Generating story...";

			while (true) {

				const { done, value } = await reader.read();
				if (done) break;

				const chunk = decoder.decode(value, { stream: true });

				editor.value += chunk;
				editor.scrollTop = editor.scrollHeight;
				updateWordCount(editor.value);

			}
			if (configVars["SaveAfterEveryGeneration"])
			{
				await saveStory();
			}

		} catch (error) {

			if (error.name === "AbortError") {
				console.log("⛔ Generation stopped");
				status.innerText = "Stopped";
			} else {
				console.error("AI continuation failed:", error);
				alert("Failed to continue story.");
				status.innerText = "READY";
			}
		} finally {
			controller = null; // cleanup
		}

	};

	window.stopGeneration = async function () {

		// stop frontend
		if (controller) {
			controller.abort();
		}

		// spam check
		if (!currentRequestId) return;

		// 🔥 stop backend
		if (currentRequestId) {
			await fetch("/stop_generation", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify({
					request_id: currentRequestId
				})
			});
		}

		status.innerText = "Stopped";
		// startButton.disabled = false;
		// continueButton.disabled = false;
		// stopButton.disabled = true;
		continueButton.style.display = "inline-block";
		stopButton.style.display = "none";
		startButton.style.display = "inline-block";
	};

	/* ---------------------------
	   ACCORDION
	--------------------------- */

	document.querySelectorAll(".accordion-btn").forEach(button => {

		button.addEventListener("click", function () {

			const content = this.nextElementSibling;

			if (content.style.display === "block") {
				content.style.display = "none";
			} else {
				content.style.display = "block";
			}

		});

	});

	/* ---------------------------
	   DRAFTS
	--------------------------- */

	async function getDrafts() {

		try {

			const response = await fetch('/get_drafts');
			const data = await response.json();

			if (data.status !== "success") return;

			const draftList = document.getElementById("draftList");
			draftList.innerHTML = "";

			if (data.drafts.length === 0) {
				const item = document.createElement("div");
				item.className = "draft-item";
				item.innerHTML = `
							<p>No drafts found.</p>
						`;
				draftList.appendChild(item);
				return;
			}

			data.drafts.forEach(draft => {

				const item = document.createElement("div");
				item.className = "draft-item";

				item.innerHTML = `
							<a href="/drafts/${draft.name}">${draft.name}</a>
							<p>${draft["content-short"]}</p>
							<p>${draft["modified-at"]}</p>
							<div class="actions">
								<button class="btn btn-danger-sm" onclick="deleteDraft('${draft.name}')">Delete</button>
								<button class="btn btn-primary-sm" onclick="loadDraft('${draft.name}')">Load</button>
							</div>
						`;

				draftList.appendChild(item);

			});

		} catch (err) {

			console.error("Failed to load drafts:", err);

		}

	}

	getDrafts();

	/* ---------------------------
	   DELETE DRAFT
	--------------------------- */

	window.deleteDraft = async function (name) {

		if (!confirm("Delete this draft?")) return;

		await fetch(`/delete_draft/${name}`, { method: "DELETE" });

		getDrafts();

	};

});