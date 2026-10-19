# Quiz Attempts And Plan Limits

Quiz rules live in `app/learning.py`. Routes in `app/routes.py` read the request and call those functions. The templates show the returned state.

## Starting a quiz

`create_attempt(user_id, topic_ids, difficulty, limit, language=None)` checks the user's quota, finds published questions, and saves an attempt with one answer row per question. It returns `None` when the selected catalog has no matching questions.

`select_questions()` prefers an exact category, difficulty, and language match. It then widens the search to the selected category, then to the full active catalog. Questions must be published and not archived. Language matching ignores case.

## Answering and review

`submit_answer()` checks that the answer belongs to the attempt and that the selected option belongs to that question. A submitted answer cannot be replaced. The attempt is marked complete after all answers are submitted.

The results and review routes check attempt ownership before showing the saved answers. Keep that check in the backend if templates or navigation change.

## Weekly limits

`quiz_quota_status(user_id)` uses attempts created in the last seven days:

- Free: 5 quiz starts
- Pro: 50 quiz starts
- Unlimited: no cap
- Admin: no cap

Starting a quiz uses a slot even when the learner leaves it unfinished. A slot becomes available after its attempt falls outside the rolling seven-day window.

The pricing page lists Pro at $4.99 per month and Unlimited at $9.99 per month as planned prices. Checkout is not connected. The `users.plan` value controls the quota; no payment provider updates it.

## Dashboard data

`dashboard_stats(user_id)` uses completed `QuizAttempt` rows. It falls back to the older `LegacyQuiz` rows only when the user has no completed attempts in the new format. Update the dashboard template and service tests together if the returned fields change.

## Tests

Quota, selection, answer submission, and dashboard behavior are covered in `tests/test_learning_services.py`. Attempt persistence also has coverage in `tests/test_quiz_attempt_models.py`.
