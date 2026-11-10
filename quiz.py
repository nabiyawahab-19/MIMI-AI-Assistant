
def calculate_score(questions, user_answers):
    """
    Compare a student's answers with the correct answer key.
    Return the score and feedback for each question.
    """

    results = []
    score = 0

    for index, question in enumerate(questions):
        correct_answer = question["answer"].strip().upper()
        user_answer = user_answers[index].strip().upper()

        is_correct = user_answer == correct_answer

        if is_correct:
            score += 1

        results.append({
            "question": question["question"],
            "your_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation", "")
        })

    return {
        "score": score,
        "total": len(questions),
        "percentage": round((score / len(questions)) * 100)
        if questions else 0,
        "results": results
    }
    
def parse_user_answers(message, total_questions):
    """Convert answers like 1A, 2B, 3C into an ordered answer list."""

    answers = {}

    for item in message.split(","):
        item = item.strip().upper()

        if len(item) != 2 or not item[0].isdigit():
            raise ValueError(
                "Please use this format: 1A, 2B, 3C, 4D, 5A"
            )

        number = int(item[0])
        letter = item[1]

        if number < 1 or number > total_questions:
            raise ValueError("One of the question numbers is invalid.")

        if letter not in {"A", "B", "C", "D"}:
            raise ValueError("Answers must be A, B, C, or D.")

        if number in answers:
            raise ValueError("You answered one question more than once.")

        answers[number] = letter

    if len(answers) != total_questions:
        raise ValueError("Please answer every question before submitting.")

    return [answers[i] for i in range(1, total_questions + 1)]


