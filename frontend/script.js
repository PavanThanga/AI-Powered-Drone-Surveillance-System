let currentUser = null;
let isLiveConnected = false;
let liveInterval = null;
let selectedFile = null;
const processingOverlay = document.getElementById("processingOverlay");





// Login
document.getElementById('loginFormSubmit').onsubmit = e => {
    e.preventDefault();

    const username = loginUsername.value.trim();
    const password = loginPassword.value.trim();

    // 🔐 Allowed credentials
    const allowedUser = "admin";
    const allowedPass = "6969";

    if (username === allowedUser && password === allowedPass) {
        document.querySelector('.auth-container').classList.add('animate');

        setTimeout(() => {
            currentUser = username;
            showDashboard();
            document.querySelector('.auth-container').classList.remove('animate');
        }, 800);

    } else {
        alert("Invalid credentials. Access denied.");
    }
};



function showDashboard() {
    console.log("SHOW DASHBOARD");
    authScreen.style.display = 'none';
    dashboard.style.display = 'block';
    statusIndicator.style.display = 'flex';
    userName.textContent = `User: ${currentUser}`;
    logoutBtn.classList.remove('hidden');
}
logoutBtn.onclick = () => {
    console.log("LOGOUT CALLED");
    // Reset user
    currentUser = null;

    // Hide all views
    dashboard.style.display = 'none';
    existingView.style.display = 'none';
    liveView.style.display = 'none';

    // Hide logout button
    logoutBtn.classList.add('hidden');

    // Hide status indicator
    statusIndicator.style.display = 'none';

    // Reset auth screen
    authScreen.style.display = 'flex';

    // Optional: clear inputs
    loginUsername.value = '';
    loginPassword.value = '';
};


// Mode select
document.querySelectorAll('.mode-card').forEach(card => {
    card.onclick = () => {
        dashboard.style.display = 'none';
        document.getElementById(card.dataset.mode + 'View').style.display = 'block';
    };
});

// Back buttons
backFromExisting.onclick = backToDashboard;
backFromLive.onclick = backToDashboard;

function resetExistingView() {
    // UI reset
    dualView.classList.remove('show-grid');
    uploadSection.style.display = 'block';

    originalMedia.innerHTML = '';
    aiMedia.innerHTML = '';

    processingOverlay.style.display = 'none';

    detHuman.textContent = '--';
    detVehicle.textContent = '--';
    detWeapon.textContent = '--';

    // 🔥 STATE RESET (MOST IMPORTANT)
    selectedFile = null;
    analyzeBtn.disabled = true;

    // 🔥 FORCE browser to forget previous file
    fileUpload.value = null;
}



function backToDashboard() {
    console.log("BACK TO DASHBOARD CALLED");

    resetExistingView();
    resetLiveView();   // 🔥 important

    existingView.style.display = 'none';
    liveView.style.display = 'none';
    dashboard.style.display = 'block';
}

function resetLiveView() {
    // Stop streams
    liveAI.src = "";
    liveOriginal.src = "";

    // Reset buttons
    connectBtn.disabled = false;
    startBtn.disabled = true;
    stopBtn.disabled = true;
    liveAlertBtn.disabled = true;

    // Reset input
    liveSourceInput.disabled = false;
    liveSourceInput.value = "";
}

// Upload
fileUpload.onchange = e => {
    if (!fileUpload.files || fileUpload.files.length === 0) {
        return;
    }

    // 🔥 SINGLE SOURCE OF TRUTH
    selectedFile = fileUpload.files[0]
    // Hide upload UI
    uploadSection.style.display = 'none';

    // Show dual view
    dualView.classList.add('show-grid');

    // Load original (NO autoplay)
    originalMedia.innerHTML = selectedFile.type.startsWith('video')
        ? `<video src="${URL.createObjectURL(selectedFile)}" controls muted></video>`
        : `<img src="${URL.createObjectURL(selectedFile)}">`;

    // Enable Analyze button
    analyzeBtn.disabled = false;

    // Clear previous AI output
    aiMedia.innerHTML = '';
    processingOverlay.style.display = 'none';

    // Reset summary
    detHuman.textContent = '--';
    detVehicle.textContent = '--';
    detWeapon.textContent = '--';
};

