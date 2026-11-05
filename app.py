import streamlit as st
import smtplib
from email.message import EmailMessage
import re

from database import (
    create_tables,
    create_user,
    login_user,
    save_song_feedback,
    save_song,
    get_saved_songs,
    remove_saved_song,
    get_user_by_email,
    create_password_reset_code,
    verify_password_reset_code,
    reset_password,
    save_music_profile,
    get_music_profile,
    EMAIL_ADDRESS,
    EMAIL_APP_PASSWORD,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from urllib.parse import quote_plus
from utils.recommender import recommend_songs
from utils.personality_emotion import generate_personality_emotion
from utils.quiz_mapper import generate_personality


# Initialize database tables
create_tables()
# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="🎵 SongPersona AI",
    page_icon="🎵",
    layout="centered",
)


# ==================================================
# AUTHENTICATION
# ==================================================

def send_password_reset_email(recipient_email, reset_code):

    message = EmailMessage()

    message["Subject"] = "SongPersona AI - Password Reset Code"
    message["From"] = EMAIL_ADDRESS
    message["To"] = recipient_email

    message.set_content(
        f"""
Hello,

We received a request to reset your SongPersona AI password.

Your password reset code is:

{reset_code}

This code is valid for 10 minutes.

If you did not request a password reset, you can safely ignore this email.

Regards,
SongPersona AI
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD
        )

        server.send_message(message)


def show_authentication():
    # Switch to Login after successful registration
    if st.session_state.pop("switch_to_login_after_signup", False):
        st.session_state["auth_tab"] = "🔐 Login"
        st.session_state["show_signup_success"] = True
    
    st.markdown(
        '<div class="auth-title">🎵 SongPersona AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="auth-subtitle">Discover the music personality within you</div>',
        unsafe_allow_html=True
    )

    # Center the authentication selector
    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])

    with auth_col2:
        auth_tab = st.radio(
            " ",
            ["🔐 Login", "✨ Create Account"],
            horizontal=True,
            key="auth_tab"
        )
    # Show registration success after the Login tab loads
    if st.session_state.pop("show_signup_success", False):
     st.success(
        "Account created successfully! 🎉 "
        "You can now log in with your new account."
    )

    # ==================================================
    # FORGOT PASSWORD
    # ==================================================

    if st.session_state.auth_mode == "forgot_password":

        st.subheader("Reset your password 🔐")

        st.write(
            "Enter the email address associated with your "
            "SongPersona AI account."
        )

        reset_email_input = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="reset_email_input"
        )

        if st.button(
            "📩 Send Reset Code",
            use_container_width=True,
            key="send_reset_code_button"
        ):

            if not reset_email_input.strip():

                st.error(
                    "Please enter your email address."
                )

            else:

                reset_email_input = (
                    reset_email_input.strip().lower()
                )

                user = get_user_by_email(
                    reset_email_input
                )

                if not user:

                    st.error(
                        "No account was found with this email."
                    )

                else:

                    reset_code = create_password_reset_code(
                        user[0]
                    )

                    try:

                        send_password_reset_email(
                            reset_email_input,
                            reset_code
                        )

                        st.session_state.reset_user_id = user[0]

                        st.session_state.reset_email = (
                            reset_email_input
                        )

                        st.session_state.auth_mode = (
                            "verify_code"
                        )

                        st.success(
                            "A password reset code has been "
                            "sent to your email. 📩"
                        )

                        st.rerun()

                    except Exception:

                        st.error(
                            "Unable to send the reset email. "
                            "Please check your email configuration."
                        )

        st.write("")

        if st.button(
            "← Back to Login",
            key="back_to_login_button"
        ):

            st.session_state.auth_mode = "login"

            st.session_state.reset_user_id = None

            st.session_state.reset_email = None

            st.rerun()

        return


    # ==================================================
    # VERIFY RESET CODE
    # ==================================================

    if st.session_state.auth_mode == "verify_code":

        st.subheader("Enter Reset Code 🔑")

        st.write(
            f"A 6-digit reset code was sent to "
            f"**{st.session_state.reset_email}**."
        )

        reset_code_input = st.text_input(
            "Reset Code",
            placeholder="Enter the 6-digit code",
            max_chars=6,
            key="reset_code_input"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter your new password",
            key="new_password"
        )

        confirm_new_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter your new password",
            key="confirm_new_password"
        )

        if st.button(
            "🔐 Reset Password",
            use_container_width=True,
            key="reset_password_button"
        ):

            if not reset_code_input:

                st.error(
                    "Please enter the reset code."
                )

            elif not new_password or not confirm_new_password:

                st.error(
                    "Please enter and confirm your new password."
                )

            elif new_password != confirm_new_password:

                st.error(
                    "Passwords do not match."
                )

            elif len(new_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            else:

                valid_code = verify_password_reset_code(
                    st.session_state.reset_user_id,
                    reset_code_input
                )

                if not valid_code:

                    st.error(
                        "Invalid or expired reset code."
                    )

                else:

                    reset_success = reset_password(
                        st.session_state.reset_user_id,
                        new_password
                    )

                    if reset_success:

                        st.session_state.auth_mode = "login"

                        st.session_state.reset_user_id = None

                        st.session_state.reset_email = None

                        st.success(
                            "Password reset successfully! 🎉 "
                            "You can now log in with your new password."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Unable to reset the password. "
                            "Please try again."
                        )

        st.write("")

        if st.button(
            "← Back to Login",
            key="verify_back_to_login_button"
        ):

            st.session_state.auth_mode = "login"

            st.session_state.reset_user_id = None

            st.session_state.reset_email = None

            st.rerun()

        return


    # ==================================================
    # LOGIN
    # ==================================================

    if auth_tab == "🔐 Login":
        st.subheader("Welcome back! ❤️")

        login_email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        # FORGOT PASSWORD
        if st.button(
            "Forgot password?",
            key="forgot_password_button"
        ):

            st.session_state.auth_mode = (
                "forgot_password"
            )

            st.rerun()

        st.write("")

        # --------------------------------------------------
        # LOGIN BUTTON
        # --------------------------------------------------

        if st.button(
            "Login",
            use_container_width=True,
            key="login_button"
        ):

            if not login_email or not login_password:

                st.error(
                    "Please enter your email and password."
                )

            else:

                user = login_user(
                    login_email.strip(),
                    login_password
                )

                if user:

                    st.session_state.logged_in = True

                    st.session_state.user_id = user[0]

                    st.session_state.user_name = user[1]

                    st.session_state.user_email = user[2]

                    saved_profile = get_music_profile(user[0])

                    if saved_profile:

                        st.session_state.personality = saved_profile[0]

                        st.session_state.emotion_profile = saved_profile[1]

                        st.session_state.profile_created = True

                    else:

                        st.session_state.personality = None

                        st.session_state.emotion_profile = None

                        st.session_state.profile_created = False

                    # Trigger login success animation
                    st.session_state["show_login_success"] = True

                    st.session_state.page = "home"

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )


    # ==================================================
    # SIGN UP
    # ==================================================

    elif auth_tab == "✨ Create Account":

        st.subheader(
            "Create your SongPersona account 🎶"
        )

        signup_name = st.text_input(
            "Name",
            placeholder="Enter your name",
            key="signup_name"
        )

        signup_email = st.text_input(
            "Email",
            placeholder="Enter your email",
            key="signup_email"
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a password",
            key="signup_password"
        )

        signup_confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="signup_confirm_password"
        )

        if st.button(
            "Create Account",
            use_container_width=True,
            key="signup_button"
        ):

            # Clean user inputs
            clean_name = signup_name.strip()
            clean_email = signup_email.strip().lower()

            # 1. Check all fields
            if (
                not clean_name
                or not clean_email
                or not signup_password
                or not signup_confirm_password
            ):

                st.error("Please fill in all fields.")

            # 2. Validate email format
            elif not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                clean_email
            ):

                st.error("Please enter a valid email address.")

            # 3. Check password length
            elif len(signup_password) < 6:

                st.error(
                    "Password must be at least 6 characters."
                )

            # 4. Confirm passwords match
            elif signup_password != signup_confirm_password:

                st.error("Passwords do not match.")

            else:

                created = create_user(
                    clean_name,
                    clean_email,
                    signup_password
                )

                if created:

                    # Switch to Login after registration
                    st.session_state[
                        "switch_to_login_after_signup"
                    ] = True

                    st.rerun()

                else:

                    st.error(
                        "An account with this email already exists."
                    )


# --------------------------------------------------
# Load Custom CSS
# --------------------------------------------------

try:

    with open(
        "assets/style.css",
        encoding="utf-8"
    ) as f:

        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True,
        )

except FileNotFoundError:

    st.warning(
        "assets/style.css was not found. "
        "The app will still run without the custom styling."
    )


# --------------------------------------------------
# Session State
# --------------------------------------------------

def init_session_state():

    create_tables()

    defaults = {

        "logged_in": False,

        "user_id": None,

        "user_name": None,

        "user_email": None,

        "auth_mode": "login",

        "reset_user_id": None,

        "reset_email": None,

        "page": "home",

        "profile_created": False,

        "personality": None,

        "emotion_profile": None,

        "recommendations": None,

        "recommendation_offset": 0,

        # Quiz state
        "quiz_question": 0,

        "quiz_answers": {},
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


init_session_state()


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def go_to(page):

    st.session_state.page = page

    st.rerun()



def reset_profile():

    st.session_state.profile_created = False

    st.session_state.personality = None

    st.session_state.emotion_profile = None

    st.session_state.recommendations = None

    st.session_state.recommendation_offset = 0

    # Reset quiz
    st.session_state.quiz_question = 0

    st.session_state.quiz_answers = {}

    # Clear checkbox widget state only when restarting the quiz
    for key in list(st.session_state.keys()):
        if key.startswith("quiz_checkbox_"):
            del st.session_state[key]


# --------------------------------------------------
# Radar Chart
# --------------------------------------------------

def show_radar_chart(personality):

    # --------------------------------------------------
    # ORIGINAL PERSONALITY TRAITS
    # --------------------------------------------------

    traits = list(
        personality.keys()
    )

    values = [
        float(value)
        for value in personality.values()
    ]

    # Close the radar shape
    radar_values = (
        values + values[:1]
    )

    # --------------------------------------------------
    # HUMAN-FRIENDLY LABELS
    # --------------------------------------------------

    radar_labels = {

        "Introversion":
            "Me-Time Music",

        "Emotional Intensity":
            "Feel Music Deeply",

        "Romanticism":
            "Soft & Romantic",

        "Energy Preference":
            "Music Energy",

        "Optimism":
            "Feel-Good Side",

        "Independence":
            "Unique Taste",
    }

    display_traits = [
        radar_labels.get(
            trait,
            trait
        )
        for trait in traits
    ]

    # --------------------------------------------------
    # ANGLES
    # --------------------------------------------------

    angles = np.linspace(
        0,
        2 * np.pi,
        len(traits) + 1
    )

    # --------------------------------------------------
    # CREATE SMALL RADAR CHART
    # --------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(3.2, 3.2),
        dpi=100,
        subplot_kw={
            "polar": True
        }
    )

    # --------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------

    fig.patch.set_facecolor(
        "#0F0F14"
    )

    ax.set_facecolor(
        "#0F0F14"
    )

    # --------------------------------------------------
    # RADAR LINE
    # --------------------------------------------------

    ax.plot(
        angles,
        radar_values,
        linewidth=2.2,
        color="#A78BFA"
    )

    # --------------------------------------------------
    # RADAR FILL
    # --------------------------------------------------

    ax.fill(
        angles,
        radar_values,
        color="#A78BFA",
        alpha=0.20
    )

    # --------------------------------------------------
    # FRIENDLY LABELS
    # --------------------------------------------------

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        display_traits,
        fontsize=7,
        color="white"
    )

    # --------------------------------------------------
    # SCORE RANGE
    # --------------------------------------------------

    ax.set_ylim(
        0,
        10
    )

    ax.set_yticks(
        [2, 4, 6, 8, 10]
    )

    ax.set_yticklabels(
        ["2", "4", "6", "8", "10"],
        fontsize=6,
        color="#B8B8C7"
    )

    # --------------------------------------------------
    # GRID
    # --------------------------------------------------

    ax.grid(
        color="#555566",
        alpha=0.35,
        linewidth=0.6
    )

    # --------------------------------------------------
    # OUTER BORDER
    # --------------------------------------------------

    ax.spines[
        "polar"
    ].set_color(
        "#555566"
    )

    ax.spines[
        "polar"
    ].set_alpha(
        0.5
    )

    # --------------------------------------------------
    # LABEL DISTANCE
    # --------------------------------------------------

    ax.tick_params(
        axis="x",
        pad=5
    )

    ax.tick_params(
        axis="y",
        pad=2
    )

    # --------------------------------------------------
    # TIGHT LAYOUT
    # --------------------------------------------------

    plt.tight_layout(
        pad=0.2
    )

    # --------------------------------------------------
    # CENTER THE SMALL CHART
    # --------------------------------------------------

    col1, col2, col3 = st.columns(
        [1, 1, 1]
    )

    with col2:

        st.pyplot(
            fig,
            width=350
        )

    # --------------------------------------------------
    # CLOSE FIGURE
    # --------------------------------------------------

    plt.close(fig)


# --------------------------------------------------
# Personality Explanation
# --------------------------------------------------

def show_explanation(personality):

    st.divider()

    # --------------------------------------------------
    # How to read the profile
    # --------------------------------------------------

    st.markdown(
        "### 📖 How to Read Your Profile"
    )

    st.info(
        "The farther a point is from the center, "
        "the stronger that trait is in your music "
        "preferences. Scores range from **0 to 10**."
    )

    # --------------------------------------------------
    # Sort traits from strongest to weakest
    # --------------------------------------------------

    sorted_traits = sorted(
        personality.items(),
        key=lambda x: float(x[1]),
        reverse=True,
    )

    strongest_traits = [
        trait
        for trait, score in sorted_traits[:3]
    ]

    # --------------------------------------------------
    # HUMAN-FRIENDLY TRAIT LABELS
    # --------------------------------------------------

    trait_labels = {

        "Introversion":
            "🎧 Your Me Time Music",

        "Emotional Intensity":
            "❤️ You Feel Music Deeply",

        "Romanticism":
            "💕 Your Soft & Romantic Side",

        "Energy Preference":
            "⚡ Your Music Energy",

        "Optimism":
            "☀️ Your Feel Good Side",

        "Independence":
            "🦋 Your Unique Taste",
    }

    # --------------------------------------------------
    # HUMAN-FRIENDLY DESCRIPTIONS
    # --------------------------------------------------

    trait_descriptions = {

        "Introversion":
            "You enjoy having your own musical space.",

        "Emotional Intensity":
            "You tend to connect deeply with the feelings in a song.",

        "Romanticism":
            "You have a soft spot for heartfelt and romantic songs.",

        "Energy Preference":
            "You enjoy music that matches your energy, from calm to lively.",

        "Optimism":
            "You enjoy music that can lift your mood.",

        "Independence":
            "You like music that feels personal and true to your own taste.",
    }

    # --------------------------------------------------
    # TECHNICAL DESCRIPTIONS
    # --------------------------------------------------
    # These are kept for the AI/project side.

    technical_descriptions = {

        "Introversion":
            "reflective, personal, and calmer music",

        "Emotional Intensity":
            "emotionally expressive and meaningful music",

        "Romanticism":
            "sentimental, romantic, and emotionally warm music",

        "Energy Preference":
            "energetic, lively, and high-energy music",

        "Optimism":
            "positive, uplifting, and cheerful music",

        "Independence":
            "expressive, individualistic, and distinctive music",
    }

    # --------------------------------------------------
    # FRIENDLY TRAIT LINE
    # --------------------------------------------------

    trait_line = " • ".join(
        trait_labels.get(trait, trait)
        for trait in strongest_traits
    )

    # --------------------------------------------------
    # CREATE NATURAL MUSIC PERSONALITY DESCRIPTION
    # --------------------------------------------------

    phrase_parts = [
        trait_descriptions[trait]
        for trait in strongest_traits
        if trait in trait_descriptions
    ]

    if len(phrase_parts) == 1:

        music_description = (
            phrase_parts[0]
        )

    elif len(phrase_parts) == 2:

        music_description = (
            f"{phrase_parts[0]} "
            f"{phrase_parts[1]}"
        )

    elif len(phrase_parts) >= 3:

        # Keep this shorter so the card
        # does not become too crowded.

        music_description = (
            f"{phrase_parts[0]} "
            f"{phrase_parts[1]}"
        )

    else:

        music_description = (
            "Your music preferences reflect "
            "your own unique combination of traits."
        )

    # --------------------------------------------------
    # PROFILE CARDS
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)

    # ==================================================
    # CARD 1 — STRONGEST TRAIT
    # ==================================================

    with col1:

        if strongest_traits:

            primary_trait = strongest_traits[0]

            primary_score = float(
                sorted_traits[0][1]
            )

            primary_label = trait_labels.get(
                primary_trait,
                primary_trait
            )

        else:

            primary_trait = "Unique"

            primary_label = (
                "🎵 Your Unique Music Personality"
            )

            primary_score = 0

        # Friendly names for secondary traits

        secondary_traits = " • ".join(
            trait_labels.get(
                trait,
                trait
            )
            for trait in strongest_traits[1:]
        )

        secondary_html = (
            secondary_traits
            if secondary_traits
            else "Your profile has a unique balance of traits."
        )

        st.html(
            f"""
            <div style="
                background: linear-gradient(
                    145deg,
                    #18151f,
                    #111117
                );
                border: 1px solid #302844;
                border-radius: 16px;
                padding: 22px;
                min-height: 185px;
                box-shadow:
                    0 8px 25px
                    rgba(0,0,0,0.20);
            ">

                <div style="
                    color: #a78bfa;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    margin-bottom: 12px;
                ">
                    ⭐ YOUR STRONGEST TRAIT
                </div>

                <div style="
                    color: white;
                    font-size: 20px;
                    font-weight: 700;
                    line-height: 1.35;
                ">
                    {primary_label}
                </div>

                <div style="
                    color: #9f9baa;
                    font-size: 11px;
                    margin-top: 5px;
                ">
                    AI trait: {primary_trait}
                </div>

                <div style="
                    color: #c4b5fd;
                    font-size: 13px;
                    margin-top: 5px;
                    font-weight: 600;
                ">
                    {primary_score:.1f} / 10
                </div>

                <div style="
                    color: #b8b8c7;
                    font-size: 13px;
                    margin-top: 12px;
                    line-height: 1.6;
                ">
                    {secondary_html}
                </div>

            </div>
            """
        )

    # ==================================================
    # CARD 2 — MUSIC PERSONALITY
    # ==================================================

    with col2:

        strongest_detail = (
            ", ".join(
                technical_descriptions[trait]
                for trait in strongest_traits
                if trait in technical_descriptions
            )
        )

        if strongest_detail:

            supporting_text = (
                "These traits help shape the music "
                "you are most likely to connect with."
            )

        else:

            supporting_text = (
                "Your strongest personality signals "
                "shape a distinctive musical taste."
            )

        st.html(
            f"""
            <div style="
                background: linear-gradient(
                    145deg,
                    #18151f,
                    #111117
                );
                border: 1px solid #302844;
                border-radius: 16px;
                padding: 22px;
                min-height: 185px;
                box-shadow:
                    0 8px 25px
                    rgba(0,0,0,0.20);
            ">

                <div style="
                    color: #a78bfa;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    margin-bottom: 14px;
                ">
                    🎵 YOUR MUSIC PERSONALITY
                </div>

                <div style="
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    line-height: 1.6;
                ">
                    {music_description}
                </div>

                <div style="
                    color: #b8b8c7;
                    font-size: 13px;
                    margin-top: 12px;
                    line-height: 1.6;
                ">
                    {supporting_text}
                </div>

            </div>
            """
        )

    # ==================================================
    # CARD 3 — SIMPLE WORDS
    # ==================================================

    with col3:

        simple_words = (
            trait_line
            if trait_line
            else "Your unique music personality"
        )

        st.html(
            f"""
            <div style="
                background: linear-gradient(
                    145deg,
                    #18151f,
                    #111117
                );
                border: 1px solid #302844;
                border-radius: 16px;
                padding: 22px;
                min-height: 185px;
                box-shadow:
                    0 8px 25px
                    rgba(0,0,0,0.20);
            ">

                <div style="
                    color: #a78bfa;
                    font-size: 13px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    margin-bottom: 14px;
                ">
                    🎧 IN SIMPLE WORDS
                </div>

                <div style="
                    color: white;
                    font-size: 17px;
                    font-weight: 700;
                    line-height: 1.5;
                ">
                    {simple_words}
                </div>

                <div style="
                    color: #b8b8c7;
                    font-size: 13px;
                    margin-top: 14px;
                    line-height: 1.6;
                ">
                    These are the three personality signals
                    that influence your musical preferences
                    the most.
                </div>

            </div>
            """
        )

# --------------------------------------------------
# Recommendations
# --------------------------------------------------

def show_recommendations(
    recommendations,
    personality=None
):

    st.divider()

    st.subheader(
        "🎵 Songs Picked Just for You"
    )

    if (
        recommendations is None
        or recommendations.empty
    ):

        st.warning(
            "No matching songs found. "
            "Try another profile."
        )

        return

    # --------------------------------------------------
    # Recommendation Batches
    # --------------------------------------------------

    batch_size = 5

    total_recommendations = len(
        recommendations
    )

    current_offset = st.session_state.get(
        "recommendation_offset",
        0
    )

    if current_offset >= total_recommendations:

        current_offset = 0

        st.session_state.recommendation_offset = 0

    display_df = recommendations.iloc[
        current_offset:
        current_offset + batch_size
    ].copy()

    # --------------------------------------------------
    # Helper
    # --------------------------------------------------

    def safe_value(value):

        if pd.isna(value):

            return ""

        return str(value)

    # --------------------------------------------------
    # Recommendation Cards
    # --------------------------------------------------

    saved_songs = get_saved_songs(
        st.session_state.user_id
    )

    saved_song_keys = {
        (song[1], song[2])
        for song in saved_songs
    }

    for rank, (_, row) in enumerate(
        display_df.iterrows(),
        start=1
    ):

        title = safe_value(
            row.get(
                "title",
                "Unknown Song"
            )
        )

        artist = safe_value(
            row.get(
                "artist",
                "Unknown Artist"
            )
        )

        emotion = safe_value(
            row.get(
                "emotion",
                "Unknown"
            )
        )

        emotion_score = row.get(
            "emotion_score",
            None
        )

        similarity = row.get(
            "similarity",
            None
        )

        # --------------------------------------------------
        # Spotify Search
        # --------------------------------------------------

        spotify_query = quote_plus(
            f"{title} {artist}"
        )

        spotify_url = (
            "https://open.spotify.com/search/"
            f"{spotify_query}"
        )

        # --------------------------------------------------
        # Emotion Percentage
        # --------------------------------------------------

        try:

            emotion_percentage = (
                float(emotion_score) * 100
            )

        except (
            TypeError,
            ValueError
        ):

            emotion_percentage = 0

        # --------------------------------------------------
        # Personality Match Percentage
        # --------------------------------------------------

        try:

            match_percentage = (
                float(similarity) * 100
            )

        except (
            TypeError,
            ValueError
        ):

            match_percentage = 0

        emotion_percentage = max(
            0,
            min(
                100,
                emotion_percentage
            )
        )

        match_percentage = max(
            0,
            min(
                100,
                match_percentage
            )
        )

        # --------------------------------------------------
        # Recommendation Label
        # --------------------------------------------------

        if match_percentage >= 80:

            match_label = (
                "Strong personality fit"
            )

        elif match_percentage >= 65:

            match_label = (
                "Good personality fit"
            )

        else:

            match_label = (
                "Personality fit"
            )

        why_text = (
            f"This song is a {match_label.lower()} for your music personality, "
            f"with a {match_percentage:.1f}% personality match. "
            f"The detected emotion is {emotion.lower()}, "
            f"with {emotion_percentage:.1f}% confidence."
        )

        # --------------------------------------------------
        # RECOMMENDATION CARD
        # --------------------------------------------------

        st.html(
            f"""
            <div style="
                background: linear-gradient(
                    145deg,
                    #18151f,
                    #111117
                );
                border: 1px solid #302844;
                border-radius: 16px;
                padding: 18px 20px;
                margin-bottom: 13px;
                box-shadow:
                    0 8px 25px
                    rgba(0,0,0,0.20);
            ">

                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    gap: 15px;
                ">

                    <div style="
                        flex: 1;
                        min-width: 0;
                    ">

                        <div style="
                            color: #a78bfa;
                            font-size: 11px;
                            font-weight: 700;
                            letter-spacing: 1px;
                            margin-bottom: 6px;
                        ">
                            #{rank} RECOMMENDATION
                        </div>

                        <div style="
                            color: white;
                            font-size: 18px;
                            font-weight: 700;
                            line-height: 1.4;
                            margin-bottom: 4px;
                        ">
                            🎵 {title}
                        </div>

                        <div style="
                            color: #b8b8c7;
                            font-size: 14px;
                        ">
                            {artist}
                        </div>

                    </div>

                    <div style="
                        background: #2b2340;
                        color: #c4b5fd;
                        border-radius: 20px;
                        padding: 6px 12px;
                        font-size: 12px;
                        font-weight: 600;
                        white-space: nowrap;
                    ">
                        {emotion}
                    </div>

                </div>

                <div style="
                    margin-top: 15px;
                    color: #b8b8c7;
                    font-size: 12px;
                    line-height: 1.5;
                ">

                    <span style="
                        color: #c4b5fd;
                        font-weight: 600;
                   ">
                       💡 Why this song?
                   </span>

                   &nbsp;&nbsp;

                   {why_text}

                </div>

                <div style="
                    margin-top: 15px;
                ">

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        color: #b8b8c7;
                        font-size: 12px;
                        margin-bottom: 5px;
                    ">

                        <span>
                            Emotion Confidence
                        </span>

                        <span>
                            {emotion_percentage:.1f}%
                        </span>

                    </div>

                    <div style="
                        height: 6px;
                        background: #292633;
                        border-radius: 10px;
                        overflow: hidden;
                    ">

                        <div style="
                            width: {emotion_percentage}%;
                            height: 100%;
                            background: #a78bfa;
                            border-radius: 10px;
                        "></div>

                    </div>

                </div>

                <div style="
                    margin-top: 11px;
                ">

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        color: #b8b8c7;
                        font-size: 12px;
                        margin-bottom: 5px;
                    ">

                        <span>
                            Personality Match
                        </span>

                        <span>
                            {match_percentage:.1f}%
                        </span>

                    </div>

                    <div style="
                        height: 6px;
                        background: #292633;
                        border-radius: 10px;
                        overflow: hidden;
                    ">

                        <div style="
                            width: {match_percentage}%;
                            height: 100%;
                            background: #c4b5fd;
                            border-radius: 10px;
                        "></div>

                    </div>

                </div>

                <a
                    href="{spotify_url}"
                    target="_blank"
                    rel="noopener noreferrer"
                    style="
                        display: inline-block;
                        margin-top: 15px;
                        padding: 9px 14px;
                        border: 1px solid #3b3152;
                        border-radius: 10px;
                        background: #1f1930;
                        color: #c4b5fd;
                        text-decoration: none;
                        font-size: 13px;
                        font-weight: 700;
                    "
                >
                    🎧 Listen on Spotify ↗
                </a>

            </div>
            """
        )

        if (
            title,
            artist
        ) in saved_song_keys:

            st.success(
                "💜 Saved to your songs",
                icon="💜"
            )

        else:

            if st.button(
                "💾 Save Song",
                key=f"save_song_{current_offset}_{rank}",
                width="stretch"
            ):

                save_song(
                    st.session_state.user_id,
                    title,
                    artist,
                    emotion,
                    emotion_score,
                    similarity
                )

                st.success(
                    "Song saved successfully! 💜"
                )

                st.rerun()
        # ----------------------------------------------
        # RECOMMENDATION FEEDBACK
        # ----------------------------------------------

        st.write("")

        st.caption(
            "Did you like this recommendation?"
        )

        feedback_col1, feedback_col2 = st.columns(2)

        with feedback_col1:

            if st.button(
                "❤️ Love it",
                key=f"feedback_love_{current_offset}_{rank}",
                width="stretch"
            ):

                save_song_feedback(
                    st.session_state.user_id,
                    title,
                    artist,
                    "love"
                )

                st.session_state[
                    f"feedback_{current_offset}_{rank}"
                ] = "love"

                st.success(
                    "Glad you liked it! 💜"
                )

        with feedback_col2:

            if st.button(
                "👎 Not for me",
                key=f"feedback_no_{current_offset}_{rank}",
                width="stretch"
            ):

                save_song_feedback(
                    st.session_state.user_id,
                    title,
                    artist,
                    "not_for_me"
                )

                st.session_state[
                    f"feedback_{current_offset}_{rank}"
                ] = "not_for_me"

                st.info(
                    "Thanks for your feedback! 🎵"
                )


    # --------------------------------------------------
    # Recommend Again
    # --------------------------------------------------

    next_offset = (
        current_offset + batch_size
    )

    if next_offset < total_recommendations:

        st.write("")

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            if st.button(
                "🔄 Recommend Again",
                use_container_width=True,
                key="recommend_again_button",
            ):

                st.session_state.recommendation_offset = (
                    next_offset
                )

                st.rerun()

    elif total_recommendations > batch_size:

        st.write("")

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            if st.button(
                "🔄 Show Recommendations Again",
                use_container_width=True,
                key="recommend_restart_button",
            ):

                st.session_state.recommendation_offset = 0

                st.rerun()


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

def show_home():
    
# ==================================================
# USER ACCOUNT
# ==================================================

    account_col1, account_col2 = st.columns(
        [8, 2]
    )

    with account_col2:

        user_name = st.session_state.get(
            "user_name",
            "User"
        )

        with st.popover(
            f"👤 {user_name}",
            width="content"
            
        ):

            st.markdown("### 👤 My Account")

            st.caption("ACCOUNT DETAILS")

            st.markdown(f"**Name**  \n{user_name}")

            st.markdown("**Email**")

            user_email = st.session_state.get("user_email", "")

            st.markdown(
               f"""
               <div style="
               background: #191b23;
               border-radius: 12px;
               padding: 12px;
               color: #e5e0ed;
               font-size: 14px;
               overflow-wrap: anywhere;
               line-height: 1.5;
            ">
               {user_email}
            </div>
            """,
            unsafe_allow_html=True
        )

            st.divider()

            # ------------------------------------------
            # MY MUSIC PROFILE
            # ------------------------------------------

            if st.button(
                "👤 My Music Profile",
                key="account_music_profile",
                width="stretch"
            ):

                st.session_state.page = "music_profile"

                st.rerun()

            # ------------------------------------------
            # SAVED SONGS
            # ------------------------------------------

            if st.button(
                "💾 Saved Songs",
                key="account_saved_songs",
                width="stretch"
            ):

                st.session_state.page = "saved_songs"

                st.rerun()

            # ------------------------------------------
            # LOGOUT
            # ------------------------------------------

            if st.button(
                "🚪 Logout",
                key="logout_button",
                width="stretch"
            ):

                st.session_state.logged_in = False

                st.session_state.user_id = None

                st.session_state.user_name = None

                st.session_state.user_email = None

                st.session_state.page = "home"

                st.rerun()

    # ==================================================
    # WELCOME MESSAGE
    # ==================================================

    st.html(
        f"""
        <div style="
            text-align: center;
            margin-top: 0px;
            margin-bottom: -10px;
        ">

            <h2 style="
                color: white;
                margin-bottom: 5px;
                font-size: 28px;
                font-weight: 600;
            ">
                Welcome back, {st.session_state.user_name}! 👋
            </h2>

            <p style="
                color: #aaa;
                font-size: 15px;
                margin-top: 0;
            ">
                Ready to discover music that feels like you?
            </p>

        </div>
        """
    )


    # ==================================================
    # HERO SECTION
    # ==================================================

    st.html(
        """
        <div class="hero-section" style="
            margin-top: -35px;
        ">

            <div class="hero-content">

                <div class="hero-badge">
                    🎧 AI-Powered Music Discovery
                </div>

                <h1>
                    Find Music That
                    <span>Feels Like You.</span>
                </h1>

                <p>
                    SongPersona AI understands your
                    personality, emotions, and music
                    preferences to discover songs that
                    truly match you.
                </p>

                <div class="hero-features">

                    <div>
                        🧠 Personality Analysis
                    </div>

                    <div>
                        🎵 Smart Recommendations
                    </div>

                    <div>
                        💜 Emotion-Aware
                    </div>

                </div>

            </div>

        </div>
        """
    )


    # ==================================================
    # DISCOVER BUTTON
    # ==================================================

    st.write("")

    col1, col2, col3 = st.columns(
        [1, 2, 1]
    )

    with col2:

        if st.button(
            "🎧  Discover My Music Personality  →",
            use_container_width=True,
            key="discover_music_button",
        ):

            reset_profile()

            go_to("quiz")


    # ==================================================
    # HOW SONGPERSONA AI WORKS
    # ==================================================

    st.html(
        """
        <div style="
            text-align: center;
            margin-top: 35px;
            margin-bottom: 25px;
        ">

            <h2 style="
                color: white;
                font-size: 26px;
                margin-bottom: 8px;
            ">
                ✨ How SongPersona AI Works
            </h2>

            <p style="
                color: #999;
                font-size: 15px;
                margin-top: 0;
            ">
                From your music taste to personalized recommendations.
            </p>

        </div>
        """
    )

    step1, step2, step3 = st.columns(3)

    with step1:

        st.html(
            """
            <div style="
                background: #15151d;
                border: 1px solid #292936;
                border-radius: 16px;
                padding: 25px 20px;
                min-height: 145px;
            ">

                <div style="
                    font-size: 30px;
                    margin-bottom: 12px;
                ">
                    🎧
                </div>

                <h3 style="
                    color: white;
                    font-size: 18px;
                    margin-bottom: 8px;
                ">
                    1. Take the Quiz
                </h3>

                <p style="
                    color: #aaa;
                    font-size: 14px;
                    line-height: 1.6;
                    margin: 0;
                ">
                    Answer six simple questions about your music taste.
                </p>

            </div>
            """
        )

    with step2:

        st.html(
            """
            <div style="
                background: #15151d;
                border: 1px solid #292936;
                border-radius: 16px;
                padding: 25px 20px;
                min-height: 145px;
            ">

                <div style="
                    font-size: 30px;
                    margin-bottom: 12px;
                ">
                    🧠
                </div>

                <h3 style="
                    color: white;
                    font-size: 18px;
                    margin-bottom: 8px;
                ">
                    2. Discover Your Persona
                </h3>

                <p style="
                    color: #aaa;
                    font-size: 14px;
                    line-height: 1.6;
                    margin: 0;
                ">
                    AI turns your answers into a six-trait music personality.
                </p>

            </div>
            """
        )

    with step3:

        st.html(
            """
            <div style="
                background: #15151d;
                border: 1px solid #292936;
                border-radius: 16px;
                padding: 25px 20px;
                min-height: 145px;
            ">

                <div style="
                    font-size: 30px;
                    margin-bottom: 12px;
                ">
                    🎵
                </div>

                <h3 style="
                    color: white;
                    font-size: 18px;
                    margin-bottom: 8px;
                ">
                    3. Get Your Songs
                </h3>

                <p style="
                    color: #aaa;
                    font-size: 14px;
                    line-height: 1.6;
                    margin: 0;
                ">
                    Our recommendation engine finds songs that match your profile.
                </p>

            </div>
            """
        )


# --------------------------------------------------
# QUIZ PAGE
# --------------------------------------------------

def show_quiz():

    st.html(
        """
        <div class="quiz-intro">

            <div class="quiz-badge">
                🎧 PERSONALIZED MUSIC QUIZ
            </div>

            <h2>
                Tell Us About Your
                <span>Music Taste.</span>
            </h2>

            <p>
                Answer a few questions about your
                listening habits, preferences,
                and emotions.
            </p>

            <p>
                We'll use your answers to create
                your personalized SongPersona profile.
            </p>

        </div>
        """
    )


    # --------------------------------------------------
    # Questions
    # --------------------------------------------------

    questions = [

        {
            "key": "listening_time",

            "question":
                "🎧 1. When do you usually enjoy listening to music the most?",

            "options": [
                "📚 While studying or working",
                "🚗 While travelling",
                "🌙 Before sleeping",
                "🏋️ During workouts",
                "🎉 At parties or with friends",
            ],
        },

        {
            "key": "favorite_element",

            "question":
                "🎵 2. What do you enjoy the most in a song?",

            "options": [
                "📝 Meaningful lyrics",
                "🎤 The singer's voice",
                "🎸 Melody",
                "🥁 Beat",
                "🎧 Overall vibe",
            ],
        },

        {
            "key": "playlist",

            "question":
                "❤️ 3. Which playlist would you most likely play right now?",

            "options": [
                "🌧 Rainy Day Vibes",
                "❤️ Love Songs",
                "🌅 Chill Evening",
                "🔥 Workout Hits",
                "🎉 Party Mix",
            ],
        },

        {
            "key": "discovery",

            "question":
                "🌍 4. How do you usually discover new music?",

            "options": [
                "❤️ I mostly replay my favourites",
                "👥 Friends or family",
                "📱 Social media",
                "🎧 Spotify/YouTube recommendations",
                "🚀 I actively search for new artists",
            ],
        },

        {
            "key": "lyrics",

            "question":
                "✨ 5. What kind of lyrics do you enjoy the most?",

            "options": [
                "💕 Romantic",
                "🌟 Inspirational",
                "📖 Storytelling",
                "🎉 Fun & Party",
                "🤷 I don't pay much attention to lyrics",
            ],
        },

        {
            "key": "mood",

            "question":
                "🌈 6. How do you want music to make you feel?",

            "options": [
                "😌 Calm & Relaxed",
                "😊 Happy",
                "💭 Thoughtful",
                "💪 Motivated",
                "⚡ Excited",
            ],
        },
    ]

    total_questions = len(
        questions
    )

    current_index = (
        st.session_state.quiz_question
    )

    if current_index < 0:

        current_index = 0

    if current_index >= total_questions:

        current_index = (
            total_questions - 1
        )

    st.session_state.quiz_question = (
        current_index
    )

    current_question = questions[
        current_index
    ]


    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    progress_value = (
        (current_index + 1)
        / total_questions
    )

    st.progress(
        progress_value,
        text=(
            f"Question {current_index + 1} "
            f"of {total_questions}"
        ),
    )


    # --------------------------------------------------
    # Question Navigation
    # --------------------------------------------------

    st.markdown(
        '<div class="quiz-sidebar-title">'
        'YOUR QUESTIONS'
        '</div>',
        unsafe_allow_html=True,
    )

    nav_cols = st.columns(
        total_questions
    )

    for index, question in enumerate(
        questions
    ):

        with nav_cols[index]:

            answered = (
                question["key"]
                in st.session_state.quiz_answers
            )

            if index == current_index:

                button_text = (
                    f"● {index + 1}"
                )

            elif answered:

                button_text = (
                    f"✓ {index + 1}"
                )

            else:

                button_text = (
                    f"{index + 1}"
                )

            if st.button(
                button_text,
                key=f"question_nav_{index}",
                use_container_width=True,
            ):

                st.session_state.quiz_question = (
                    index
                )

                st.rerun()


    st.write("")


    # --------------------------------------------------
    # Current Question
    # --------------------------------------------------

    st.markdown(
        f'<div class="question-counter">'
        f'Question {current_index + 1} / '
        f'{total_questions}'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="question-heading">'
        f'{current_question["question"]}'
        f'</div>',
        unsafe_allow_html=True,
    )


    # --------------------------------------------------
    # Persistent Multiple Answers (Maximum 3)
    # --------------------------------------------------

    question_key = current_question["key"]
    options = current_question["options"]

    # Get previously saved answers
    saved_answer = st.session_state.quiz_answers.get(
        question_key, []
    )

    
    # Support old answers saved as a single string
    if isinstance(saved_answer, str):
       saved_answer = [saved_answer]
    else:
     saved_answer = list(saved_answer)[:3]

    # Create unique keys for each checkbox
    checkbox_keys = [
        f"quiz_checkbox_{question_key}_{i}"
        for i in range(len(options))
    ]

    # Restore previously selected checkboxes
    for i, option in enumerate(options):
        widget_key = checkbox_keys[i]

        if widget_key not in st.session_state:
            st.session_state[widget_key] = (
                option in saved_answer
            )

    st.caption("Select up to 3 options.")

    # Display checkboxes
    for i, option in enumerate(options):
        widget_key = checkbox_keys[i]

        selected_count = sum(
            bool(st.session_state[key])
            for key in checkbox_keys
        )

        is_selected = st.session_state[widget_key]

        st.checkbox(
            option,
            key=widget_key,
            disabled=(
                not is_selected and selected_count >= 3
            )
        )

    # Collect selected options
    answer = [
        option
        for i, option in enumerate(options)
        if st.session_state[checkbox_keys[i]]
    ]

    # Save selected answers
    if answer:
        st.session_state.quiz_answers[question_key] = answer
    else:
        st.session_state.quiz_answers.pop(
            question_key, None
        )

    st.write("")

    # --------------------------------------------------
    # Navigation Buttons
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if current_index == 0:

            if st.button(
                "← Back to Home",
                use_container_width=True,
            ):

                go_to("home")

        else:

            if st.button(
                "← Previous",
                use_container_width=True,
            ):

                st.session_state.quiz_question -= 1

                st.rerun()


    with col2:

        if current_index < total_questions - 1:

            if st.button(
                "Next →",
                use_container_width=True,
                type="primary",
            ):

                if not answer:

                    st.warning(
                        "Please select at least one answer before continuing."
                    )

                else:

                    st.session_state.quiz_question += 1

                    st.rerun()

        else:

            create_profile = st.button(
                "✨ Create My Music Profile",
                use_container_width=True,
                type="primary",
            )

            if create_profile:

                required_keys = [
                    question["key"]
                    for question in questions
                ]

                missing_answers = [
                    key
                    for key in required_keys
                    if not st.session_state.quiz_answers.get(key)
                ]

                if missing_answers:

                    st.warning(
                        "⚠️ Please answer all six questions "
                        "before creating your music profile."
                    )

                    return


                # --------------------------------------------------
                # BACKEND — UNCHANGED
                # --------------------------------------------------

                answers = (
                    st.session_state.quiz_answers
                )

                try:

                    with st.spinner(
                        "🧠 Understanding your music personality..."
                    ):

                        personality = (
                            generate_personality(
                                answers
                            )
                        )

                    with st.spinner(
                        "💭 Analyzing your emotional music profile..."
                    ):

                        emotion_profile = (
                            generate_personality_emotion(
                                personality
                            )
                        )

                    with st.spinner(
                        "🎵 Finding songs that match your personality..."
                    ):

                        recommendations = (
                            recommend_songs(
                                personality
                            )
                        )

                    st.session_state.personality = (
                        personality
                    )

                    st.session_state.emotion_profile = (
                        emotion_profile
                    )

                    st.session_state.recommendations = (
                        recommendations
                    )
                    save_music_profile(
                        st.session_state.user_id,
                        personality,
                        emotion_profile
                    )

                    st.session_state.recommendation_offset = 0

                    st.session_state.profile_created = (
                        True
                    )

                    st.session_state.page = (
                        "results"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "Something went wrong while "
                        "creating your profile."
                    )

                    st.exception(e)


# --------------------------------------------------
# RESULTS PAGE
# --------------------------------------------------

def show_results():

    personality = (
        st.session_state.personality
    )

    emotion_profile = (
        st.session_state.emotion_profile
    )

    recommendations = (
        st.session_state.recommendations
    )

    if (
        personality is None
        or emotion_profile is None
    ):

        st.warning(
            "Your profile is not available yet. "
            "Please take the quiz first."
        )

        if st.button(
            "🎧 Take the Quiz",
            use_container_width=True,
        ):

            go_to("quiz")

        return


    # --------------------------------------------------
    # Header
    # --------------------------------------------------

    st.markdown(
        "# 🎭 Your SongPersona"
    )

    st.markdown(
        "Your music personality has been created "
        "from your quiz answers."
    )

    st.divider()


    # --------------------------------------------------
    # Music Personality
    # --------------------------------------------------

    st.subheader(
        "🎭 Your Music Personality"
    )

    emotion_type = emotion_profile.get(
        "emotion_type",
        "Your Music Persona",
    )

    emotion_description = emotion_profile.get(
        "description",
        "Your music preferences have their "
        "own unique emotional character.",
    )

    st.markdown(
        f"## {emotion_type}"
    )

    st.write(
        emotion_description
    )


    # --------------------------------------------------
    # Radar Chart
    # --------------------------------------------------

    st.subheader(
        "📊 Your Personality Profile"
    )

    show_radar_chart(
        personality
    )


    # --------------------------------------------------
    # Explanation
    # --------------------------------------------------

    show_explanation(
        personality
    )


    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    show_recommendations(
        recommendations,
        personality
    )


    # --------------------------------------------------
    # Bottom Buttons
    # --------------------------------------------------

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🎧 Take Quiz Again",
            use_container_width=True,
        ):

            reset_profile()

            go_to("quiz")

    with col2:

        if st.button(
            "🏠 Back to Home",
            use_container_width=True,
        ):

            go_to("home")


# --------------------------------------------------
# About Section
# --------------------------------------------------

def show_about():

    st.divider()

    with st.expander(
        "ℹ️ About SongPersona AI"
    ):

        st.markdown(
            """
            🎵 **SongPersona AI**

            Your personal AI music companion that
            helps you discover songs based on your
            mood, preferences, and personality.

            Simply answer a few questions and let AI
            create a music profile that understands
            your taste.

            ✨ Discover songs that match your emotions.

            🎧 Find music that feels like you.
            """
        )


# --------------------------------------------------
# SAVED SONGS PAGE
# --------------------------------------------------

def show_saved_songs():

    st.markdown(
        """
        <div style="text-align:center; margin-bottom:25px;">
            <h1 style="margin-bottom:5px;">💜 My Saved Songs</h1>
            <p style="color:#aaa;">
                Your personal collection of songs
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


    # Back to Home button

    if st.button(
        "← Back to Home",
        key="saved_back_home",
        width="stretch"
    ):

        st.session_state.page = "home"

        st.rerun()


    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    # Get saved songs for current user

    saved_songs = get_saved_songs(
        st.session_state.user_id
    )


    # No songs saved yet

    if not saved_songs:

        st.info(
            "You haven't saved any songs yet. "
            "Take the quiz and discover your music personality! 🎵"
        )

        if st.button(
            "🎵 Discover My Music Personality",
            key="saved_discover",
            width="stretch"
        ):

            st.session_state.page = "quiz"

            st.rerun()

        return


    st.markdown(
        f"### 🎶 {len(saved_songs)} Saved Song"
        f"{'s' if len(saved_songs) != 1 else ''}"
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    # Display saved songs

    for song in saved_songs:

        song_id = song[0]

        title = song[1]

        artist = song[2]

        emotion = song[3]

        emotion_score = song[4]

        similarity = song[5]

        saved_at = song[6]


        st.html(
           f"""
           <div style="
               background:#171720;
               border:1px solid #2b2b3a;
               border-radius:15px;
               padding:18px;
               margin-bottom:12px;
           ">

               <h3 style="
               margin-bottom:5px;
               color:white;
           ">
               🎵 {title}
        </h3>

        <p style="
               color:#bbb;
               margin-bottom:10px;
        ">
              🎤 {artist}
        </p>

    </div>
    """
)

        col1, col2, col3 = st.columns(3)

        with col1:

            if emotion:

                st.caption(
                    f"💜 Emotion: {emotion}"
                )

        with col2:

            if emotion_score is not None:

                st.caption(
                    f"🎯 Emotion Score: {emotion_score:.2f}"
                )

        with col3:

            if similarity is not None:

                st.caption(
                    f"✨ Match: {similarity:.2f}"
                )


        # Spotify search

        spotify_url = (
            "https://open.spotify.com/search/"
            + quote_plus(
                f"{title} {artist}"
            )
        )


        col1, col2 = st.columns(
            [1, 1]
        )

        with col1:

            st.link_button(
                "🎧 Open in Spotify",
                spotify_url,
                width="stretch"
            )

        with col2:

            if st.button(
                "🗑️ Remove",
                key=f"remove_saved_{song_id}",
                width="stretch"
            ):

                remove_saved_song(
                    song_id,
                    st.session_state.user_id
                )

                st.success(
                    "Song removed from your saved songs."
                )

                st.rerun()


        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )


# --------------------------------------------------
# MY MUSIC PROFILE PAGE
# --------------------------------------------------

def show_music_profile():

    personality = st.session_state.get(
        "personality"
    )

    emotion_profile = st.session_state.get(
        "emotion_profile"
    )

    # --------------------------------------------------
    # PROFILE NOT CREATED
    # --------------------------------------------------

    if (
        personality is None
        or emotion_profile is None
    ):

        st.title("👤 My Music Profile")

        st.caption(
            "Your personal music identity"
        )

        st.info(
            "You haven't created your music profile yet. "
            "Take the quiz to discover your music personality."
        )

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col2:

            if st.button(
                "🎧 Discover My Music Personality →",
                use_container_width=True,
                type="primary",
                key="profile_start_quiz"
            ):

                reset_profile()
                go_to("quiz")

        return


    # --------------------------------------------------
    # GET PERSONA INFORMATION
    # --------------------------------------------------

    emotion_type = emotion_profile.get(
        "emotion_type",
        "Balanced Listener 🎵"
    )

    emotion_description = emotion_profile.get(
        "description",
        "You enjoy different emotions and a variety of musical experiences."
    )


    # --------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------

    st.title("👤 My Music Profile")

    st.caption(
        "Your personal music identity"
    )


    # --------------------------------------------------
    # MUSIC PERSONA
    # --------------------------------------------------

    st.markdown("### 🎭 YOUR MUSIC PERSONA")

    with st.container(border=True):

        st.markdown(
            f"## {emotion_type}"
        )

        st.write(
            emotion_description
        )


    # --------------------------------------------------
    # TRAIT LABELS
    # --------------------------------------------------

    trait_labels = {

        "Introversion":
            "🎧 Your Me Time Music",

        "Emotional Intensity":
            "❤️ You Feel Music Deeply",

        "Romanticism":
            "💕 Your Soft & Romantic Side",

        "Energy Preference":
            "⚡ Your Music Energy",

        "Optimism":
            "🌞 Your Feel Good Side",

        "Independence":
            "🦋 Your Unique Taste",

    }


    # --------------------------------------------------
    # TRAIT DESCRIPTIONS
    # --------------------------------------------------

    trait_descriptions = {

        "Introversion":
            "You enjoy having your own musical space.",

        "Emotional Intensity":
            "You tend to connect deeply with the feelings in a song.",

        "Romanticism":
            "You have a soft spot for heartfelt and romantic songs.",

        "Energy Preference":
            "You enjoy music that matches your energy, from calm to lively.",

        "Optimism":
            "You enjoy music that can lift your mood.",

        "Independence":
            "You like music that feels personal and true to your taste.",

    }


    # --------------------------------------------------
    # FIND TOP 3 TRAITS
    # --------------------------------------------------

    sorted_traits = sorted(
        personality.items(),
        key=lambda item: float(item[1]),
        reverse=True
    )

    strongest_traits = sorted_traits[:3]


    # --------------------------------------------------
    # STRONGEST TRAITS
    # --------------------------------------------------

    st.markdown("### ⭐ Your Strongest Traits")

    st.caption(
        "The three personality signals that shape your music preferences the most."
    )


    cols = st.columns(3)


    for index, (trait, score) in enumerate(
        strongest_traits
    ):

        label = trait_labels.get(
            trait,
            trait
        )

        description = trait_descriptions.get(
            trait,
            "This personality trait influences your music preferences."
        )

        with cols[index]:

            with st.container(border=True):

                st.caption(
                    f"#{index + 1}"
                )

                st.markdown(
                    f"### {label}"
                )

                st.write(
                    description
                )

                st.markdown(
                    f"**{float(score):.1f}** / 10"
                )


    # --------------------------------------------------
    # MUSIC IDENTITY
    # --------------------------------------------------

    strongest_trait = strongest_traits[0][0]

    strongest_label = trait_labels.get(
        strongest_trait,
        strongest_trait
    )

    strongest_description = trait_descriptions.get(
        strongest_trait,
        "This personality trait strongly influences your music preferences."
    )


    st.markdown("### 🎵 Your Music Identity")


    with st.container(border=True):

        st.caption(
            "Your strongest music signal"
        )

        st.markdown(
            f"### {strongest_label}"
        )

        st.write(
            strongest_description
        )


    # --------------------------------------------------
    # PROFILE AT A GLANCE
    # --------------------------------------------------

    st.markdown("### 🎶 Your Profile at a Glance")


    col1, col2 = st.columns(2)


    with col1:

        with st.container(border=True):

            st.caption(
                "MUSIC PERSONA"
            )

            st.markdown(
                f"### 🎭 {emotion_type}"
            )


    with col2:

        with st.container(border=True):

            st.caption(
                "TOP PERSONALITY SIGNAL"
            )

            st.markdown(
                f"### {strongest_label}"
            )


    # --------------------------------------------------
    # ACTION BUTTONS
    # --------------------------------------------------

    st.divider()


    col1, col2 = st.columns(2)


    with col1:

        if st.button(
            "🎧 Retake Quiz",
            use_container_width=True,
            key="profile_retake_quiz"
        ):

            reset_profile()
            go_to("quiz")


    with col2:

        if st.button(
            "🏠 Back to Home",
            use_container_width=True,
            key="profile_back_home"
        ):

            go_to("home")

# AUTHENTICATION GATE + PAGE ROUTER

if not st.session_state.logged_in:

    show_authentication()

else:
        # Login success celebration
    if st.session_state.pop("show_login_success", False):

        st.balloons()

        st.toast(
            f"Welcome back, {st.session_state.user_name}! 🎵",
            icon="🎉"
        )

    if st.session_state.page == "home":

        show_home()

    elif st.session_state.page == "quiz":

        show_quiz()

    elif st.session_state.page == "results":

        show_results()

    elif st.session_state.page == "saved_songs":

        show_saved_songs()

    elif st.session_state.page == "music_profile":

        show_music_profile()

    else:

        st.session_state.page = "home"

        st.rerun()

# ABOUT
show_about()


    