(function () {
    const listEl = document.getElementById("sites-list");
    const sitesForm = document.getElementById("add-form");
    const siteInput = document.getElementById("url-input");
    const userForm = document.getElementById("user-form");
    const nameInput = document.getElementById("user-name");
    const chatIdInput = document.getElementById("user-chat-id");
    const userStatusEl = document.getElementById("user-status");
    const userNameDisplay = document.getElementById("user-name-display");
    const userChatDisplay = document.getElementById("user-chat-display");
    const toggleUserFormBtn = document.getElementById("toggle-user-form");
    const sitesCountEl = document.getElementById("sites-count");

    if (
        !listEl ||
        !sitesForm ||
        !siteInput ||
        !userForm ||
        !nameInput ||
        !chatIdInput ||
        !userNameDisplay ||
        !userChatDisplay ||
        !toggleUserFormBtn
    ) {
        return;
    }

    const setUserStatus = (message = "", isError = false) => {
        if (!userStatusEl) return;
        userStatusEl.textContent = message;
        userStatusEl.classList.toggle("error", Boolean(isError));
    };

    const updateToggleLabel = () => {
        const isHidden = userForm.classList.contains("is-hidden");
        toggleUserFormBtn.textContent = isHidden ? "Editar usuário" : "Cancelar";
    };

    const showUserForm = (shouldShow) => {
        userForm.classList.toggle("is-hidden", !shouldShow);
        updateToggleLabel();
    };

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
                <span>${siteIndex}. ${url}</span>
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

    const loadUser = async () => {
        const resp = await fetch("/api/user");
        if (!resp.ok) {
            throw new Error("Não foi possível carregar o usuário.");
        }
        const data = await resp.json();
        const name = data.name || "";
        const chatId = data.chat_id || "";
        nameInput.value = name;
        chatIdInput.value = chatId;
        userNameDisplay.textContent = name || "—";
        userChatDisplay.textContent = chatId || "—";
        return data;
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

    toggleUserFormBtn.addEventListener("click", () => {
        const shouldShow = userForm.classList.contains("is-hidden");
        setUserStatus("");
        showUserForm(shouldShow);
    });

    userForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            name: nameInput.value.trim(),
            chat_id: chatIdInput.value.trim(),
        };

        if (!payload.name || !payload.chat_id) {
            setUserStatus("Preencha nome e Chat ID.", true);
            return;
        }

        setUserStatus("Salvando...");
        const resp = await fetch("/api/user", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (resp.ok) {
            await loadUser();
            setUserStatus("Dados atualizados com sucesso.");
            showUserForm(false);
        } else {
            setUserStatus(await handleErrorResponse(resp), true);
        }
    });

    loadSites();
    loadUser()
        .then(() => showUserForm(false))
        .catch((error) => setUserStatus(error.message, true));
})();

