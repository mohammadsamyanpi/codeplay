# CodePlay

A responsive recreation of the supplied CodePlay design, with a landing page, local learner dashboard, playable Python quest and badge celebration. Built with HTML, CSS and JavaScript; no Node installation or build step required.

## Run locally

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Serve over HTTP rather than opening `index.html` directly, because modules and Web Workers need an HTTP origin.

## Implemented

- Single responsive layout rather than duplicated desktop/mobile content.
- English and Persian interface, RTL, bundled Persian font, light/dark themes.
- Searchable worlds, accessible FAQ, visible focus, reduced motion and back-to-top.
- Editable, syntax-highlighted Python with real execution through Pyodide 0.29.2 in a Web Worker. Execution terminates after 60 seconds to recover from infinite loops.
- Actual quest checks: a nonempty string variable `name`, the exact greeting and successful console output.
- Completion awards 50 XP once. All totals, badges and streak dates derive from saved completion state. Replaying never grants duplicate points.
- Local code/progress storage and an explicit clear-data action.
- Honest roadmap labels, feature comparison, privacy, terms, cancellation notice and accessibility information.

## Limits

This is a functioning frontend learning prototype, not a complete commercial learning platform. Only the first Python quest is implemented. Remaining Python lessons, Logic Caverns, Django courses, authentication, cloud sync, live AI, certificates, real reviews, public leagues, subscriptions and newsletter delivery need additional backend/content work. None are presented as active. Proposed Pro pricing is not a sale or checkout.

The first Python run needs internet access to `cdn.jsdelivr.net`; loading the WebAssembly runtime may take up to a minute. Python runs locally in the browser. Never enter sensitive data into the editor. Local progress is per browser and is lost when browser storage is cleared. Runtime errors are shown in the console.

## Languages

UI dictionaries are in `translations` in `app.js`. Add a complete dictionary, a language option, locale formatting and direction configuration to support another language. English and Persian are currently translated; universal language support is not claimed. Python is the only executable programming language in this version.

## Publishing

The files in the repository root can be served directly by GitHub Pages. Select the `main` branch and root folder in Pages settings. Do not publish `tmp/` or the original source PDF/text files. No credentials belong in this repository.

## Design assets

`hero.webp` and `pip.webp` were extracted from the user-supplied PDF. The bundled Vazirmatn font uses the SIL Open Font License; see `assets/OFL.txt`. The logo and persona illustrations are SVG/vector assets. Persona stories are explicitly fictional illustrations, not testimonials from real customers.