analyzeBtn.onclick = async () => {
    console.log("Analyze clicked. selectedFile =", selectedFile);

    if (!selectedFile) {
        alert("Please upload a video first");
        return;
    }

    // 🔴 Stop & clear previous processed video (if any)
    const existingVideo = aiMedia.querySelector("video");
    if (existingVideo) {
        existingVideo.pause();
        existingVideo.src = "";
        aiMedia.innerHTML = "";
    }

    // 2️⃣ Read toggle values
    const human = humanSwitch.checked;
    const vehicle = vehicleSwitch.checked;
    const weapon = weaponSwitch.checked;

    // 3️⃣ Build FormData (FIELD NAMES MUST MATCH BACKEND)
    const formData = new FormData();
    formData.append("video", selectedFile);
    formData.append("human", human ? "true" : "false");
    formData.append("vehicle", vehicle ? "true" : "false");
    formData.append("weapon", weapon ? "true" : "false");


    // 4️⃣ Show processing overlay
    processingOverlay.style.display = "flex";
    await new Promise(resolve => setTimeout(resolve, 50));

    try {
        // 5️⃣ Call backend
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();
        console.log("Backend response:", data);

        // 6️⃣ Hide overlay
        processingOverlay.style.display = "none";
        console.log(
            "VIDEO URL USED:",
            "http://127.0.0.1:5000" + data.processed_video
        );

        // 7️⃣ SHOW PROCESSED VIDEO (LEFT – 70%)
        aiMedia.innerHTML = `
            <video controls autoplay muted playsinline>
                <source src="http://127.0.0.1:5000${data.processed_video}?t=${Date.now()}" type="video/mp4">
            </video>
        `;

        // 8️⃣ SHOW ORIGINAL + SUMMARY (RIGHT – 30%)
        if (selectedFile.type.startsWith("video")) {

                originalMedia.innerHTML = `
                    <video controls>
                        <source src="${URL.createObjectURL(selectedFile)}" type="${selectedFile.type}">
                    </video>
                `;

            } else {

                originalMedia.innerHTML = `
                    <img src="${URL.createObjectURL(selectedFile)}" style="width:100%; border-radius:8px;">
                `;

            }
        detHuman.textContent = data.summary.human ? "YES" : "NO";
        detVehicle.textContent = data.summary.vehicle ? "YES" : "NO";
        detWeapon.textContent = data.summary.weapon ? "YES" : "NO";


    } catch (error) {
        processingOverlay.style.display = "none";
        console.error("Analyze error:", error);
        alert("Backend connection failed");
    }
};




// Live mode
connectBtn.onclick = () => {
    const source = liveSourceInput.value.trim();

    if (!source) {
        alert("Please enter 0 for webcam or paste RTSP URL.");
        return;
    }

    console.log("Connecting to:", source);

    // Show original stream immediately
    liveOriginal.src = `http://127.0.0.1:5000/live_original?source=${encodeURIComponent(source)}`;

    // Lock input
    liveSourceInput.disabled = true;
    connectBtn.disabled = true;

    // Enable Start
    startBtn.disabled = false;
    stopBtn.disabled = false;

};

startBtn.onclick = () => {
    const source = liveSourceInput.value.trim();

    const human = liveHumanSwitch.checked;
    const vehicle = liveVehicleSwitch.checked;
    const weapon = liveWeaponSwitch.checked;

    startBtn.disabled = true;
    stopBtn.disabled = false;
    liveAlertBtn.disabled = false;
    liveAI.src =
        `http://127.0.0.1:5000/live_processed?` +
        `source=${encodeURIComponent(source)}` +
        `&human=${human}` +
        `&vehicle=${vehicle}` +
        `&weapon=${weapon}`;
};

stopBtn.onclick = () => {
    // Stop streams
    liveAI.src = "";
    liveOriginal.src = "";

    // Reset UI state
    liveSourceInput.disabled = false;
    connectBtn.disabled = false;

    startBtn.disabled = true;
    stopBtn.disabled = true;
    liveAlertBtn.disabled = true;
};
