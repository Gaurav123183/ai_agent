import streamlit as st
import re
import html

from rag import generate_response


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Response Assist",
    page_icon="🛡️",
    layout="centered"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>
.stApp { background:#f7f8f8; }

.block-container {
    max-width:900px;
    padding-top:35px !important;
    padding-bottom:45px !important;
}

.header {
    display:flex;
    align-items:center;
    gap:10px;
    margin-top:5px;
}

.prototype {
    background:#f8e9e5;
    color:#b24d42;
    padding:4px 7px;
    border-radius:3px;
    font-size:8px;
    letter-spacing:1px;
}

.main-title {
    font-family:Georgia,serif;
    font-size:25px;
    font-weight:bold;
    color:#20343b;
}

.header-line {
    height:1px;
    background:#dce1e1;
    margin:10px 0 16px;
}

.helpline-box {
    background:white;
    border:1px solid #dce1e1;
    border-radius:7px;
    padding:15px;
    margin-bottom:18px;
}

.helpline-title {
    font-family:Georgia,serif;
    font-size:18px;
    font-weight:bold;
    color:#24343b;
    margin-bottom:12px;
}

.helpline-grid {
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:8px;
}

.helpline-card {
    border-radius:6px;
    padding:10px 5px;
    text-align:center;
}

.helpline-icon { font-size:21px; }

.helpline-name {
    font-size:9px;
    color:#4e5c61;
    min-height:23px;
}

.helpline-number {
    font-size:17px;
    font-weight:bold;
}

.helpline-note {
    font-size:9px;
    color:#697579;
    margin-top:10px;
}

.step-card {
    background:white;
    border:1px solid #dce1e1;
    border-radius:4px;
    padding:8px;
    height:55px;
}

.step-number {
    font-size:8px;
    color:#52666d;
    font-weight:bold;
    letter-spacing:1px;
}

.step-name {
    font-family:Georgia,serif;
    font-size:10px;
    color:#26373e;
    margin-top:5px;
}

.question-box {
    background:white;
    border:1px solid #dce1e1;
    border-radius:7px;
    padding:18px;
    margin-top:18px;
    margin-bottom:12px;
}

.question-title {
    font-family:Georgia,serif;
    font-size:21px;
    font-weight:bold;
    color:#24343b;
}

.input-hint {
    color:#697579;
    font-size:11px;
    margin-bottom:8px;
}

.result-box {
    background:white;
    border:1px solid #dce1e1;
    border-radius:7px;
    padding:16px;
    margin-top:18px;
    overflow:hidden;
}

.result-title {
    color:#28745d;
    font-size:10px;
    font-weight:bold;
    letter-spacing:2px;
    margin-bottom:4px;
}

.action-row {
    display:flex;
    align-items:flex-start;
    gap:12px;
    border-bottom:1px solid #dce1e1;
    padding:13px 0;
}

.action-row:last-child { border-bottom:none; }

.action-number {
    color:#c94c4c;
    font-family:Georgia,serif;
    font-size:20px;
    font-style:italic;
    min-width:28px;
}

.action-text {
    color:#26373e;
    font-family:Georgia,serif;
    font-size:13px;
    line-height:1.55;
    flex:1;
}

.disclaimer {
    border-top:1px solid #dce1e1;
    margin-top:22px;
    padding-top:10px;
    font-size:9px;
    color:#697579;
    line-height:1.5;
}

@media (max-width:700px) {
    .helpline-grid { grid-template-columns:repeat(2,1fr); }
    .main-title { font-size:22px; }
}
</style>
""", unsafe_allow_html=True)


# Keep the generated result in session state so Start Over can remove it.
st.session_state.setdefault("action_plan", None)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header">
    <span class="prototype">PROTOTYPE</span>
    <span class="main-title">Response Assist</span>
</div>
<div class="header-line"></div>
""", unsafe_allow_html=True)


# ============================================================
# EMERGENCY HELPLINES
# ============================================================

st.markdown("""
<div class="helpline-box">

<div class="helpline-title">Emergency Helplines</div>

<div class="helpline-grid">

<div class="helpline-card" style="background:#f8eeee;">
<div class="helpline-icon">🆘</div>
<div class="helpline-name">All Emergencies</div>
<div class="helpline-number" style="color:#c94c4c;">112</div>
</div>

<div class="helpline-card" style="background:#f8eeee;">
<div class="helpline-icon">🚑</div>
<div class="helpline-name">Ambulance</div>
<div class="helpline-number" style="color:#c94c4c;">108</div>
</div>

<div class="helpline-card" style="background:#eef3f5;">
<div class="helpline-icon">👮</div>
<div class="helpline-name">Police</div>
<div class="helpline-number" style="color:#304d5a;">112</div>
</div>

<div class="helpline-card" style="background:#f5eeee;">
<div class="helpline-icon">👩</div>
<div class="helpline-name">Women Helpline</div>
<div class="helpline-number" style="color:#a34c63;">181</div>
</div>

<div class="helpline-card" style="background:#eef5f0;">
<div class="helpline-icon">🧒</div>
<div class="helpline-name">Child Helpline</div>
<div class="helpline-number" style="color:#39705a;">1098</div>
</div>

</div>

<div class="helpline-note">
For immediate danger, call 112.
</div>

</div>
""", unsafe_allow_html=True)


