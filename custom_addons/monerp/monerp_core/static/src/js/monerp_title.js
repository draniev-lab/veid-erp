/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { titleService } from "@web/core/browser/title_service";

const originalStart = titleService.start;
titleService.start = function (env) {
    const service = originalStart.call(this, env);
    const origSetParts = service.setParts;
    service.setParts = function (parts) {
        if (!parts.zSysName || parts.zSysName === "Odoo" || parts.zSysName === "MonErp Enterprise") {
            parts.zSysName = "VEID Enterprise";
        }
        return origSetParts.call(this, parts);
    };
    return service;
};

// Periodic observer to clean any residual "Odoo" or "MonErp" text in document title or branding popups
if (typeof window !== "undefined") {
    if (document.title.includes("Odoo") || document.title.includes("MonErp")) {
        document.title = document.title.replace(/Odoo/g, "VEID Enterprise").replace(/MonErp/g, "VEID");
    }
    const titleObserver = new MutationObserver(() => {
        if (document.title.includes("Odoo") || document.title.includes("MonErp")) {
            document.title = document.title.replace(/Odoo/g, "VEID Enterprise").replace(/MonErp/g, "VEID");
        }
    });
    if (document.querySelector("head title")) {
        titleObserver.observe(document.querySelector("head title"), {
            subtree: true,
            characterData: true,
            childList: true,
        });
    }
}
