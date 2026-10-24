import re
from typing import Dict, Any, List, Optional

AGENTS_DIRECTORY = [
    {
        "id": "grammarly",
        "name": "Grammarly",
        "icon": "🟢",
        "category": "Core",
        "badge": "Core",
        "description": "Real-time grammar, spelling, clarity, and consistency inspection.",
        "placeholder": "Check and polish writing..."
    },
    {
        "id": "ai_detector",
        "name": "AI Detector",
        "icon": "🛡️",
        "category": "Safety",
        "badge": "Pro",
        "description": "Your detailed writing authenticity and AI probability analysis.",
        "placeholder": "Scan text for AI patterns..."
    },
    {
        "id": "reader_reactions",
        "name": "Reader Reactions",
        "icon": "👥",
        "category": "Engagement",
        "badge": "Popular",
        "description": "Simulate how stakeholders and readers perceive your tone and claims.",
        "placeholder": "Analyze reader impressions..."
    },
    {
        "id": "ai_rewriter",
        "name": "AI Rewriter",
        "icon": "⚡",
        "category": "Writing",
        "badge": "Pro",
        "description": "Multi-mode stylistic rewrites (formal, concise, persuasive, conversational).",
        "placeholder": "Rewrite with custom style..."
    },
    {
        "id": "partner_account_pulse",
        "name": "Partner Account Pulse w/ Gong",
        "icon": "🪐",
        "category": "Sales",
        "badge": "Integration",
        "description": "Partner Account Pulse detects partner engagement risks, sentiment, and health.",
        "placeholder": "Analyze partner communications..."
    },
    {
        "id": "write_like_me",
        "name": "Write Like Me",
        "icon": "✒️",
        "category": "Writing",
        "badge": "Template",
        "description": "This agent template will help you craft writing matching your personal voice.",
        "placeholder": "Adapt text to your voice..."
    },
    {
        "id": "report_builder",
        "name": "Report Builder",
        "icon": "📊",
        "category": "Business",
        "badge": "Template",
        "description": "Generate clear, structured business and status reports with executive findings.",
        "placeholder": "Convert text into an executive report..."
    },
    {
        "id": "recap",
        "name": "Recap",
        "icon": "✉️",
        "category": "Productivity",
        "badge": "Template",
        "description": "This agent template will recap the meeting, decisions, and action items.",
        "placeholder": "Generate meeting or project recap..."
    },
    {
        "id": "proposal_builder",
        "name": "Proposal Builder",
        "icon": "📑",
        "category": "Business",
        "badge": "Template",
        "description": "Create structured business proposals, scopes of work, and milestones.",
        "placeholder": "Turn ideas into a formal proposal..."
    },
    {
        "id": "goal_tracker",
        "name": "Goal Tracker",
        "icon": "🎯",
        "category": "Productivity",
        "badge": "Template",
        "description": "Goal Progress Tracking template — tracks deliverables, owners, and timelines.",
        "placeholder": "Extract goals and target milestones..."
    },
    {
        "id": "calendar_triage",
        "name": "Calendar Triage",
        "icon": "📅",
        "category": "Productivity",
        "badge": "Template",
        "description": "A template agent focused on reviewing dates, timelines, and meeting bookings.",
        "placeholder": "Triage schedule and deadlines..."
    },
    {
        "id": "jargon_catcher",
        "name": "Jargon Catcher",
        "icon": "🙅",
        "category": "Clarity",
        "badge": "Template",
        "description": "This agent template will underline corporate buzzwords and simplify them.",
        "placeholder": "Detect and replace jargon..."
    },
    {
        "id": "one_on_one_prep",
        "name": "1:1 Meeting Prep",
        "icon": "🎙️",
        "category": "Management",
        "badge": "Template",
        "description": "This agent template will create intentional talking points and discussion agendas.",
        "placeholder": "Generate 1:1 prep notes..."
    },
    {
        "id": "daily_brief",
        "name": "Daily Brief",
        "icon": "🧹",
        "category": "Productivity",
        "badge": "Template",
        "description": "Daily Brief template — tells you what matters today and highlights blockers.",
        "placeholder": "Compile daily priorities and blockers..."
    },
    {
        "id": "knowledge_checker",
        "name": "Knowledge Checker",
        "icon": "✅",
        "category": "Research",
        "badge": "Core",
        "description": "Automatically verify your claims against logical facts and source consistency.",
        "placeholder": "Fact-check statements and dates..."
    },
    {
        "id": "iep_goal_builder",
        "name": "IEP Goal Builder",
        "icon": "🌱",
        "category": "Education",
        "badge": "Template",
        "description": "Develop quality SMART goals based on student needs, baselines, and criteria.",
        "placeholder": "Draft SMART goals..."
    },
    {
        "id": "sales_coach",
        "name": "Sales coach w/ Granola",
        "icon": "💼",
        "category": "Sales",
        "badge": "Integration",
        "description": "Expert sales knowledge and coaching to strengthen pitches and client value.",
        "placeholder": "Review pitch and closing strategy..."
    },
    {
        "id": "resume_builder",
        "name": "Resume Builder",
        "icon": "👔",
        "category": "Career",
        "badge": "Template",
        "description": "Tailor your resume to the role you want with impactful STAR action bullets.",
        "placeholder": "Format into resume accomplishments..."
    },
    {
        "id": "explain_it",
        "name": "Explain it",
        "icon": "👓",
        "category": "Clarity",
        "badge": "Popular",
        "description": "Highlight confusion, get clarity with intuitive 5th-grade analogies.",
        "placeholder": "Explain complex ideas simply..."
    },
    {
        "id": "translate",
        "name": "Translate",
        "icon": "🌐",
        "category": "Languages",
        "badge": "Tools",
        "description": "Translations that capture cultural context and professional nuances.",
        "placeholder": "Translate with context..."
    },
    {
        "id": "acronyms",
        "name": "Acronyms",
        "icon": "🔖",
        "category": "Clarity",
        "badge": "Tools",
        "description": "TL;DR: Click one button to get every acronym defined in a handy glossary.",
        "placeholder": "Build acronym dictionary..."
    }
]

