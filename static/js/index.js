const themeSelect = document.getElementById("themeSelect");
const selected = themeSelect.querySelector(".selected");
const options = themeSelect.querySelector(".options");
const lmstudioStatusEl = document.getElementById("lmstudioStatus");
const glassDock = document.querySelector(".glass-dock");
const dockModeToggle = document.getElementById("dockModeToggle");

// Toggle dropdown
selected.onclick = () => {
	themeSelect.classList.toggle("open");
};

// Select option
options.querySelectorAll("div").forEach(opt => {
	opt.onclick = () => {
		const value = opt.dataset.value;
		const label = opt.innerText;

		selected.innerText = label;
		themeSelect.classList.remove("open");

		// 🔥 Use your existing function
		changeTheme(value);

		// Save preference
		localStorage.setItem("theme", value);
	};
});

// Close on outside click
document.addEventListener("click", (e) => {
	if (!themeSelect.contains(e.target)) {
		themeSelect.classList.remove("open");
	}
});
function changeTheme(theme) {
	document.documentElement.setAttribute("data-theme", theme);
	localStorage.setItem("theme", theme);

	// 🔥 Update UI label manually
	const labels = {
		"light": "Light",
		"dark": "Dark",
		"dark-blue": "Dark Blue"
	};


	const selected = themeSelect.querySelector(".selected");
	if (selected) {
		selected.innerText = labels[theme] || theme;
	}
	const options = themeSelect.querySelectorAll(".options div");

	options.forEach(opt => {
		opt.classList.remove("active");
		if (opt.dataset.value === theme) {
			opt.classList.add("active");
		}
	});
}
(function () {
	const saved = localStorage.getItem("theme") || "dark";
	changeTheme(saved);
})();


async function refreshLMStudioStatus() {
	if (!lmstudioStatusEl) return;

	lmstudioStatusEl.classList.remove("status-loaded", "status-error", "status-loading");
	lmstudioStatusEl.classList.add("status-checking");

	const label = lmstudioStatusEl.querySelector(".lmstudio-status-text");
	label.textContent = "LM Studio: Checking";
	lmstudioStatusEl.title = "Checking LM Studio status";

	try {
		const response = await fetch("/lmstudio/load_model");
		if (!response.ok) {
			throw new Error(`Status request failed with ${response.status}`);
		}

		const data = await response.json();
		const state = data.model_state || {};
		const model = state.model || "unknown";

		lmstudioStatusEl.classList.remove("status-checking", "status-loaded", "status-error", "status-loading");

		if (state.loaded) {
			lmstudioStatusEl.classList.add("status-loaded");
			label.textContent = `LM Studio: Loaded`;
			lmstudioStatusEl.title = `Loaded model: ${model}`;
			return;
		}

		if (state.status === "loading") {
			lmstudioStatusEl.classList.add("status-loading");
			label.textContent = "LM Studio: Loading";
			lmstudioStatusEl.title = `Loading model: ${model}`;
			return;
		}

		lmstudioStatusEl.classList.add("status-error");
		label.textContent = "LM Studio: Offline";
		lmstudioStatusEl.title = state.error
			? `LM Studio error: ${state.error}`
			: `Model not loaded: ${model}`;
	} catch (error) {
		lmstudioStatusEl.classList.remove("status-checking", "status-loaded", "status-loading");
		lmstudioStatusEl.classList.add("status-error");
		label.textContent = "LM Studio: Offline";
		lmstudioStatusEl.title = `LM Studio status unavailable: ${error.message}`;
	}
}

refreshLMStudioStatus();


function applyDockMode(mode) {
	if (!glassDock || !dockModeToggle) return;

	const compact = mode === "compact";
	glassDock.classList.toggle("compact-dock", compact);
	dockModeToggle.classList.toggle("active", compact);
	dockModeToggle.title = compact ? "Switch to expanded dock" : "Switch to icons-only dock";
}

if (dockModeToggle) {
	dockModeToggle.addEventListener("click", () => {
		const nextMode = glassDock.classList.contains("compact-dock") ? "expanded" : "compact";
		localStorage.setItem("dockMode", nextMode);
		applyDockMode(nextMode);
	});
}

(function () {
	const savedDockMode = localStorage.getItem("dockMode") || "expanded";
	applyDockMode(savedDockMode);
})();