# ============================================================
# RESPONSE PROTOCOL
# ============================================================

steps = [
    ("01", "Official help"),
    ("02", "Confirm status"),
    ("03", "Nearby people"),
    ("04", "Safety guidance"),
    ("05", "Escalate")
]

cols = st.columns(5)

for col, (number, name) in zip(cols, steps):
    with col:
        st.markdown(
            f"""
            <div class="step-card">
                <div class="step-number">{number}</div>
                <div class="step-name">{name}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown("""
<div class="question-box">
    <div class="question-title">What's the situation?</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="input-hint">'
    'You can either select the options below, describe the incident, '
    'or use both.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# OPTION INPUTS
# ============================================================

st.markdown("**Type of emergency**")

emergency_type = st.pills(
    "Emergency type",
    [
        "Medical",
        "Accident",
        "Assault / threat",
        "Trapped / unsafe location",
        "Lost / unreachable",
        "Natural disaster"
    ],
    selection_mode="single",
    label_visibility="collapsed",
    key="emergency_type"
)


st.markdown("**Have you been able to contact them directly?**")

contact_status = st.pills(
    "Contact status",
    [
        "Yes, spoke to them",
        "No response",
        "Haven't tried yet"
    ],
    selection_mode="single",
    label_visibility="collapsed",
    key="contact_status"
)


st.markdown("**Do you know their exact location?**")

location_status = st.pills(
    "Location status",
    [
        "Yes, confirmed",
        "Rough idea only",
        "No idea"
    ],
    selection_mode="single",
    label_visibility="collapsed",
    key="location_status"
)


st.markdown("**Is anyone else nearby who could help?**")

nearby_help = st.pills(
    "Nearby help",
    [
        "Yes",
        "Not that I know of"
    ],
    selection_mode="single",
    label_visibility="collapsed",
    key="nearby_help"
)


# ============================================================
# DESCRIPTION
# ============================================================

st.markdown("**Describe the incident (optional)**")

situation = st.text_area(
    "Incident description",
    placeholder=(
        "Example: My friend had a bike accident near the college gate. "
        "She is injured and not responding to my calls."
    ),
    height=120,
    label_visibility="collapsed",
    key="situation"
)


# ============================================================
# EMERGENCY TYPE DETECTION FOR DESCRIPTION-ONLY INPUT
# ============================================================

def detect_emergency_type(description):

    text = description.lower()

    keyword_groups = {

        "medical": [
            "medical",
            "heart attack",
            "stroke",
            "fainted",
            "unconscious",
            "breathing problem",
            "not breathing",
            "bleeding",
            "seizure",
            "sick",
            "ill",
            "collapsed",
            "poison",
            "overdose"
        ],

        "accident": [
            "accident",
            "crash",
            "collision",
            "bike accident",
            "car accident",
            "road accident",
            "vehicle accident",
            "injured",
            "injury",
            "fell",
            "fall",
            "hit by a car"
        ],

        "assault": [
            "assault",
            "attack",
            "attacked",
            "threat",
            "threatened",
            "stalking",
            "stalker",
            "harassment",
            "harassed",
            "violence",
            "violent",
            "domestic violence",
            "following me",
            "following her",
            "following him"
        ],

        "trapped": [
            "trapped",
            "locked",
            "stuck",
            "unsafe location",
            "dangerous location",
            "can't get out",
            "cannot get out",
            "stranded"
        ],

        "lost": [
            "lost",
            "missing",
            "unreachable",
            "can't reach",
            "cannot reach",
            "not responding",
            "no response",
            "disappeared",
            "whereabouts unknown"
        ],

        "disaster": [
            "earthquake",
            "flood",
            "flooding",
            "cyclone",
            "storm",
            "landslide",
            "tsunami",
            "natural disaster",
            "disaster",
            "fire",
            "building collapse"
        ]
    }

    scores = {}

    for emergency, keywords in keyword_groups.items():
        scores[emergency] = sum(
            1 for keyword in keywords
            if keyword in text
        )

    best_type = max(
        scores,
        key=scores.get
    )

    if scores[best_type] == 0:
        return None

    return best_type


# ============================================================
# ACTION PLAN
# ============================================================

if st.button("Get Action Plan", key="get_action_plan", type="primary"):

    # --------------------------------------------------------
    # At least ONE thing must be provided:
    # options OR description.
    # --------------------------------------------------------

    any_option = any([
        emergency_type,
        contact_status,
        location_status,
        nearby_help
    ])

    has_description = bool(
        situation.strip()
    )

    if not any_option and not has_description:

        st.warning(
            "Please select at least one option or describe the incident."
        )

    else:

        # ----------------------------------------------------
        # Determine emergency type.
        #
        # Priority:
        # 1. Selected emergency type
        # 2. Detect it from description
        # ----------------------------------------------------

        if emergency_type:

            detected_type = emergency_type

        else:

            detected_type = detect_emergency_type(
                situation
            )

        if not detected_type:

            st.warning(
                "Please select the emergency type or describe "
                "the incident clearly enough to identify it."
            )

        else:

            try:

                # ------------------------------------------------
                # Build complete situation.
                # Missing option values are explicitly marked
                # instead of preventing the request.
                # ------------------------------------------------

                description_text = (
                    situation.strip()
                    if situation.strip()
                    else "No additional description provided."
                )

                contact_value = (
                    contact_status
                    if contact_status
                    else "Not provided"
                )

                location_value = (
                    location_status
                    if location_status
                    else "Not provided"
                )

                nearby_value = (
                    nearby_help
                    if nearby_help
                    else "Not provided"
                )

                with st.spinner(
                    "Preparing your action plan..."
                ):

                    response = generate_response(
                        detected_type,
                        contact_value,
                        location_value,
                        nearby_value,
                        description_text
                    )

                clean_response = str(response)

                # ------------------------------------------------
                # Clean Gemini/response formatting.
                # ------------------------------------------------

                clean_response = re.sub(
                    r"```(?:html|markdown|text)?",
                    "",
                    clean_response,
                    flags=re.IGNORECASE
                )

                clean_response = clean_response.replace(
                    "```",
                    ""
                )

                clean_response = re.sub(
                    r"<[^>]*>",
                    "",
                    clean_response
                )

                # Remove headings if the response contains them.
                clean_response = re.sub(
                    r"^\s*(SEVERITY|IMMEDIATE ACTIONS|WHAT TO AVOID|NEXT STEP)\s*:?\s*$",
                    "",
                    clean_response,
                    flags=re.IGNORECASE | re.MULTILINE
                )

                actions = []

                # ------------------------------------------------
                # Extract numbered actions.
                # ------------------------------------------------

                for line in clean_response.splitlines():

                    line = line.strip()

                    if not line:
                        continue

                    match = re.match(
                        r"^\s*(?:\*\*)?(\d+)[\.\)]\s+(.*?)(?:\*\*)?$",
                        line
                    )

                    if match:

                        action = match.group(2).strip()

                        action = action.replace(
                            "**",
                            ""
                        ).replace(
                            "__",
                            ""
                        )

                        if action:
                            actions.append(action)

                # ------------------------------------------------
                # Fallback: split paragraph into sentences.
                # ------------------------------------------------

                if not actions:

                    sentences = re.split(
                        r"(?<=[.!?])\s+",
                        clean_response
                    )

                    actions = [
                        sentence.strip()
                        for sentence in sentences
                        if sentence.strip()
                    ]

                actions = actions[:5]

                if not actions:
                    raise RuntimeError(
                        "No action plan was returned."
                    )

                # ------------------------------------------------
                # DISPLAY RESULT
                # ------------------------------------------------

                result_html = """
<div class="result-box">

<div class="result-title">
● &nbsp; RECOMMENDED ACTION PLAN
</div>
"""

                for i, action in enumerate(
                    actions,
                    1
                ):

                    safe_action = html.escape(
                        action
                    )

                    result_html += f"""
<div class="action-row">

<div class="action-number">
{i}
</div>

<div class="action-text">
{safe_action}
</div>

</div>
"""

                result_html += "</div>"

                # Save result so it survives Streamlit reruns.
                st.session_state["action_plan"] = result_html

                st.markdown(
                    st.session_state["action_plan"],
                    unsafe_allow_html=True
                )


            except Exception as e:

                print(
                    "Response Assist ERROR:",
                    repr(e)
                )

                st.error(
                    "Unable to generate the action plan. "
                )
                st.code(
                    repr(e)
                )


# ============================================================
# START OVER
# ============================================================

if st.session_state.get("action_plan"):

    if st.button(
        "Start Over",
        key="start_over",
        type="secondary"
    ):

        # Clear every input widget.
        st.session_state["emergency_type"] = None
        st.session_state["contact_status"] = None
        st.session_state["location_status"] = None
        st.session_state["nearby_help"] = None
        st.session_state["situation"] = ""

        # Clear the generated result.
        st.session_state["action_plan"] = None

        # Rerun so all widgets are recreated with empty values.
        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="disclaimer">
Prototype for demonstration purposes.
This tool is not a substitute for contacting official emergency services.
<br><br>
In any real emergency, call local emergency services immediately.
</div>
""", unsafe_allow_html=True)
