import requests


class Questions:

    DEFAULT_TOPICS = ["uncategorized", "linux", "bash", "docker", "sql", "cms", "code", 
        "devops", "react", "laravel", "postgres", "django", "cpanel", "nodejs", 
        "wordpress", "next-js", "vuejs", "apache-kafka", "html"
    ]
    
    def __init__(self, api_key):
        self.api_key = api_key       
        

    def get_questions(self, topic: str = "uncategorized", limit: int = 10, difficulty: str = "Easy") -> list[dict]:
        try:
            response = requests.get(
                "https://quizapi.io/api/v1/questions",
                params={
                    "apiKey": self.api_key,
                    "category": topic,
                    "limit": limit,
                    "difficulty": difficulty,
                    "single_answer_only": "true",
                },
                timeout=5,
            )
            response.raise_for_status()
        except requests.RequestException:
            return []

        try:
            questions_data = response.json()
        except ValueError:
            return []

        if not isinstance(questions_data, list) or not questions_data:
            return []

        questions = []
        for item in questions_data:
            question_text = item.get("question")
            if not question_text:
                continue

            answers = item.get("answers", {})
            if not answers:
                continue

            answers_list = {k: v for k, v in answers.items() if v is not None}

            correct_answer = next(
                (
                    answers_list.get(k.replace("_correct", ""))
                    for k, v in item.get("correct_answers", {}).items()
                    if str(v).lower() == "true"
                ),
                None,
            )
            if not correct_answer:
                continue

            questions.append({
                "text": question_text,
                "description": item.get("description") or "",
                "answers": list(answers_list.values()),
                "correct_answer": correct_answer,
                "explanation": item.get("explanation") or "No explanation available",
            })

        print(questions)

        return questions