const dock = document.querySelector(".dock-container");
const dragBtn = dock.querySelector("#dragDockBtn");

const resetDockPosition = () => {
	localStorage.removeItem("dockX");
	localStorage.removeItem("dockY");

	// Restore original CSS positioning
	dock.style.left = "50%";
	dock.style.top = "auto";
	dock.style.bottom = "0px";
	dock.style.transform = "translateX(-50%)";
};

// check if viewing on mobile
if (window.innerWidth <= 768) {
	alert("Mobile view detected - docking to bottom center");
	setDefaultPosition();
}

(function () {
	const savedX = localStorage.getItem("dockX");
	const savedY = localStorage.getItem("dockY");

	if (savedX && savedY) {
		dock.style.left = savedX;
		dock.style.top = savedY;
		dock.style.bottom = "auto";
		dock.style.transform = "none";
	} else {
		// Default centered bottom
		dock.style.left = "50%";
		dock.style.bottom = "0px";
		dock.style.top = "auto";
		dock.style.transform = "translateX(-50%)";
	}
})();

let isDragging = false;
let offsetX = 0;
let offsetY = 0;

// Start dragging
dragBtn.addEventListener("mousedown", (e) => {
	isDragging = true;

	const rect = dock.getBoundingClientRect();

	// 🔥 Lock current visual position BEFORE removing transform
	dock.style.left = rect.left + "px";
	dock.style.top = rect.top + "px";
	dock.style.bottom = "auto"; // reset bottom to avoid conflicts
	dock.style.transform = "none";

	// Now calculate offsets
	offsetX = e.clientX - rect.left;
	offsetY = e.clientY - rect.top;
});

// Drag move
document.addEventListener("mousemove", (e) => {
	if (!isDragging) return;

	dock.style.left = e.clientX - offsetX + "px";
	dock.style.top = e.clientY - offsetY + "px";
	dock.style.bottom = "auto";
});

// Stop dragging
document.addEventListener("mouseup", () => {
	if (!isDragging) return;
	isDragging = false;

	// Save position
	localStorage.setItem("dockX", dock.style.left);
	localStorage.setItem("dockY", dock.style.top);
});


function timeAgo(timestamp) {
	const now = new Date();
	const date = new Date(Number(timestamp)); // already in ms
	const seconds = Math.floor((now - date) / 1000);

	if (seconds < 5) return "Just now";

	const intervals = [
		{ label: "year", seconds: 31536000 },
		{ label: "month", seconds: 2592000 },
		{ label: "day", seconds: 86400 },
		{ label: "hour", seconds: 3600 },
		{ label: "minute", seconds: 60 },
		{ label: "second", seconds: 1 }
	];

	for (const interval of intervals) {
		const count = Math.floor(seconds / interval.seconds);
		if (count >= 1) {
			return `${count} ${interval.label}${count > 1 ? "s" : ""} ago`;
		}
	}
}


