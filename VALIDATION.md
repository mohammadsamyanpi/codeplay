# Validation and design corrections

## Completed automated checks

- JavaScript syntax passes for the app and Python worker.
- English and Persian dictionaries have identical key sets.
- A new learner starts with zero XP, zero badges and zero streak.
- Completing before successful execution does not award points.
- Successful checks award exactly 50 XP and one badge.
- Repeated completion cannot award duplicate XP.
- Editing code invalidates previous successful checks.
- Completed progress is persisted in local storage.
- HTML escaping protects displayed user code.
- The starter code preserves the apostrophe in `Let's go, Alex`.
- The pinned Pyodide script URL responds with HTTP 200.

## Browser verification status

Verified in Chrome after reconnecting the extension:

- Desktop landing page and Persian mobile layouts were visually inspected.
- Narrow mobile layouts had no document-level horizontal overflow.
- Real Python execution printed both complete lines and passed all three quest checks.
- Invalid Python produced a SyntaxError and disabled completion; resetting recovered successfully.
- Completion displayed the badge, awarded 50 XP and persisted after reload.
- Replaying an already completed quest kept completion disabled, preventing duplicate XP.
- Instruction goals and result checks now update together.
- Persian RTL, light/dark switching, search filtering and its empty state were checked.
- Light-theme syntax and statistic colors were adjusted for readability.

Public deployment verified on October 5, 2026:

- GitHub Pages built successfully with HTTPS enabled.
- The page, JavaScript, CSS, Python worker, illustrations and font returned HTTP 200.
- Real Python execution also passed all three checks on the published origin.
- A deliberate infinite loop stopped after 60 seconds and re-enabled Run code.
- FAQ expansion worked using the Enter key; the privacy dialog opened and closed.
- Persian language, RTL direction and the light theme persisted after reload.

Clearing local progress has not been exercised in the browser. The checklist below is retained for subsequent releases.

## Mapping to the supplied 32 corrections

1. One responsive document, not repeated desktop/mobile sections.
2–3. Valid starter code and complete console output from real execution.
4. Badge belongs inside the Pro card; no unsupported popularity claim.
5. Back-to-top control on long pages.
6, 17. Explicit email label, privacy link and consent text. Newsletter is disabled until a delivery service exists.
7–8, 24. Consistent primary CTA; outlined secondary actions; separate navigation links.
9–10. Clear Pro roadmap/unlock explanation and consistent difficulty categories.
11–12. Unverified rating/member counts removed rather than invented.
13–14. Actual new-user state; exactly 50 XP once; totals derive from completion.
15. No floating XP popup covering the page; completion uses a dismissible dialog.
16. Distinct Explore and Company footer groups.
18–19. Illustrated avatars and clear sample-persona roles; stories explicitly marked fictional.
20. Native expandable FAQs with visible plus/minus indicators.
21–22. Feature comparison and explicit noncommercial cancellation/refund notice.
23. No emoji-dependent artwork; primary illustrations are image/vector assets. Text symbols use standard browser glyphs.
25–28. Search, syntax highlighting, uncluttered execution status and separated assurance items.
29. Copyright uses the current runtime year; 2026 is the actual year at implementation.
30–31. English/Persian selection, RTL, accessibility notice and light/dark themes.
32. Extensible interface dictionaries, but only English/Persian translations and Python execution currently exist. “All languages” needs scope clarification; universal support is not claimed.

## Manual acceptance checklist

- Desktop at 1440px, mobile at 390px and 320px: no horizontal overflow or overlapping controls.
- Light/dark themes and English/Persian direction persist after reload.
- Search shows matching worlds and a useful empty state.
- FAQs, menu, info dialogs and back-to-top work with keyboard and touch.
- Running default Python prints both complete lines and passes all three checks.
- Invalid syntax shows the actual error and disables completion.
- Changing code after a successful run requires another run before completion.
- An infinite loop is terminated within 60 seconds.
- Completing updates the dashboard, badge and XP; replay adds no XP.
- Reload preserves progress; privacy reset clears learning data with a confirmation.
- Published GitHub Pages paths load all assets and the worker.
