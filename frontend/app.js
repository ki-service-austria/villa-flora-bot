// Villa Flora Booking Bot Frontend

const API_BASE = "https://villa-flora-bot.onrender.com/api";

// DOM Elements
const searchForm = document.getElementById("searchForm");
const chatMessages = document.getElementById("chatMessages");
const loadingSection = document.getElementById("loadingSection");
const resultsSection = document.getElementById("resultsSection");
const resultsContainer = document.getElementById("resultsContainer");
const errorSection = document.getElementById("errorSection");
const errorMessage = document.getElementById("errorMessage");

// Set min date to today
const today = new Date().toISOString().split("T")[0];
document.getElementById("checkin").min = today;
document.getElementById("checkout").min = today;

// Event Listeners
searchForm.addEventListener("submit", handleSearch);

async function handleSearch(e) {
    e.preventDefault();

    // Sammle Formulardaten
    const formData = {
        checkin: document.getElementById("checkin").value,
        checkout: document.getElementById("checkout").value,
        adults: parseInt(document.getElementById("adults").value),
        children: parseInt(document.getElementById("children").value),
        infants: parseInt(document.getElementById("infants").value),
        preferred_room_type: document.getElementById("roomType").value || undefined,
        balcony: document.getElementById("balcony").checked
    };

    // Validiere Daten
    if (!formData.checkin || !formData.checkout) {
        showError("Bitte Ankunfts- und Abreisedatum angeben");
        return;
    }

    const checkinDate = new Date(formData.checkin);
    const checkoutDate = new Date(formData.checkout);

    if (checkoutDate <= checkinDate) {
        showError("Abreisedatum muss nach Ankunftsdatum liegen");
        return;
    }

    if (formData.adults + formData.children + formData.infants === 0) {
        showError("Mindestens 1 Person erforderlich");
        return;
    }

    // Zeige Message im Chat
    addChatMessage(
        `Ich suche nach Zimmer für ${formData.adults + formData.children + formData.infants} Personen vom ${formatDate(formData.checkin)} bis ${formatDate(formData.checkout)}...`,
        "user"
    );

    // Zeige Loading
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/search`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || result.message || "Fehler bei der Suche");
        }

        // Zeige Ergebnisse
        displayResults(result.data, formData);

    } catch (error) {
        console.error("Search error:", error);
        showError(`Fehler: ${error.message}`);
        addChatMessage(
            `Es gab einen Fehler bei der Suche: ${error.message}`,
            "bot"
        );
    }
}

function displayResults(suggestions, formData) {
    // Verstecke vorherige Sections
    loadingSection.style.display = "none";
    errorSection.style.display = "none";

    // Zeige Results
    resultsSection.style.display = "block";
    resultsContainer.innerHTML = "";

    const nights = suggestions.nights || 1;
    const totalPersons = suggestions.total_persons;
    const hasChildren = suggestions.has_children;

    // Bot-Antwort
    let botMessage = `Ich habe verfügbare Zimmer für ${totalPersons} Personen gefunden (${nights} Nächte).<br>`;
    if (hasChildren) {
        botMessage += `Da du mit Kindern reist, habe ich komfortable Kombinationen ausgewählt:`;
    } else {
        botMessage += `Hier sind meine Empfehlungen:`;
    }
    addChatMessage(botMessage, "bot");

    // Zeige Vorschläge
    if (!suggestions.suggestions || suggestions.suggestions.length === 0) {
        addChatMessage("Leider keine Verfügbarkeit für deine Anfrage gefunden.", "bot");
        resultsContainer.innerHTML = '<p style="color: #666;">Keine verfügbaren Zimmer gefunden. Bitte versuche andere Daten.</p>';
        return;
    }

    suggestions.suggestions.forEach((suggestion, index) => {
        const card = document.createElement("div");
        card.className = "result-card";

        const confidence = Math.round(suggestion.confidence * 100);
        const totalPrice = (suggestion.total_price || 0).toFixed(2);
        const pricePerNight = (totalPrice / nights).toFixed(2);

        let html = `
            <div>
                <h3>🏆 Option ${index + 1}: ${suggestion.title}</h3>
                <p><strong>Grund:</strong> ${suggestion.reason}</p>
                <div class="result-price">€${pricePerNight}/Nacht<br><small style="font-size: 0.6em;">€${totalPrice} für ${nights} Nächte</small></div>
                <div class="result-meta">
                    <strong>Anzahl Zimmer:</strong> <span>${suggestion.room_count}</span>
                </div>
                <div class="result-meta">
                    <strong>Passgenauigkeit:</strong> <span>${confidence}%</span>
                </div>
                <div class="result-reason">"${suggestion.reason}"</div>
                <a href="${suggestion.booking_link || '#'}" class="btn-booking" target="_blank">
                    Jetzt buchen →
                </a>
            </div>
        `;

        card.innerHTML = html;
        resultsContainer.appendChild(card);
    });
}

function addChatMessage(message, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showLoading() {
    loadingSection.style.display = "flex";
    resultsSection.style.display = "none";
    errorSection.style.display = "none";
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorSection.style.display = "block";
    loadingSection.style.display = "none";
    resultsSection.style.display = "none";
}

function resetForm() {
    searchForm.reset();
    resultsSection.style.display = "none";
    errorSection.style.display = "none";
    loadingSection.style.display = "none";
    addChatMessage("Neue Suche? Gib mir deine Anforderungen ein! 😊", "bot");
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit" });
}
