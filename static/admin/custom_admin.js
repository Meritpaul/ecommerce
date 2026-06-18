/**
 * PureShop — Custom Admin Enhancements
 * 1. Disables browser autofill on username/password fields (admin login + user forms)
 * 2. Adds a show/hide eye-icon toggle to every password input
 */
(function () {
    'use strict';

    function buildToggleButton() {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.setAttribute('aria-label', 'Show password');
        btn.tabIndex = -1;
        btn.style.cssText = [
            'position:absolute', 'right:8px', 'top:50%',
            'transform:translateY(-50%)', 'background:none',
            'border:none', 'cursor:pointer', 'padding:4px',
            'color:#6b7280', 'display:flex', 'align-items:center',
            'z-index:5'
        ].join(';');

        btn.innerHTML =
            '<svg class="pw-eye-show" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
            '<path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>' +
            '<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>' +
            '</svg>' +
            '<svg class="pw-eye-hide" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none">' +
            '<path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/>' +
            '</svg>';

        return btn;
    }

    function addToggle(input) {
        // Skip if already processed
        if (input.dataset.pwToggleAdded) return;
        input.dataset.pwToggleAdded = 'true';

        const parent = input.parentNode;

        // Wrap the input in a relative-positioned span so the button can be absolutely placed
        const wrapper = document.createElement('span');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        wrapper.style.width = input.style.width || '100%';

        parent.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        input.style.paddingRight = '36px';
        input.style.boxSizing = 'border-box';
        input.style.width = '100%';

        const btn = buildToggleButton();
        wrapper.appendChild(btn);

        btn.addEventListener('click', function () {
            const showIcon = btn.querySelector('.pw-eye-show');
            const hideIcon = btn.querySelector('.pw-eye-hide');
            if (input.type === 'password') {
                input.type = 'text';
                showIcon.style.display = 'none';
                hideIcon.style.display = '';
                btn.setAttribute('aria-label', 'Hide password');
            } else {
                input.type = 'password';
                showIcon.style.display = '';
                hideIcon.style.display = 'none';
                btn.setAttribute('aria-label', 'Show password');
            }
        });
    }

    function disableAutofill() {
        // Admin login form fields
        const loginUsername = document.querySelector('#id_username');
        const loginPassword = document.querySelector('#id_password');

        if (loginUsername) loginUsername.setAttribute('autocomplete', 'off');
        if (loginPassword) loginPassword.setAttribute('autocomplete', 'new-password');

        // Any form on the page (login form, user add/change form)
        document.querySelectorAll('form').forEach(function (form) {
            form.setAttribute('autocomplete', 'off');
        });
    }

    function init() {
        disableAutofill();

        document.querySelectorAll('input[type="password"]').forEach(function (input) {
            input.setAttribute('autocomplete', 'new-password');
            addToggle(input);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();