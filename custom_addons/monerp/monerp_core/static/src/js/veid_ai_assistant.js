/**
 * VEID Enterprise — AI Assistant
 * Prototype d'assistant conversationnel utilisant Puter.js.
 */
(function () {
    'use strict';

    if (window.__veidAiAssistantInitialized) return;
    window.__veidAiAssistantInitialized = true;

    const PUTER_URL = 'https://js.puter.com/v2/';
    const MODEL = 'claude-sonnet-4-6';
    let puterPromise = null;
    let busy = false;

    function loadPuter() {
        if (window.puter?.ai?.chat) return Promise.resolve(window.puter);
        if (puterPromise) return puterPromise;

        puterPromise = new Promise((resolve, reject) => {
            let script = document.querySelector('script[data-veid-puter]');

            if (!script) {
                script = document.createElement('script');
                script.src = PUTER_URL;
                script.async = true;
                script.dataset.veidPuter = 'true';
                document.head.appendChild(script);
            }

            const timeout = setTimeout(() => {
                reject(new Error('Délai dépassé lors du chargement de Puter.js.'));
            }, 20000);

            script.addEventListener('load', () => {
                clearTimeout(timeout);
                if (window.puter?.ai?.chat) resolve(window.puter);
                else reject(new Error('Puter.js est chargé, mais son API IA est indisponible.'));
            }, { once: true });

            script.addEventListener('error', () => {
                clearTimeout(timeout);
                reject(new Error('Impossible de charger Puter.js. Vérifie ta connexion.'));
            }, { once: true });

            // Le script peut avoir été chargé avant cet appel.
            if (window.puter?.ai?.chat) {
                clearTimeout(timeout);
                resolve(window.puter);
            }
        }).catch(error => {
            puterPromise = null;
            throw error;
        });

        return puterPromise;
    }

    function addMessage(container, role, text) {
        const message = document.createElement('div');
        message.className = `veid-ai-message veid-ai-${role}`;

        const label = document.createElement('strong');
        label.textContent = role === 'user' ? 'Vous' : 'VEID AI';

        const body = document.createElement('div');
        body.className = 'veid-ai-message-body';
        body.textContent = text;

        message.append(label, body);
        container.appendChild(message);
        container.scrollTop = container.scrollHeight;
        return body;
    }

    function extractText(response) {
        const content = response?.message?.content ?? response?.content;
        if (typeof content === 'string') return content;
        if (Array.isArray(content)) {
            return content.map(part => part.text || '').filter(Boolean).join('\n');
        }
        return typeof response === 'string'
            ? response
            : JSON.stringify(response, null, 2);
    }

    function createAssistant() {
        if (document.getElementById('veid-ai-launcher')) return;

        const launcher = document.createElement('button');
        launcher.id = 'veid-ai-launcher';
        launcher.type = 'button';
        launcher.innerHTML = '<i class="fa fa-magic" aria-hidden="true"></i>';
        launcher.title = 'Ouvrir VEID Copilot';
        launcher.setAttribute('aria-label', 'Ouvrir VEID Copilot');

        const panel = document.createElement('section');
        panel.id = 'veid-ai-panel';
        panel.className = 'veid-ai-hidden';
        panel.style.display = 'none';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-label', 'Assistant IA VEID');

        const header = document.createElement('header');
        header.className = 'veid-ai-header';

        const heading = document.createElement('div');
        heading.className = 'veid-ai-heading';

        const title = document.createElement('strong');
        title.textContent = 'VEID Copilot';

        const subtitle = document.createElement('span');
        subtitle.textContent = 'Assistant Décisionnel & Opérationnel';
        heading.append(title, subtitle);

        const close = document.createElement('button');
        close.type = 'button';
        close.textContent = '×';
        close.className = 'veid-ai-close';
        close.setAttribute('aria-label', 'Fermer');

        header.append(heading, close);

        const notice = document.createElement('div');
        notice.className = 'veid-ai-notice';
        notice.textContent =
            'Prototype : évitez de saisir des mots de passe ou des données confidentielles de l’entreprise.';

        const messages = document.createElement('div');
        messages.id = 'veid-ai-messages';
        messages.className = 'veid-ai-messages';
        addMessage(messages, 'assistant',
            'Bonjour ! Je suis VEID AI. Posez-moi une question sur votre ERP, la gestion ou l’informatique.');

        const form = document.createElement('form');
        form.className = 'veid-ai-form';

        const input = document.createElement('textarea');
        input.id = 'veid-ai-input';
        input.rows = 2;
        input.maxLength = 10000;
        input.placeholder = 'Posez votre question…';
        input.setAttribute('aria-label', 'Votre question');

        const send = document.createElement('button');
        send.type = 'submit';
        send.textContent = 'Envoyer';

        form.append(input, send);
        panel.append(header, notice, messages, form);
        document.body.append(launcher, panel);

        function closePanel() {
            panel.classList.add('veid-ai-hidden');
            panel.style.display = 'none';
            launcher.focus();
        }

        launcher.addEventListener('click', () => {
            if (panel.style.display === 'none' || panel.classList.contains('veid-ai-hidden')) {
                panel.style.display = 'flex';
                panel.classList.remove('veid-ai-hidden');
                input.focus();
            } else {
                panel.style.display = 'none';
                panel.classList.add('veid-ai-hidden');
            }
        });
        close.addEventListener('click', closePanel);

        form.addEventListener('submit', async event => {
            event.preventDefault();
            const question = input.value.trim();
            if (!question || busy) return;

            busy = true;
            input.disabled = true;
            send.disabled = true;

            addMessage(messages, 'user', question);
            input.value = '';
            const answer = addMessage(messages, 'assistant', 'Chargement de l’assistant…');

            try {
                const puter = await loadPuter();
                answer.textContent = 'Claude réfléchit…';

                const response = await puter.ai.chat(question, { model: MODEL });
                answer.textContent = extractText(response) || 'Aucune réponse textuelle reçue.';
            } catch (error) {
                answer.textContent = `Erreur : ${error.message || 'Impossible de contacter l’assistant.'}`;
            } finally {
                busy = false;
                input.disabled = false;
                send.disabled = false;
                input.focus();
                messages.scrollTop = messages.scrollHeight;
            }
        });
    }

    function init() {
        if (!document.querySelector('.o_web_client')) return;
        createAssistant();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }

    // Odoo peut remplacer certaines parties de son interface lors de la navigation.
    setInterval(init, 2000);
})();
