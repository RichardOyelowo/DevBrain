import requests


class Questions:

    DEFAULT_TOPICS = ["uncategorized", "linux", "bash", "docker", "sql", "cms", "code", 
        "devops", "react", "laravel", "postgres", "django", "cpanel", "nodejs", 
        "wordpress", "next-js", "vuejs", "apache-kafka", "html"
    ]
    
    def __init__(self, api_key):
        self.api_key = api_key       
        

    def get_questions(self, topic: str = "uncategorized", limit: int = 10, difficulty: str = 'Easy') -> list:
        try:
            response = requests.get(
                f'https://quizapi.io/api/v1/questions?apiKey={self.api_key}&category={topic}&limit={limit}&difficulty={difficulty}&single_answer_only=true',
                timeout=5
            )
        except requests.RequestException as e:
            return []

        questions_data = response.json()

        if not questions_data:
            return []

        questions = []
        for item in questions_data:
            answers_list = {k: v for k, v in item["answers"].items() if v is not None}

            correct_answer = None
            for key, value in item.get("correct_answers", {}).items():
                if str(value).lower() == "true":
                    correct_answer = answers_list.get(key.replace("_correct", ""))
                    break

            if correct_answer is None:
                continue

            questions.append({
                "text": item["question"], 
                "description": item.get("description", ""),
                "answers": list(answers_list.values()),
                "correct_answer": correct_answer, 
                "explanation": item.get("explanation", "") or "No explanation available"
            })

        if not questions:
            return []

        return questions
