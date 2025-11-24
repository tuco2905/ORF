(function () {
    const listEl = document.getElementById("sites-list");
    const sitesForm = document.getElementById("add-form");
    const siteInput = document.getElementById("url-input");
    const sitesCountEl = document.getElementById("sites-count");

    if (!listEl || !sitesForm || !siteInput) {
        return;
    }

    const handleErrorResponse = async (response) => {
        try {
            const data = await response.json();
            return data.error || "Erro ao processar a solicitação.";
        } catch {
            return "Erro ao processar a solicitação.";
        }
    };

    const renderSites = (sites) => {
        let siteIndex = 1;
        listEl.innerHTML = "";
        sites.forEach((url) => {
            const li = document.createElement("li");
            li.innerHTML = `
                <span>${siteIndex}. <a href="${url}" target="_blank">${url}</a></span>
                <button type="button" class="btn btn--danger btn--sm" data-url="${url}">Remover</button>
            `;
            listEl.appendChild(li);
            siteIndex++;
        });

        if (sitesCountEl) {
            sitesCountEl.textContent = sites.length;
        }
    };

    const loadSites = async () => {
        const resp = await fetch("/api/sites");
        renderSites(await resp.json());
    };

    sitesForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const url = siteInput.value.trim();
        if (!url) return;

        const resp = await fetch("/api/sites", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });

        if (resp.ok) {
            const data = await resp.json();
            renderSites(data.sites);
            siteInput.value = "";
        } else {
            alert(await handleErrorResponse(resp));
        }
    });

    listEl.addEventListener("click", async (event) => {
        if (event.target.tagName !== "BUTTON") return;
        const url = event.target.dataset.url;
        const confirmRemoval = window.confirm(`Remover ${url} da lista?`);
        if (!confirmRemoval) return;

        const resp = await fetch("/api/sites", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });

        if (resp.ok) {
            const data = await resp.json();
            renderSites(data.sites);
        } else {
            alert(await handleErrorResponse(resp));
        }
    });

    loadSites();
})();