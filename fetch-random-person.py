import wikipediaapi
import random


def generate_quiz_data(question_count=20):
    """
    Generates data for a 20-question quiz based on Wikipedia sections.

    Args:
        question_count (int): The number of questions to generate for the quiz.

    Returns:
        list: A list of dictionary objects, where each dictionary represents
              a quiz question with its sections, options, and correct answer.
              Returns an empty list if data generation fails.
    """

    # Initialize the Wikipedia API
    wiki_api = wikipediaapi.Wikipedia(
        user_agent='MyQuizApp/1.0 (popxicman@example.com)',
        language='en'
    )

    # Fetching 50 people at random from the list of people in the people.json file
    with open('people.txt', 'r') as file:
        people = file.readlines()
    name_pool = [person.strip() for person in people]
    name_pool = random.sample(name_pool, int(question_count*2.5))

    wrong_answer_pool = name_pool.copy()
    print(f"Successfully fetched {len(name_pool)} names for the answer pool.")

    quiz_data = []
    print("Fetching section data for each quiz subject...")

    for i, subject_title in enumerate(name_pool):
        print(f"  ({i+1}/{question_count}) Getting data for: {subject_title}")
        page = wiki_api.page(subject_title)

        if not page.exists() or not page.sections:
            print(f"    -> Skipping '{subject_title}' (no sections or page error).")
            continue
        else:
            if i == question_count:
                break

        # Get the section titles
        sections = [s.title for s in page.sections]

        # Assemble the answer options
        correct_answer = subject_title
        wrong_answer_pool.remove(correct_answer)
        
        # Randomly select 3 wrong answers
        options = random.sample(wrong_answer_pool, 3)
        options.append(correct_answer)
        random.shuffle(options) # Shuffle the options for the user

        quiz_data.append({
            "question_number": len(quiz_data) + 1,
            "sections": sections,
            "options": options,
            "correct_answer": correct_answer
        })

    return quiz_data

if __name__ == "__main__":
    # Generate the quiz
    quiz = generate_quiz_data(
        question_count=10
    )

    if quiz:
        print("\n--- QUIZ GENERATED SUCCESSFULLY ---")
        # Print the first two questions as an example
        for question in quiz:
            print(f"\n--- Question {question['question_number']} ---")
            print("Which person's page has these sections?")
            for sec in question['sections']:
                print(f"  - {sec}")
            print("\nOptions:")
            for i, opt in enumerate(question['options']):
                print(f"  {chr(65+i)}. {opt}")
            print(f"\nCorrect Answer: {question['correct_answer']}")
