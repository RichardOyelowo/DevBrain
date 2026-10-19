# Admin And Question Authoring

Admin pages are in `app/admin.py`. Each route uses `@admin_required`; hiding a navigation link is not an access check. Forms that change data use POST and CSRF protection.

## Admin access

New accounts have the `user` role. On an empty database, an owner can set `ADMIN_BOOTSTRAP_ENABLED=true` before registering the first account. Turn the setting off as soon as that account is created.

The setting does not promote an account on an existing database. Do not leave bootstrap enabled while registration is open.

## Catalog pages

- `/admin/questions`: review the question library and edit questions.
- `/admin/topics`: add or update quiz categories.
- `/admin/languages`: manage language filters for code questions.
- `/admin/presets`: create fast-start quiz presets.
- `/admin/import`: paste question JSON or upload a JSON file.

Categories with linked questions or presets are deactivated instead of deleted. Imported questions are drafts. Review each question before publishing it.

## Import format

An import accepts a list of questions or an object with a `questions` list. Each question needs a category, prompt, and at least two answer options. Exactly one option must be correct. A category name creates the category when no category ID is supplied.

```json
[
  {
    "topic": "Data Structures",
    "difficulty": "EASY",
    "prompt": "What does len(items) return?",
    "description": "Assume items is a list.",
    "explanation": "It returns the number of elements in the list.",
    "language": "python",
    "code_snippet": "items = [1, 2, 3]",
    "options": [
      { "text": "3", "is_correct": true },
      { "text": "2", "is_correct": false }
    ]
  }
]
```

The importer accepts 1 to 100 questions in a batch. It validates the full batch before saving it. Imported rows get draft status and an import source marker. The question library is where an admin reviews and publishes them.

For code questions, set `language` and `code_snippet`. Keep the category about the skill, such as Data Structures, rather than using the language as the category.

## Before publishing

- Check the prompt and answer options for ambiguity.
- Confirm there is exactly one correct answer.
- Add an explanation that teaches the underlying idea.
- Confirm the category is active.
- Set a language only when the question uses a language-specific filter.
- Publish only after review.
