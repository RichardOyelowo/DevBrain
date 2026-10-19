# Frontend Structure

DevBrain renders pages with Flask and Jinja. Templates live in `app/templates`. Styles and browser behavior live in `app/static`. There is no package manager or frontend build command.

## Templates

`app/templates/layout.html` owns the shared page shell, navigation, flashes, and static asset links. Public pages use the marketing header. Signed-in pages use the app sidebar. Admin navigation is shown only to admins, while `@admin_required` protects the routes themselves.

Shared Jinja helpers live in `app/templates/components/macros.html`. Page templates should extend the layout and use route names from the existing Flask blueprints.

## CSS

`app/static/css/main.css` is the stylesheet entry point. It imports design tokens, reset rules, base styles, layout, components, utilities, page styles, and compatibility rules from `legacy/shim.css`.

Keep styles close to their purpose:

- `tokens/`: colors, spacing, type, motion, and depth values
- `layout/`: page shell, header, sidebar, footer, and grid
- `components/`: buttons, cards, forms, tables, and feedback
- `pages/`: marketing and signed-in app pages
- `legacy/shim.css`: old class names that remain in templates

The older `base.css`, `layout.css`, `components.css`, and `pages.css` files are compatibility imports. New page styles belong under `pages/`.

## JavaScript

`app/static/js/app.js` handles mobile navigation, icon setup, and answer selection in the quiz form. Quiz answers are submitted with the form. The server checks ownership, answer state, and selected options.

Keep DOM text updates safe. If a new feature needs server data, add a server-rendered value or a focused API route with normal authentication and response checks.

## External assets

The layout loads Google Fonts and Lucide from their public CDNs. The app itself has no frontend dependency install or compile step.
