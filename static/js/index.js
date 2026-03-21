document.addEventListener("DOMContentLoaded", function () {

	let configVars = {
		"SaveAfterEveryGeneration": true,
	}

	const editor = document.querySelector(".editor textarea");
	const status = document.querySelector(".stats.msg");
	const continueButton = document.querySelector("#continueBtn");
	const stopButton = document.querySelector("#stopBtn");
	const startButton = document.querySelector("#startBtn");
	const plotModal = document.querySelector("#plotModal");
	let plotsTextfromAI = "";
	let plots = [];
	let useCachedPlots = !true;
	continueButton.style.display = "inline-block";
	stopButton.style.display = "none";
	startButton.style.display = "inline-block";

	function isEditorEmpty() {
		return !editor.value.trim();
	}

	// Initially disable continue button if editor empty
	if (isEditorEmpty()) {
		continueButton.disabled = true;
		continueButton.style.display = "none";
	}

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

	editor.addEventListener("input", () => {
		updateWordCount(editor.value);
		// Disable continue button if editor empty
		continueButton.disabled = isEditorEmpty();
		continueButton.style.display = isEditorEmpty() ? "none" : "inline-block";
	});

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
		continueButton.disabled = isGenerating || isEditorEmpty();
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

	window.closeModal = function (el) {
		document.body.style.overflow = "auto";

		const modal = el.closest(".modal");
		if (modal) {
			modal.style.display = "none";
		}
	}

	// window.onclick = function (event) {
	// 	const modal = document.getElementById("ideaModal");
	// 	if (event.target === modal) closeModal();
	// };
	window.onclick = function (event) {
		if (event.target.classList.contains("modal")) {
			document.body.style.overflow = "auto";
			event.target.style.display = "none";

			console.log("Closed modal:", event.target.id);
		}
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

	window.sendDataToLLM = async function (generatePlots = false, el = null) {

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

		closeModal(el);

		try {
			// continueButton.disabled = true;
			// stopButton.disabled = false;
			// startButton.disabled = true;
			continueButton.style.display = "none";
			stopButton.style.display = "inline-block";
			startButton.style.display = "none";

			if (useCachedPlots) {
				await populatePlots();
				return;
			}


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

			status.innerText = (!generatePlots) ? "Generating Story..." : "Generating Plots... Please wait...";


			while (true) {

				const { done, value } = await reader.read();

				if (done) break;

				const chunk = decoder.decode(value, { stream: true });

				if (!generatePlots) {
					editor.value += chunk;
					editor.scrollTop = editor.scrollHeight;
					updateWordCount(editor.value);
				}

				plotsTextfromAI += chunk;
				// plots = plotsTextfromAI.split("\n\n");
			}
			if (!generatePlots) {
				await saveStory();
				return;
			}
			await populatePlots();

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

	window.populatePlots = async function () {
		const plotsDiv = document.getElementById("plotSuggestions");
		plotsDiv.innerHTML = "";
		plots = plotsTextfromAI.trim();
		// console.log(plots);
		plots = useCachedPlots ? JSON.parse(localStorage.getItem("plots")) : plots;
		if (!useCachedPlots) {
			localStorage.setItem("plots", JSON.stringify(plots));
		}

		console.log(plots.match(/{[\s\S]*?}/g));

		plots = plots
			.match(/{[\s\S]*?}/g)
			.map(obj => {
				let fixed = obj
					.replace(/\\n/g, "")
					.replace(/:\s*([^",\{\}\[\]]+)(?=,|\})/g, (match, p1) => {
						return ': "' + p1.trim() + '"';
					});
				console.log(fixed);

				return JSON.parse(fixed);
			});

		// console.log(plots);

		for (let i = 0; i < plots.length; i++) {
			const plot = plots[i];
			const plotDiv = document.createElement("div");
			plotDiv.classList.add("plot");
			plotDiv.innerHTML = `
				<h3>${plot.title}</h3>
				<h4>Core Idea</h4>
				<p>${plot.core_idea}</p>
				<h4>Protagonist</h4>
				<p>${plot.protagonist}</p>
				<h4>Conflict</h4>
				<p>${plot.conflict}</p>
				<h4>Stakes</h4>
				<p>${plot.stakes}</p>
				<h4>Direction</h4>
				<p>${plot.direction}</p>
			`;
			plotDiv.addEventListener("click", function () {
				plotModal.style.display = "block";
				plotModal.querySelector(".modal-content .modal-body").innerHTML = `
					<h3>${plot.title}</h3>
					<h4>Core Idea</h4>
					<p>${plot.core_idea}</p>
					<h4>Protagonist</h4>
					<p>${plot.protagonist}</p>
					<h4>Conflict</h4>
					<p>${plot.conflict}</p>
					<h4>Stakes</h4>
					<p>${plot.stakes}</p>
					<h4>Direction</h4>
					<p>${plot.direction}</p>
				`;
			})
			plotsDiv.appendChild(plotDiv);
		}

		// Everything below runs AFTER loop finishes
		// await new Promise(resolve => setTimeout(resolve, 6000));

		status.innerText = "READY";

		getDrafts();

		stopButton.style.display = "none";
		startButton.style.display = "inline-block";
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
			if (configVars["SaveAfterEveryGeneration"]) {
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