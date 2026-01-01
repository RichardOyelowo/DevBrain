from config import API_KEY

class Questions:

    DEFAULT_TOPICS = ['Linux', 'BASH', 'PHP', 'Docker', 'HTML', 'Postgres', 'MySQL', 
    'Laravel', 'Kubernetes', 'JavaScript', 'Python', 'Openshift', 'Terraform', 'React', 
    'Django', 'cPanel', 'Ubuntu', 'nodeJS', 'WordPress', 'Next.js', 'VueJS', 'Apache Kafka']
    

    def get_questions(self, topic: str = "uncategorized", limit: int = 10, difficulty: str = 'Easy') -> list:
        try:
            response = requests.get(
                f'https://quizapi.io/api/v1/questions?apiKey={API_KEY}&category={topic}&limit={limit}&difficulty={difficulty}&single_answer_only=true',
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException:
            return []

        questions_data = response.json()
        if not questions_data:
            return []

        questions = []
        for item in questions_data:
            answers_list = {k: v for k, v in item.get("answers", {}).items() if v is not None}

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
