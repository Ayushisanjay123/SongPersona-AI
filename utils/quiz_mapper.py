
"""
quiz_mapper.py

Converts the user's music taste quiz answers into
the personality profile required by the recommendation engine.
"""


def generate_personality(answers):
    """
    Convert quiz answers into personality traits.

    Supports either a single answer or a list of up to 3
    selected answers per question.
    """

    personality = {
        "Introversion": [],
        "Emotional Intensity": [],
        "Romanticism": [],
        "Energy Preference": [],
        "Optimism": [],
        "Independence": []
    }

    # -------------------------------------------------------
    # Scoring mappings for all 6 questions
    # -------------------------------------------------------

    question_mappings = {
        "listening_time": {
            "📚 While studying or working": {
                "Introversion": 8,
                "Energy Preference": 3,
                "Optimism": 5
            },
            "🚗 While travelling": {
                "Introversion": 5,
                "Energy Preference": 5,
                "Optimism": 6
            },
            "🌙 Before sleeping": {
                "Introversion": 9,
                "Energy Preference": 2,
                "Optimism": 4
            },
            "🏋️ During workouts": {
                "Introversion": 2,
                "Energy Preference": 9,
                "Optimism": 8
            },
            "🎉 At parties or with friends": {
                "Introversion": 2,
                "Energy Preference": 10,
                "Optimism": 9
            }
        },

        "favorite_element": {
            "📝 Meaningful lyrics": {
                "Emotional Intensity": 9,
                "Romanticism": 7
            },
            "🎤 The singer's voice": {
                "Emotional Intensity": 6,
                "Romanticism": 5
            },
            "🎸 Melody": {
                "Emotional Intensity": 7,
                "Romanticism": 6
            },
            "🥁 Beat": {
                "Energy Preference": 9,
                "Optimism": 7
            },
            "🎧 Overall vibe": {
                "Emotional Intensity": 6,
                "Energy Preference": 6
            }
        },

        "playlist": {
            "🌧 Rainy Day Vibes": {
                "Emotional Intensity": 9,
                "Introversion": 8
            },
            "❤️ Love Songs": {
                "Romanticism": 10,
                "Emotional Intensity": 8
            },
            "🌅 Chill Evening": {
                "Introversion": 7,
                "Optimism": 6
            },
            "🔥 Workout Hits": {
                "Energy Preference": 10,
                "Optimism": 8
            },
            "🎉 Party Mix": {
                "Energy Preference": 9,
                "Optimism": 9
            }
        },

        "discovery": {
            "❤️ I mostly replay my favourites": {
                "Independence": 3
            },
            "👥 Friends or family": {
                "Independence": 5
            },
            "📱 Social media": {
                "Independence": 6
            },
            "🎧 Spotify/YouTube recommendations": {
                "Independence": 7
            },
            "🚀 I actively search for new artists": {
                "Independence": 10
            }
        },

        "lyrics": {
            "💕 Romantic": {
                "Romanticism": 10
            },
            "🌟 Inspirational": {
                "Optimism": 9
            },
            "📖 Storytelling": {
                "Emotional Intensity": 8
            },
            "🎉 Fun & Party": {
                "Energy Preference": 9
            },
            "🤷 I don't pay much attention to lyrics": {
                "Energy Preference": 7
            }
        },

        "mood": {
            "😌 Calm & Relaxed": {
                "Introversion": 8
            },
            "😊 Happy": {
                "Optimism": 9
            },
            "💭 Thoughtful": {
                "Emotional Intensity": 8
            },
            "💪 Motivated": {
                "Energy Preference": 9
            },
            "⚡ Excited": {
                "Energy Preference": 10,
                "Optimism": 8
            }
        }
    }

    # -------------------------------------------------------
    # Process each question
    # -------------------------------------------------------

    for question, mapping in question_mappings.items():

        selected_answers = answers.get(question, [])

        # Support old single-answer data as well as new lists
        if isinstance(selected_answers, str):
            selected_answers = [selected_answers]
        elif selected_answers is None:
            selected_answers = []
        else:
            selected_answers = list(selected_answers)[:3]

        # Collect scores separately for each trait in this question
        question_scores = {}

        for answer in selected_answers:
            answer_scores = mapping.get(answer, {})

            for trait, score in answer_scores.items():
                question_scores.setdefault(trait, []).append(score)

        # Average each trait's scores within this question
        # so selecting more options does not add extra weight
        for trait, scores in question_scores.items():
            average_score = sum(scores) / len(scores)
            personality[trait].append(average_score)

    # -------------------------------------------------------
    # Average the collected question-level values
    # -------------------------------------------------------

    final_personality = {}

    for trait, values in personality.items():

        if values:
            final_personality[trait] = round(sum(values) / len(values))
        else:
            final_personality[trait] = 5

    return final_personality