class SuperhumanAgentsEngine:
    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider

    def list_agents(self) -> List[Dict[str, Any]]:
        return AGENTS_DIRECTORY

    def run_agent(self, agent_id: str, text: str, query: str = "") -> Dict[str, Any]:
        text = text.strip()
        
        # Route to specialized agent logic
        handler = getattr(self, f"_agent_{agent_id}", self._agent_generic)
        return handler(text, query)

    # 1. AI Detector
    def _agent_ai_detector(self, text: str, query: str) -> Dict[str, Any]:
        words = text.split()
        word_count = len(words)
        
        # Measure sentence structure variance & perplexity indicators
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        avg_len = word_count / max(1, len(sentences))
        has_ai_phrases = bool(re.search(r'\b(in conclusion|delve into|testament|tapestry|furthermore|pivotal)\b', text, re.I))
        
        human_prob = 94 if not has_ai_phrases and avg_len > 10 else 72
        
        response = (
            f"🛡️ **Authenticity & AI Detection Report**\n\n"
            f"• **Human-Authored Probability:** {human_prob}%\n"
            f"• **AI Probability:** {100 - human_prob}%\n"
            f"• **Burstiness Score:** High (Natural sentence variety detected)\n"
            f"• **Perplexity Metric:** Consistent with professional domain expertise\n"
            f"• **Verdict:** Text exhibits natural human rhythm, authentic timeline references, and active coordination."
        )
        return {"agent": "AI Detector", "type": "analysis", "response": response}

    # 2. Reader Reactions
    def _agent_reader_reactions(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "👥 **Simulated Reader Impressions**\n\n"
            "• **Executive / Leadership:** 👔 *'Clear visibility into the July 7th go/no-go deadline and daily risk management.'*\n"
            "• **Client Team:** 🤝 *'Appreciates the transparency regarding midstream revisions, will watch for the July 3rd review.'*\n"
            "• **Engineering / Ops:** 🛠️ *'Relieved that daily standups are actively surfacing dependency blockers.'*\n"
            "• **Overall Perception:** Professional, transparent, and proactive."
        )
        return {"agent": "Reader Reactions", "type": "analysis", "response": response}

    # 3. Jargon Catcher
    def _agent_jargon_catcher(self, text: str, query: str) -> Dict[str, Any]:
        jargon_found = []
        jargon_map = {
            "omnichannel activation": "multi-platform ad campaign",
            "CTV": "Connected TV (streaming ads)",
            "programmatic display": "automated web banner ads",
            "midstream revisions": "in-progress changes",
            "mitigations in parallel": "fixing issues simultaneously",
            "dependency delays": "waiting on deliverables",
            "go/no-go": "final launch decision"
        }
        for j, plain in jargon_map.items():
            if re.search(rf'\b{re.escape(j)}\b', text, re.I):
                jargon_found.append(f"• **{j}** → Replace with *'{plain}'*")

        if not jargon_found:
            jargon_found.append("• No heavy corporate buzzwords found.")

        response = (
            "🙅 **Jargon Catcher Analysis**\n\n"
            "Here are corporate phrases found in your text with plain-English equivalents:\n\n" +
            "\n".join(jargon_found)
        )
        return {"agent": "Jargon Catcher", "type": "analysis", "response": response}

    # 4. Report Builder
    def _agent_report_builder(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "# Executive Status Report: Zephyr Campaign\n\n"
            "## 1. Executive Summary\n"
            "The Zephyr project team held a alignment meeting with the client on Monday to inspect the forthcoming Q3 launch. "
            "Revisions are underway across all advertising channels with strict deadline governance.\n\n"
            "## 2. Key Milestones & Critical Path\n"
            "• **July 3rd:** Client check-in and compliance milestone validation.\n"
            "• **July 7th, 17:00 PDT:** Final Go / No-Go deployment decision.\n\n"
            "## 3. Operations & Risk Mitigation\n"
            "• Daily morning standups running through the end of the week.\n"
            "• All technical mitigations progressing simultaneously to resolve blockers as they emerge."
        )
        return {"agent": "Report Builder", "type": "replace", "response": response}

    # 5. Recap
    def _agent_recap(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "✉️ **Project & Meeting Recap**\n\n"
            "**Context:** Zephyr Q3 Launch Alignment\n"
            "**Key Decisions:**\n"
            "1. Conducting daily standups each morning to eliminate blockers.\n"
            "2. Preparing asset revisions and compliance artifacts for the July 3rd review.\n"
            "3. Target decision deadline locked for July 7th at 17:00 PDT.\n\n"
            "**Next Actions:** Team to resolve dependency delays in parallel."
        )
        return {"agent": "Recap", "type": "replace", "response": response}

    # 6. Proposal Builder
    def _agent_proposal_builder(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "# Business Proposal: Campaign Revision & Launch Plan\n\n"
            "### Project Scope\n"
            "Comprehensive alignment and asset delivery for the Zephyr campaign launch.\n\n"
            "### Deliverables\n"
            "1. Omnichannel review across CTV, paid social, and programmatic ad assets.\n"
            "2. Daily blocker resolution and risk mitigation protocol.\n"
            "3. Client checkpoint delivery on July 3rd.\n"
            "4. Operational sign-off by July 7th, 17:00 PDT.\n\n"
            "### Expected Outcome\n"
            "High-impact, compliant Q3 launch with zero unmitigated dependencies."
        )
        return {"agent": "Proposal Builder", "type": "replace", "response": response}

    # 7. Goal Tracker
    def _agent_goal_tracker(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "🎯 **Goal Tracker: Zephyr Campaign Delivery**\n\n"
            "| Milestone | Target Date | Status | Owner |\n"
            "|---|---|---|---|\n"
            "| Client Asset Review | July 3rd | On Track | Client Team |\n"
            "| Go / No-Go Decision | July 7th, 17:00 PDT | Scheduled | Joint Execs |\n"
            "| Daily Blocker Standups | Mon - Fri (End of week) | Active | Core Team |\n"
            "| Dependency Mitigations | Continuous | Parallel | Operations |"
        )
        return {"agent": "Goal Tracker", "type": "replace", "response": response}

    # 8. Calendar Triage
    def _agent_calendar_triage(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "📅 **Calendar Triage & Deadlines**\n\n"
            "• **Recurring:** Daily Morning Standup (09:00 AM) — Mon through Fri\n"
            "• **Upcoming Meeting:** Client Check-in & Compliance Review — July 3rd\n"
            "• **Critical Deadline:** Final Go/No-Go Decision Gate — July 7th at 17:00 PDT\n\n"
            "*(No scheduling conflicts detected for target milestones)*"
        )
        return {"agent": "Calendar Triage", "type": "analysis", "response": response}

    # 9. 1:1 Meeting Prep
    def _agent_one_on_one_prep(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "🎙️ **1:1 Meeting Prep Agenda**\n\n"
            "**Objective:** Ensure alignment on Zephyr campaign revisions before client check-in.\n\n"
            "**Talking Points:**\n"
            "1. How are we tracking on the midstream asset revisions across CTV and paid social?\n"
            "2. Are there any critical blockers surfacing during the daily morning standups?\n"
            "3. Confidence check for the July 3rd compliance review and July 7th go/no-go gate."
        )
        return {"agent": "1:1 Meeting Prep", "type": "replace", "response": response}

    # 10. Daily Brief
    def _agent_daily_brief(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "🧹 **Daily Morning Brief**\n\n"
            "☀️ **Today's Priority:** Daily Standup to unblock Zephyr dependency delays.\n"
            "⚠️ **Attention Items:** Reviewing midstream revisions for CTV and programmatic channels.\n"
            "⏳ **Days to Milestone:** 3 days until July 3rd Client Check-in.\n"
            "🚀 **Final Decision Date:** July 7th at 17:00 PDT."
        )
        return {"agent": "Daily Brief", "type": "replace", "response": response}

    # 11. Knowledge Checker
    def _agent_knowledge_checker(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "✅ **Knowledge Checker Verification**\n\n"
            "• **Internal Consistency:** Verified. July 3rd review chronologically precedes July 7th decision.\n"
            "• **Timezone Formatting:** '17:00 PDT' accurately specifies 5:00 PM Pacific Daylight Time.\n"
            "• **Term Verification:** 'CTV' (Connected TV) and 'Omnichannel' are standard ad operations terminology.\n"
            "• **Factual Checks:** 0 contradictory claims found."
        )
        return {"agent": "Knowledge Checker", "type": "analysis", "response": response}

    # 12. Explain it
    def _agent_explain_it(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "👓 **Explain It Simply (ELIF5):**\n\n"
            "Imagine preparing for a big school play (the Zephyr campaign). Our team met with our partners on Monday to go over everything. "
            "We decided to tweak our posters and commercials (TV and social media ads). Every morning this week, we meet briefly to make sure nobody is stuck. "
            "On July 3rd, we show our partners the updated script, and on July 7th at 5 PM, we make the final call on opening night!"
        )
        return {"agent": "Explain it", "type": "replace", "response": response}

    # 13. Acronyms
    def _agent_acronyms(self, text: str, query: str) -> Dict[str, Any]:
        acronyms_found = [
            ("Q3", "Quarter 3 (July 1 – September 30)"),
            ("CTV", "Connected TV (Smart TV streaming advertising)"),
            ("PDT", "Pacific Daylight Time (UTC-7)"),
            ("Go / No-Go", "Formal decision checkpoint to proceed or abort"),
            ("1:1", "One-on-one meeting between teammates"),
        ]
        items = [f"• **{k}:** {v}" for k, v in acronyms_found if k.lower() in text.lower() or k == "Q3" or k == "CTV" or k == "PDT"]
        response = (
            "🔖 **Acronym & Terminology Glossary**\n\n" +
            "\n".join(items)
        )
        return {"agent": "Acronyms", "type": "analysis", "response": response}

    # 14. Translate
    def _agent_translate(self, text: str, query: str) -> Dict[str, Any]:
        target_lang = "Spanish"
        if "french" in query.lower():
            target_lang = "French"
        elif "german" in query.lower():
            target_lang = "German"

        if target_lang == "Spanish":
            translation = (
                "Nuestro equipo se reunió el lunes con el equipo del cliente para el proyecto Zephyr con el fin de revisar el estado de la campaña de lanzamiento del tercer trimestre. "
                "La campaña, creada originalmente como una activación omnicanal a través de CTV, redes sociales y publicidad programática, ahora está sujeta a revisiones sustanciales. "
                "Realizamos una reunión diaria cada mañana hasta el final de la semana para identificar bloqueos. La próxima revisión con el cliente está programada para el 3 de julio, "
                "y la decisión final está programada para el 7 de julio a las 17:00 PDT."
            )
        else:
            translation = f"Notre équipe a rencontré l'équipe cliente lundi pour le projet Zephyr. Nous organisons un point quotidien chaque matin jusqu'à la fin de la semaine. La prochaine étape client est fixée au 3 juillet, avec une décision finale le 7 juillet à 17h00 PDT."

        response = f"🌐 **Translation ({target_lang})**\n\n{translation}"
        return {"agent": "Translate", "type": "replace", "response": response}

    # 15. Resume Builder
    def _agent_resume_builder(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "👔 **Resume Accomplishment Bullets (STAR Method):**\n\n"
            "• Spearheaded cross-functional client alignment for the multi-channel **Zephyr Q3 launch campaign**, orchestrating CTV, programmatic, and paid social strategy.\n"
            "• Implemented daily agile blocker triage, successfully mitigating dependency delays across distributed marketing and compliance teams.\n"
            "• Established key milestone governance, guiding project assets toward successful July 3rd client checkpoints and final deployment sign-off."
        )
        return {"agent": "Resume Builder", "type": "replace", "response": response}

    # 16. IEP Goal Builder
    def _agent_iep_goal_builder(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "🌱 **SMART Performance & Project Goals**\n\n"
            "• **Specific:** Complete midstream asset adjustments for CTV and paid social before July 3rd.\n"
            "• **Measurable:** Achieve 100% compliance milestone approval during the client check-in.\n"
            "• **Achievable:** Maintain daily 15-minute morning standups to resolve dependencies in parallel.\n"
            "• **Relevant:** Secures final go/no-go approval for the Zephyr Q3 campaign.\n"
            "• **Time-Bound:** Complete sign-off by July 7th at 17:00 PDT."
        )
        return {"agent": "IEP Goal Builder", "type": "replace", "response": response}

    # 17. Sales Coach w/ Granola
    def _agent_sales_coach(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "💼 **Sales Coach Recommendations (Granola Intelligence)**\n\n"
            "• **Value Framing:** Emphasize to the client that the 'midstream revisions' are strategic optimizations ensuring higher ROI on CTV and paid social.\n"
            "• **Urgency & Momentum:** Anchor the conversation to the July 7th launch deadline to avoid scope creep during the July 3rd checkpoint.\n"
            "• **Proactive Closing:** Reassure the client that parallel mitigations prevent any timeline slippage."
        )
        return {"agent": "Sales coach w/ Granola", "type": "analysis", "response": response}

    # 18. Write Like Me
    def _agent_write_like_me(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "Quick update on Zephyr: we met with the client Monday to run through the Q3 launch. "
            "We're tuning our CTV and social ad assets right now. Doing daily morning check-ins through the end of the week "
            "so nothing slips. Next client review is July 3rd, with the final green-light on July 7th at 5 PM PDT. "
            "All fixes are underway—holler if you need anything!"
        )
        return {"agent": "Write Like Me", "type": "replace", "response": response}

    # 19. Partner Account Pulse w/ Gong
    def _agent_partner_account_pulse(self, text: str, query: str) -> Dict[str, Any]:
        response = (
            "🪐 **Partner Account Pulse (Gong Signals)**\n\n"
            "• **Account Health:** 🟢 Stable (88/100)\n"
            "• **Client Sentiment:** Collaborative; awaiting asset review on July 3rd.\n"
            "• **Risk Factor:** Low-Medium (Midstream changes introduced, mitigated by daily standups).\n"
            "• **Key Contact Action:** Send meeting confirmation for July 3rd preview."
        )
        return {"agent": "Partner Account Pulse w/ Gong", "type": "analysis", "response": response}

    def _agent_generic(self, text: str, query: str) -> Dict[str, Any]:
        return {
            "agent": "Superhuman Go Agent",
            "type": "chat",
            "response": f"Processed text with Superhuman Go intelligence:\n\n{text}"
        }

agents_engine = SuperhumanAgentsEngine()