function createModal(innerHTML, options = {}) {
	const config = {
		placement: "center", // center | top | bottom
		size: "md", // sm | md | lg | xl | fullscreen
		scrollable: false,
		animation: true,
		backdrop: true,
		keyboard: true,
		...options
	};

	// Create modal root
	const modal = document.createElement("div");
	modal.className = "modal fade";
	modal.tabIndex = -1;

	// Create dialog
	const modalDialog = document.createElement("div");
	modalDialog.className = "modal-dialog";

	// 👉 Placement handling (clean way)
	switch (config.placement) {
		case "center":
			modalDialog.classList.add("modal-dialog-centered");
			break;

		case "top":
			modalDialog.style.marginTop = "1rem";
			break;

		case "bottom":
			modalDialog.classList.add("modal-dialog-centered");
			modalDialog.style.alignItems = "flex-end";
			break;
	}

	// 👉 Size handling
	const sizeMap = {
		sm: "modal-sm",
		lg: "modal-lg",
		xl: "modal-xl",
		fullscreen: "modal-fullscreen"
	};

	if (sizeMap[config.size]) {
		modalDialog.classList.add(sizeMap[config.size]);
	}

	// 👉 Scrollable
	if (config.scrollable) {
		modalDialog.classList.add("modal-dialog-scrollable");
	}

	// Create content
	const modalContent = document.createElement("div");
	modalContent.className = "modal-content";
	modalContent.className += " p-3"; // padding
	modalContent.innerHTML = innerHTML;

	// Assemble
	modalDialog.appendChild(modalContent);
	modal.appendChild(modalDialog);
	document.body.appendChild(modal);

	// Bootstrap init
	const bsModal = new bootstrap.Modal(modal, {
		backdrop: config.backdrop,
		keyboard: config.keyboard
	});

	modal.setAttribute("role", "dialog");
	modal.setAttribute("aria-modal", "true");



	modal.addEventListener("shown.bs.modal", () => {
		// Try to focus something meaningful inside
		let focusTarget = modal.querySelector(
			"[autofocus], textarea, input, button, [tabindex]:not([tabindex='-1'])"
		);

		if (!focusTarget) {
			// fallback to modal itself
			modal.setAttribute("tabindex", "-1");
			focusTarget = modal;
		}

		focusTarget.focus();
	});

	// 👉 Optional animation
	if (config.animation) {
		modalContent.style.animation = "slideIn 0.3s ease";
	}

	//bsModal.show();

	// Cleanup
	const previouslyFocused = document.activeElement;

	modal.addEventListener("hide.bs.modal", () => {
		if (document.activeElement && modal.contains(document.activeElement)) {
			document.activeElement.blur();
		}
	});

	modal.addEventListener("hidden.bs.modal", () => {
		bsModal.dispose();
		modal.remove();
	});

	return {
		el: modal,
		instance: bsModal,
		get: (selector) => modal.querySelector(selector),
		close: () => bsModal.hide()
	};
}


function showDialog({
	title = "Confirm",
	message = "",
	markupHTML = "",
	confirmText = "OK",
	cancelText = "Cancel",
	showCancel = true,
	onConfirm = async () => { },
	onCancel = async () => { }
}) {
	return new Promise((resolve) => {
		const modalObj = createModal(`
					<h3>${title}</h3>
					<p>${message}</p>
					${markupHTML}
					<div class="d-flex justify-content-end gap-2">
						${showCancel ? `<button class="btn btn-secondary dialogCancel">${cancelText}</button>` : ""}
						<button class="btn btn-primary dialogConfirm">${confirmText}</button>
					</div>
				`);

		const modalEl = modalObj.el;
		const modal = modalObj.instance;

		modalEl.querySelector(".dialogConfirm").onclick = async () => {
			await onConfirm();   // 🔥 run user-defined async function
			modal.hide();
			resolve(true);
		};

		if (showCancel) {
			modalEl.querySelector(".dialogCancel").onclick = async () => {
				await onCancel(); // 🔥 optional cancel logic
				modal.hide();
				resolve(false);
			};
		}

		modal.show();
	});
}

async function showMessage({
	type = "success",
	title = "",
	message,
	showDismissBtn = false,
	dismissByKey = true,
	dismissByClick = true,
	dismissByTimer = false,
	dismissTimerMS = 5000
}) {
	const icon = {
		success: "bi bi-check-circle-fill",
		error: "bi bi-exclamation-triangle-fill",
		warning: "bi bi-exclamation-triangle-fill",
		info: "bi bi-info-circle-fill"
	}
	/*const msgModal = createModal(`
		<label><i class="${icon[type]}"></i> ${title}</label>
		<p>${message}</p>
		${showDismiss ? `<button class="btn btn-primary" id="dialogConfirm">OK</button>` : ""}
	`)*/
	const msgModal = createModal(`
				<div class="text-center">				
					<label class="fs-5"><i class="${icon[type]}"></i> ${title}</label>
					<hr>
					<p class="mb-4">${message}</p>
					${showDismissBtn ? `
						<div class="d-grid">
							<button class="btn btn-primary btn-lg dialogConfirm">
								OK
							</button>
						</div>
					` : ""}
				</div>
			`, {
		backdrop: dismissByClick ? true : "static",
		keyboard: dismissByKey
	});
	msgModal.instance.show();

	if (showDismissBtn) {
		msgModal.el.querySelector(".dialogConfirm").onclick = async () => {
			msgModal.instance.hide();
		};
	}

	if (dismissByTimer) {
		setTimeout(() => {
			msgModal.instance.hide();
		}, dismissTimerMS);
	}
}
