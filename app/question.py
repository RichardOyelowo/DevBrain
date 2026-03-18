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
                    "topics": topic,
                    "limit": limit,
                    "difficulty": difficulty,
                    "single_answer_only": "true",
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5,
            )
            response.raise_for_status()
            json_data = response.json()
            questions_data = json_data.get("data", [])
        except (requests.RequestException, ValueError) as e:
            # Optional: log the error
            print(f"Error fetching questions: {e}")
            questions_data = []

        if not isinstance(questions_data, list) or not questions_data:
            return []

        questions = []

        for item in questions_data:
            question_text = item.get("text")

            if not question_text:
                continue

            answers_dict = item.get("answers", [])
            
            answers_list = [ans.get("text") for ans in answers_dict]
            # Determine correct answer
            correct_answer = next((ans.get("text") for ans in answers_dict if ans.get("isCorrect") is True), None)
            if not correct_answer:
                continue

            questions.append({
                "text": question_text,
                "description": "",
                "answers": answers_list,
                "correct_answer": correct_answer,
                "explanation": item.get("explanation") or "No explanation available",  # stays string
            })
            
        print(questions)
        return questions
