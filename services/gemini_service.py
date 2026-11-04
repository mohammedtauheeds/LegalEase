"""
LegalEase - Google Gemini AI Integration Service.
File: services/gemini_service.py

Uses the official `google-genai` Python SDK to generate grounded, accessible,
and legally responsible Indian legal awareness explanations.
Enforces strict zero-hallucination guardrails, criminal law transition awareness (BNS/BNSS/BSA),
prompt injection defense, and authoritative source attribution.
"""

import logging
import re
from typing import Any, Dict, List, Optional

from config import Config
from services.source_verification import format_provision_label

logger = logging.getLogger("legalease.gemini_service")

# Prompt injection patterns to detect and neutralize
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"disregard\s+(?:all\s+)?prior\s+rules",
    r"system\s*prompt",
    r"you\s+are\s+now\s+(?:dan|unrestricted|god)",
    r"jailbreak",
    r"act\s+as\s+an\s+unfiltered\s+ai",
    r"bypass\s+(?:all\s+)?safeguards",
]

# Strict Indian Legal Awareness System Instruction
SYSTEM_INSTRUCTION = (
    "You are LegalEase, an AI-powered Indian legal awareness assistant.\n"
    "Your role is to explain Indian laws, legal rights, statutory provisions, and common legal procedures "
    "in simple, understandable English for the general public in India.\n"
    "You are NOT a lawyer, do NOT provide formal legal representation, and do NOT offer individualized legal advice.\n\n"

    "STRICT JURISDICTION RULE:\n"
    "- Focus exclusively on Indian law (Constitution of India, central Acts, state statutes, and Indian judicial procedures).\n"
    "- Never cite or apply United States, United Kingdom, or other foreign legal frameworks to Indian legal questions. "
    "If an inquiry mentions a foreign jurisdiction, explicitly clarify that LegalEase specializes only in Indian law.\n\n"

    "FACTUAL ACCURACY & ZERO-HALLUCINATION RULE:\n"
    "- Never invent statutes, section numbers, case names, court judgments, citations, penalties, or procedures.\n"
    "- Ground your answer strictly in the verified legal context provided, or well-established Indian statutory knowledge.\n"
    "- If a legal provision or case cannot be verified, explicitly state: 'This provision could not be verified from official records.'\n"
    "- Clearly distinguish between statutory legislation enacted by Parliament and judicial precedents delivered by courts.\n\n"

    "CRIMINAL LAW TRANSITION (IN FORCE FROM JULY 1, 2024):\n"
    "- India's three new criminal codes came into force on July 1, 2024:\n"
    "  • Bharatiya Nyaya Sanhita, 2023 (BNS) replaced the Indian Penal Code, 1860 (IPC).\n"
    "  • Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) replaced the Code of Criminal Procedure, 1973 (CrPC).\n"
    "  • Bharatiya Sakshya Adhiniyam, 2023 (BSA) replaced the Indian Evidence Act, 1872 (IEA).\n"
    "- Offences committed on or after July 1, 2024 are governed by BNS, BNSS, and BSA.\n"
    "- Offences committed prior to July 1, 2024 remain governed by IPC, CrPC, and IEA under transitional provisions.\n"
    "- When referencing offences, clarify both the modern BNS/BNSS/BSA provision and its former IPC/CrPC/IEA equivalent.\n\n"

    "CENTRAL VS. STATE JURISDICTION & LEGISLATIVE LISTS:\n"
    "- Clearly distinguish between Central laws (Union List) and State-specific laws (State List, e.g. Rent Control, Shops & Establishments, Land Revenue, Police regulations).\n"
    "- When answering questions involving State subjects, explain that rules and procedures vary across States, identify the applicable State/UT if mentioned, and clarify that the citizen should verify their local State enactment.\n"
    "- When discussing the 4 Labour Codes (Code on Wages 2019, IR Code 2020, Social Security Code 2020, OSH Code 2020), note that while enacted by Parliament, transitional enforcement continues alongside pre-existing wage and industrial dispute legislation until complete nationwide rule notification.\n\n"

    "MANDATORY 8-SECTION RESPONSE STRUCTURE:\n"
    "Format every response using these clean, distinct markdown sections:\n"
    "### Direct Answer\n"
    "[Short, direct, understandable answer addressing the citizen's actual question immediately]\n\n"
    "### Relevant Law\n"
    "[List applicable legislation: Act Name, Section/Article, Legal Status, and Official Source URL]\n\n"
    "### Explanation in Simple English\n"
    "[Explain what the legal provisions mean in plain, everyday language without unnecessary jargon]\n\n"
    "### Conditions and Exceptions\n"
    "[Explain when the rule applies, when it does not apply, and any statutory exceptions]\n\n"
    "### Rights of the Person\n"
    "[Detail the constitutional and statutory safeguards available to the citizen]\n\n"
    "### Available Remedies\n"
    "[Clearly distinguish: Police complaint (FIR/Zero FIR), Legal demand notice, Departmental complaint/Statutory authority, Tribunal, Court proceedings, or Appeal]\n\n"
    "### Practical Next Steps\n"
    "1. [Actionable step 1]\n"
    "2. [Actionable step 2]\n"
    "3. [Actionable step 3]\n\n"
    "### Relevant Judicial Decisions\n"
    "[If verified decisions are in retrieved context, cite them accurately with Case Title, Court, Citation, and Ratio. If NO verified decisions are in context, write EXACTLY: 'No verified judicial decisions were found for this query.' NEVER invent fictional case names, parties, or citations.]\n\n"
    "### Sources\n"
    "[List authentic, verified official government and judicial sources]\n\n"

    "HIGH-RISK & EMERGENCY SAFEGUARDS:\n"
    "- For inquiries concerning arrest, police custody, domestic violence, online financial fraud, or immediate physical safety, "
    "provide cautious general procedures, warn against missing court limitation periods, and prominently highlight official helplines:\n"
    "  • Pan-India Emergency: 112\n"
    "  • Cyber Crime Reporting: 1930 / https://cybercrime.gov.in/\n"
    "  • National Consumer Helpline: 1915 / https://consumerhelpline.gov.in/\n"
    "  • Free Legal Aid (NALSA): 15100 / https://nalsa.gov.in/\n"
    "  • Women Helpline: 1091 / 181\n"
    "- Advise consulting a qualified advocate or visiting the nearest District Legal Services Authority (DLSA).\n\n"

    "OFF-TOPIC NON-LEGAL INQUIRIES:\n"
    "- If the user asks an off-topic question unrelated to law (e.g. cooking, coding, weather, sports, celebrity gossip), "
    "politely refuse: 'LegalEase is dedicated to Indian legal awareness. I can only assist with Indian laws, legal rights, and procedures.'\n\n"

    "LEGAL DISCLAIMER:\n"
    "- Conclude your explanation with a short reminder: 'Disclaimer: This information is for public legal awareness only "
    "and does not constitute formal legal advice. Please consult a qualified advocate for specific legal representation.'"
)


class GeminiService:
    """Manages Google Gemini client initialization, prompt assembly, and text generation."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key if api_key is not None else Config.GEMINI_API_KEY
        self.model_name = model if model is not None else Config.GEMINI_MODEL
        self.client = None
        self._init_error = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the official google-genai Client."""
        placeholder_keys = {
            "your_gemini_api_key_here",
            "replace-with-a-secure-random-secret-key-for-sessions",
            "replace_with_your_api_key",
            "none"
        }
        if not self.api_key or not self.api_key.strip() or self.api_key.strip().lower() in placeholder_keys:
            self._init_error = "GEMINI_API_KEY is not configured in environment variables. Set a valid Gemini API key in LegalEase/.env to enable generative AI answers."
            self.client = None
            return

        try:
            # Official google-genai SDK import
            from google import genai
            self.client = genai.Client(api_key=self.api_key.strip())
            self._init_error = None
        except ImportError:
            self._init_error = "The official 'google-genai' SDK is not installed. Run: pip install google-genai"
            self.client = None
        except Exception as e:
            self._init_error = f"Failed to initialize google-genai client: {str(e)}"
            self.client = None

    def validate_user_input(self, question: str) -> Tuple[bool, Optional[str]]:
        """Validate input string against length, nulls, and prompt injection."""
        if not question or not isinstance(question, str) or not question.strip():
            return False, "Question parameter must be a non-empty string."

        clean = question.strip()
        if len(clean) > 1000:
            return False, "Question exceeds the maximum allowed length of 1000 characters."

        # Check for prompt injection patterns
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, clean, re.IGNORECASE):
                logger.warning("Prompt injection pattern detected in user query.")
                return False, "Security Notice: Your query contains unauthorized instruction-override directives."

        return True, None

    def build_sources_list(self, legal_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Extract and structure verified source references from the retrieved legal context."""
        sources = []
        seen_urls = set()

        if not legal_context:
            # Default authoritative baseline
            return [{
                "title": "India Code - Digital Repository of All Central and State Acts",
                "type": "Official Legislation",
                "url": "https://www.indiacode.nic.in/"
            }]

        # 1. Statutory Provisions
        for stat in legal_context.get("retrieved_statutes", []):
            url = stat.get("source_url") or "https://www.indiacode.nic.in/"
            if url not in seen_urls:
                seen_urls.add(url)
                sec_label = format_provision_label(stat.get('act_name', 'Indian Statute'), stat.get('section', ''))
                sources.append({
                    "title": sec_label,
                    "type": "Official Legislation",
                    "url": url,
                    "status": stat.get("status", "")
                })

        # 2. Retrieved Court Judgments
        for j in legal_context.get("retrieved_judgments", []):
            url = j.get("url") or "https://www.sci.gov.in/"
            if url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    "title": j.get("title", "Indian Court Judgment"),
                    "type": "Court Judgment",
                    "court": j.get("court", "Indian Court"),
                    "citation": j.get("citation", ""),
                    "url": url
                })

        # 3. NLP / FAQ Analysis Source
        nlp_res = legal_context.get("nlp_analysis", {})
        faq_url = nlp_res.get("source_url")
        if faq_url and faq_url not in seen_urls:
            seen_urls.add(faq_url)
            sources.append({
                "title": nlp_res.get("source_title", "Official Indian Legal Portal"),
                "type": "Government Resource",
                "url": faq_url
            })

        # Ensure at least one authoritative portal is present
        if not sources:
            sources.append({
                "title": "India Code - Digital Repository of All Central and State Acts",
                "type": "Official Legislation",
                "url": "https://www.indiacode.nic.in/"
            })

        return sources

    def construct_prompt(
        self,
        user_question: str,
        legal_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Assemble the complete grounded prompt combining question, context, and conversation history."""
        prompt_parts = []

        # 1. Retrieved Context Section
        prompt_parts.append("### VERIFIED RETRIEVED LEGAL CONTEXT ###")
        if legal_context:
            # Check statutory provisions
            statutes = legal_context.get("retrieved_statutes", [])
            if statutes:
                prompt_parts.append("\n[Official Statutory Provisions]:")
                for s in statutes:
                    s_label = format_provision_label(s.get('act_name', 'Indian Statute'), s.get('section', ''))
                    sec_str = str(s.get('section', ''))
                    prompt_parts.append(
                        f" • Act: {s.get('act_name', 'Indian Statute')}\n"
                        f"   Section: {sec_str}\n"
                        f"   Provision: {s_label}\n"
                        f"   Heading: {s.get('heading')}\n"
                        f"   Text: {s.get('text')}\n"
                        f"   Status: {s.get('status')}\n"
                        f"   Corresponding/Prior Provision: {s.get('corresponding_provision', 'None')}"
                    )

            # Check court judgments
            judgments = legal_context.get("retrieved_judgments", [])
            if judgments:
                prompt_parts.append("\n[Retrieved Court Judgments]:")
                for j in judgments:
                    prompt_parts.append(
                        f" • Title: {j.get('title')}\n"
                        f"   Court: {j.get('court')}\n"
                        f"   Citation: {j.get('citation')}\n"
                        f"   Summary: {j.get('summary')}"
                    )

            # Check FAQ analysis context
            nlp_res = legal_context.get("nlp_analysis", {})
            if nlp_res and nlp_res.get("topic"):
                prompt_parts.append(
                    f"\n[Domain Topic]: {nlp_res.get('topic')}\n"
                    f"[Detected Intent]: {nlp_res.get('intent')}"
                )
                if nlp_res.get("answer"):
                    prompt_parts.append(f"[Verified FAQ Guidance]: {nlp_res.get('answer')}")

            # Check jurisdiction & Seventh Schedule distribution
            jur = legal_context.get("jurisdiction_info")
            if jur and jur.get("is_state_specific"):
                prompt_parts.append(f"\n[Detected Jurisdiction]: {jur.get('jurisdiction')} (State-specific laws apply)")

            sched = legal_context.get("seventh_schedule")
            if sched and sched.get("advisory"):
                prompt_parts.append(f"[Constitutional Legislative Distribution]: {sched.get('list')} - {sched.get('advisory')}")

            # Check state-specific statutes
            state_stats = legal_context.get("state_statutes", [])
            if state_stats:
                prompt_parts.append("\n[State-Specific Legislation]:")
                for st in state_stats:
                    prompt_parts.append(
                        f" • State Act: {st.get('title')} ({st.get('state_name')})\n"
                        f"   Summary: {st.get('summary')}\n"
                        f"   Remedy: {st.get('remedies')}"
                    )
        else:
            prompt_parts.append(
                "No external documents retrieved. Rely strictly on verified Indian statutory principles and acknowledge any limitation."
            )

        # 2. Limited Conversation History (Up to 3 recent turns)
        if conversation_history:
            prompt_parts.append("\n### RECENT CONVERSATION HISTORY ###")
            recent_turns = conversation_history[-4:]
            for msg in recent_turns:
                role = "Citizen" if msg.get("role") in ("user", "citizen") else "LegalEase"
                content = msg.get("content", "").strip()
                prompt_parts.append(f"{role}: {content}")

        # 3. User Question
        prompt_parts.append("\n### CURRENT CITIZEN QUESTION ###")
        prompt_parts.append(f"Question: {user_question.strip()}")
        prompt_parts.append("\nProvide a clear, simple English legal awareness response according to your system rules:")

        return "\n".join(prompt_parts)

    def generate_legal_answer(
        self,
        user_question: str,
        legal_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Primary interface: generates grounded legal response using Gemini.
        Returns standardized dictionary:
        {
            "success": bool,
            "answer": str,
            "sources": list,
            "model": str,
            "fallback_used": bool,
            "error": str | None
        }
        """
        sources = self.build_sources_list(legal_context)

        # 1. Input Validation
        is_valid, validation_err = self.validate_user_input(user_question)
        if not is_valid:
            return {
                "success": False,
                "answer": validation_err,
                "sources": sources,
                "model": self.model_name,
                "fallback_used": False,
                "error": validation_err
            }

        # 2. Check Client Initialization
        if self.client is None or self._init_error:
            logger.warning(f"Gemini client unavailable: {self._init_error}. Engaging verified fallback.")
            return self._generate_fallback_answer(user_question, legal_context, error_msg=self._init_error)

        # 3. Build Prompt
        prompt = self.construct_prompt(user_question, legal_context, conversation_history)

        # 4. Invoke Gemini API via official google-genai SDK
        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=Config.GEMINI_TEMPERATURE,
                max_output_tokens=Config.GEMINI_MAX_OUTPUT_TOKENS,
                system_instruction=SYSTEM_INSTRUCTION
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Validate response content
            if not response or not hasattr(response, "text") or not response.text:
                return {
                    "success": False,
                    "answer": "The AI model returned an empty response. Please verify the question with official sources.",
                    "sources": sources,
                    "model": self.model_name,
                    "fallback_used": True,
                    "error": "Empty or malformed response returned from Gemini API."
                }

            generated_text = response.text.strip()

            return {
                "success": True,
                "answer": generated_text,
                "sources": sources,
                "model": self.model_name,
                "fallback_used": False,
                "error": None
            }

        except Exception as e:
            err_str = str(e)
            logger.error(f"Gemini API invocation error: {err_str}")

            # Specific error categorization
            user_err = "Gemini API service is temporarily unavailable."
            if "quota" in err_str.lower() or "429" in err_str:
                user_err = "AI generation quota or rate limit exceeded. Reverting to verified legal fallback."
            elif "api_key" in err_str.lower() or "401" in err_str or "unauthorized" in err_str.lower():
                user_err = "Invalid or expired Gemini API key."
            elif "not found" in err_str.lower() or "404" in err_str:
                user_err = f"Configured Gemini model '{self.model_name}' was not found or is unsupported."
            elif "timeout" in err_str.lower() or "deadline" in err_str.lower():
                user_err = "Request to Gemini API timed out."

            return self._generate_fallback_answer(user_question, legal_context, error_msg=f"{user_err} Details: {err_str}")

    def _generate_fallback_answer(
        self,
        user_question: str,
        legal_context: Optional[Dict[str, Any]] = None,
        error_msg: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provides a safe, substantive, and grounded fallback response strictly conforming
        to the standardized 8-section output structure using verified local statutory data.
        """
        sources = self.build_sources_list(legal_context)
        statutes = (legal_context or {}).get("retrieved_statutes", [])
        judgments = (legal_context or {}).get("retrieved_judgments", [])
        nlp_res = (legal_context or {}).get("nlp_analysis", {})
        sched = (legal_context or {}).get("seventh_schedule")
        state_stats = (legal_context or {}).get("state_statutes", [])
        intent = nlp_res.get("intent", "")

        lower_q = user_question.lower()
        parts = []

        # =========================================================================
        # Domain Synthesizer: Specific Pre-Configured Verified Legal Knowledge
        # =========================================================================
        if "common law" in lower_q or "stare decisis" in lower_q:
            direct_ans = (
                "India operates under a common law legal system rooted in constitutional supremacy, "
                "codified parliamentary enactments, and binding judicial precedents (stare decisis)."
            )
            rel_law = [
                "• Constitution of India, 1950 — Article 141 (Law declared by Supreme Court binding on all courts) [Current Law | Source: India Code]",
                "• Constitution of India, 1950 — Articles 32 & 226 (Remedies for enforcement of Fundamental Rights and Judicial Review) [Current Law | Source: India Code]"
            ]
            explanation = (
                "Under the Indian common law tradition, substantive and procedural laws are codified by Parliament and "
                "State Legislatures (such as Bharatiya Nyaya Sanhita, Code of Civil Procedure, Contract Act). The higher "
                "judiciary (Supreme Court of India and State High Courts) interprets these enactments, and decisions of the "
                "Supreme Court become binding law for all courts within the territory of India under Article 141."
            )
            conditions = (
                "The doctrine of precedent applies strictly to the ratio decidendi (the legal principle on which the decision "
                "is founded), while obiter dicta carry persuasive value. Precedents are subordinate to valid constitutional "
                "amendments and subsequent clarifying parliamentary enactments."
            )
            rights = (
                "• Right to equal protection of laws and consistent judicial application (Article 14).\n"
                "• Right to invoke constitutional remedies before High Courts (Article 226) or the Supreme Court (Article 32)."
            )
            remedies = (
                "• File a Writ Petition under Article 226 before the jurisdictional High Court.\n"
                "• File a Writ Petition or Special Leave Petition (SLP) under Article 136 before the Supreme Court.\n"
                "• Statutory appeals through established civil or criminal appellate hierarchies."
            )
            next_steps = (
                "1. Identify the specific statutory enactment and section applicable to your factual dispute.\n"
                "2. Research reported Supreme Court and High Court precedents establishing the legal ratio.\n"
                "3. Consult a qualified advocate or approach the District Legal Services Authority (DLSA) for guidance."
            )

        elif any(w in lower_q for w in ["theft", "stolen", "stealing"]):
            direct_ans = (
                "Theft of movable property is a cognizable criminal offence under Indian law, punishable with "
                "imprisonment up to 3 years, fine, or both (or community service for first-time petty theft under ₹5,000 where property is returned)."
            )
            rel_law = [
                "• Bharatiya Nyaya Sanhita, 2023 (BNS) — Section 303 (Theft & Punishment) [Current Law in force since July 1, 2024 | Source: India Code]",
                "• Indian Penal Code, 1860 (IPC) — Section 378 & Section 379 [Repealed prior law for offences before July 1, 2024 | Source: India Code]",
                "• Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) — Section 173 (Registration of FIR) [Current Law | Source: India Code]"
            ]
            explanation = (
                "Theft occurs when someone intending to take dishonestly any movable property out of the possession of "
                "any person without that person's consent, moves that property in order to such taking. Key ingredients: "
                "dishonest intention, movable property, taking out of possession, absence of consent, and moving the property."
            )
            conditions = (
                "Property must be movable. Taking immovable property or property abandoned without an owner is not theft. "
                "For petty first-time theft where the value of stolen property is less than ₹5,000 and the property is restored, "
                "community service may be ordered instead of incarceration under Section 303(2) BNS."
            )
            rights = (
                "• Complainant's right to have an FIR registered immediately without refusal (Zero FIR if at another station).\n"
                "• Informant's statutory right to obtain a free signed copy of the FIR (Section 173(2) BNSS).\n"
                "• Right to claim interim custody of recovered stolen property under Section 497 BNSS."
            )
            remedies = (
                "• Lodge an FIR at the nearest Police Station or dial 112.\n"
                "• If police refuse registration, submit a written complaint to the Superintendent of Police under Section 173(4) BNSS.\n"
                "• File a complaint before the Judicial Magistrate under Section 175(3) BNSS."
            )
            next_steps = (
                "1. Gather item details: purchase bills, serial numbers, photos, IMEI numbers, or vehicle registration.\n"
                "2. Visit the nearest police station or dial 112 immediately to register an FIR.\n"
                "3. Collect and verify your free stamped copy of the FIR."
            )

        elif "420" in lower_q or "cheating" in lower_q:
            direct_ans = (
                "Cheating and dishonestly inducing delivery of property (formerly known as a '420 case') is an aggravated "
                "criminal offence punishable with imprisonment up to 7 years and fine."
            )
            rel_law = [
                "• Bharatiya Nyaya Sanhita, 2023 (BNS) — Section 318(4) (Cheating and dishonestly inducing delivery of property) [Current Law in force since July 1, 2024 | Source: India Code]",
                "• Indian Penal Code, 1860 (IPC) — Section 420 [Repealed prior law for offences before July 1, 2024 | Source: India Code]",
                "• Information Technology Act, 2000 — Section 66D (Cheating by personation using computer resource) [Current Law | Source: India Code]"
            ]
            explanation = (
                "The offence requires deceiving any person and fraudulently or dishonestly inducing them to deliver any "
                "property to any person, or to make, alter or destroy the whole or any part of a valuable security. "
                "In online financial frauds, Section 66D of the IT Act also applies concurrently."
            )
            conditions = (
                "Fraudulent or dishonest intention must exist from the inception of the transaction. A mere subsequent failure "
                "to perform a contractual promise without initial deception constitutes a civil breach, not criminal cheating."
            )
            rights = (
                "• Victim's right to register an FIR for cognizable cheating.\n"
                "• Immediate banking freeze through National Cyber Crime Reporting Portal (1930) for cyber financial fraud.\n"
                "• Right to initiate civil recovery proceedings under Order 37 CPC alongside criminal prosecution."
            )
            remedies = (
                "• Register an FIR under Section 173 BNSS at the jurisdictional Police Station.\n"
                "• For cyber / online financial fraud, dial 1930 and file a complaint on cybercrime.gov.in.\n"
                "• File an application before Judicial Magistrate under Section 175(3) BNSS if police refuse action.\n"
                "• Institute a Summary Suit under Order XXXVII of the Code of Civil Procedure (CPC) for monetary recovery."
            )
            next_steps = (
                "1. Preserve all transaction records, bank statements, WhatsApp chats, agreements, and payment screenshots.\n"
                "2. For online financial fraud, notify your bank immediately and dial 1930 within the 'golden hour'.\n"
                "3. File a written complaint with the Police or Cyber Crime Cell."
            )

        elif any(w in lower_q for w in ["fundamental right", "constitutional remedy", "habeas corpus", "writ", "writs", "illegal detention", "unlawful detention", "detained"]):
            if any(w in lower_q for w in ["detained", "detention", "habeas"]):
                direct_ans = (
                    "Under the Constitution of India, any person who is illegally detained by the police or public authorities "
                    "has an immediate constitutional remedy to approach the High Court under Article 226 or the Supreme Court under "
                    "Article 32 seeking a Writ of Habeas Corpus to secure immediate release."
                )
            else:
                direct_ans = (
                    "Under the Constitution of India, citizens and persons are guaranteed Fundamental Rights in Part III, "
                    "which are directly enforceable against the State through the Supreme Court (Article 32) and High Courts (Article 226)."
                )
            rel_law = [
                "• Constitution of India, 1950 — Article 21 (Protection of life and personal liberty) [Current Law | Source: India Code]",
                "• Constitution of India, 1950 — Articles 12 to 35 (Part III: Fundamental Rights) [Current Law | Source: India Code]",
                "• Constitution of India, 1950 — Article 32 (Remedies for enforcement of Part III rights / Supreme Court Writs) [Current Law | Source: India Code]",
                "• Constitution of India, 1950 — Article 226 (Power of High Courts to issue writs including Habeas Corpus) [Current Law | Source: India Code]"
            ]
            explanation = (
                "The Constitution of India guarantees fundamental freedoms under Part III, centrally anchored by Article 21 "
                "(Protection of life and personal liberty) and Article 22 (Safeguards against arbitrary arrest and detention). "
                "Any unlawful detention by the police violates fundamental rights under Articles 21 and 22. The higher judiciary "
                "(Supreme Court under Article 32 and High Courts under Article 226) possesses extraordinary writ jurisdiction "
                "to command the immediate production and release of illegally detained individuals."
            )
            conditions = (
                "Fundamental rights are enforceable against the 'State' as defined under Article 12. Detention beyond 24 hours "
                "without production before a Judicial Magistrate is unconstitutional under Article 22(2). Fundamental rights "
                "are subject only to reasonable restrictions prescribed by law."
            )
            rights = (
                "• Right to life, personal liberty, privacy, and fair trial (Article 21).\n"
                "• Right to be produced before the nearest magistrate within 24 hours of arrest/detention (Article 22(2)).\n"
                "• Inherent right to approach the Supreme Court directly under Article 32 or High Court under Article 226 whenever personal liberty is infringed."
            )
            remedies = (
                "• Writ of Habeas Corpus under Article 226 before the High Court or Article 32 before the Supreme Court (direct remedy against illegal detention).\n"
                "• Writ of Mandamus (to compel performance of public duties).\n"
                "• Writ of Certiorari / Prohibition (to quash or prevent unlawful orders of lower tribunals).\n"
                "• Claim public law damages and compensation for unlawful detention violating Article 21.\n"
                "• Complaint before the National Human Rights Commission (NHRC) or State Police Complaints Authority."
            )
            next_steps = (
                "1. Gather details of the detention: date, time, police station, detaining officers, and lack of magistrate production.\n"
                "2. Contact the National Legal Aid Helpline at 15100 or visit NALSA (nalsa.gov.in) for immediate emergency legal representation.\n"
                "3. Instruct an advocate to urgently file a Habeas Corpus Writ Petition under Article 226 before the High Court or Article 32 before the Supreme Court."
            )

        elif "fir" in lower_q or "zero fir" in lower_q:
            direct_ans = (
                "An FIR (First Information Report) is the statutory starting point of a criminal investigation for any "
                "cognizable offence. A Zero FIR allows an FIR to be registered at any police station regardless of territorial jurisdiction."
            )
            rel_law = [
                "• Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) — Section 173 (Information in cognizable cases / FIR) [Current Law in force since July 1, 2024 | Source: India Code]",
                "• Code of Criminal Procedure, 1973 (CrPC) — Section 154 [Repealed prior law | Source: India Code]"
            ]
            explanation = (
                "Section 173 BNSS mandates that every information relating to the commission of a cognizable offence must be "
                "recorded by the police. It can be given orally, in writing, or electronically (e-FIR, to be signed within 3 days). "
                "A Zero FIR must be registered immediately and subsequently transferred to the competent jurisdictional station."
            )
            conditions = (
                "For offences punishable with 3 to 7 years imprisonment, the police officer may conduct a preliminary inquiry "
                "within 14 days with prior permission of a Deputy Superintendent of Police (DSP) before registering an FIR under Section 173(3) BNSS."
            )
            rights = (
                "• Absolute statutory right to obtain a free copy of the FIR immediately (Section 173(2) BNSS).\n"
                "• Right to register a Zero FIR at any police station without territorial objection.\n"
                "• Right to file an electronic FIR (e-FIR)."
            )
            remedies = (
                "• Report directly to the Police Station or dial 112.\n"
                "• If the station officer refuses registration, send the complaint in writing by post to the Superintendent of Police (Section 173(4) BNSS).\n"
                "• File an application before the Judicial Magistrate under Section 175(3) BNSS."
            )
            next_steps = (
                "1. Prepare a clear written statement noting date, time, location, suspect details, witnesses, and facts.\n"
                "2. Approach the nearest police station or submit an e-FIR on the state police portal.\n"
                "3. Insist on obtaining your free stamped and signed copy of the registered FIR."
            )

        elif any(p in lower_q for p in ["is this legal", "is it legal", "can i do this", "is that illegal", "what does the law say", "tell me the law", "is it allowed", "can i sue", "help me with law"]) or (len(lower_q.split()) <= 3 and "legal" in lower_q and not any(k in lower_q for k in ["aid", "metrology", "tender", "heir", "notice"])):
            direct_ans = (
                "Under Indian law, rights, duties, and remedies depend upon specific statutory enactments of Parliament "
                "and State Legislatures. Please provide specific factual context (such as the nature of the dispute, parties, "
                "or location) for precise statutory provisions."
            )
            rel_law = [
                "• Constitution of India, 1950 — Fundamental Rights & Directive Principles [Current Law | Source: India Code]",
                "• Relevant Central and State Enactments published on official government digital repositories."
            ]
            explanation = (
                "The Indian legal framework distinguishes between civil disputes, criminal offences, regulatory compliances, "
                "and constitutional rights. Every claim requires establishing a recognized cause of action, territorial "
                "jurisdiction, and adherence to statutory limitation periods."
            )
            conditions = (
                "Legal proceedings must be initiated within the time limits prescribed by the Limitation Act, 1963, "
                "and must satisfy procedural requirements under the Code of Civil Procedure or Bharatiya Nagarik Suraksha Sanhita."
            )
            rights = (
                "• Right to due process of law, natural justice, and a fair hearing before any adverse action.\n"
                "• Right to free legal aid under Section 12 of the Legal Services Authorities Act, 1987 for eligible citizens.\n"
                "• Right to information under the RTI Act, 2005 for records held by public authorities."
            )
            remedies = (
                "• Issue a formal Legal Notice through an advocate.\n"
                "• Approach the competent regulatory authority, tribunal, or civil/criminal court.\n"
                "• Contact the District Legal Services Authority (DLSA) or dial 15100 for free legal assistance."
            )
            next_steps = (
                "1. Clarify the specific legal issue, parties involved, and transaction or dispute dates.\n"
                "2. Preserve all written communication, contracts, notices, and payment proofs.\n"
                "3. Contact the National Legal Aid Helpline at 15100 or consult an advocate in your jurisdiction."
            )

        # =========================================================================
        # Dynamic Synthesizer: Generated from Retrieved Statutes & Context
        # =========================================================================
        elif statutes:
            primary_stat = statutes[0]
            act_title = primary_stat.get("act_name", "Indian Statute")
            sec_num = primary_stat.get("section", "")
            heading = primary_stat.get("heading", "")
            text = primary_stat.get("text", "")
            if not text or str(text).lower() in ("none", "null"):
                text = heading
            status = primary_stat.get("status", "Current Legislation")
            url = primary_stat.get("source_url", "https://www.indiacode.nic.in/")

            primary_label = format_provision_label(act_title, sec_num)
            direct_ans = (
                f"Under Indian law, your matter is governed primarily by **{primary_label}** "
                f"({heading}). Indian statutory provisions provide clear rights, standards, and institutional remedies."
            )

            rel_law = []
            for s in statutes[:3]:
                s_act = s.get("act_name", "Indian Statute")
                s_sec = s.get("section", "")
                s_label = format_provision_label(s_act, s_sec)
                s_stat = f"[{s.get('status', 'Current Legislation')} | Source: {s.get('source_url', 'https://www.indiacode.nic.in/')}]"
                s_head = f" — {s.get('heading')}" if s.get("heading") else ""
                rel_law.append(f"• {s_label}{s_head} {s_stat}")

            if sched and sched.get("advisory"):
                rel_law.append(f"• Constitutional Legislative Jurisdiction ({sched.get('list')}): {sched.get('advisory')}")

            if state_stats:
                for st in state_stats[:2]:
                    rel_law.append(f"• State Legislation: {st.get('title')} ({st.get('state_name')}) — {st.get('summary')}")

            explanation = (
                f"**Statutory Provision:** {text}\n\n"
                f"This provision sets out the statutory framework and obligations under Indian law."
            )
            if primary_stat.get("corresponding_provision"):
                explanation += f"\n\n*Historical Note: This provision corresponds to former {primary_stat.get('corresponding_provision')}.*"
            if nlp_res.get("answer"):
                explanation += f"\n\n**Additional Guidance:** {nlp_res.get('answer')}"

            # Tailored conditions and remedies based on intent
            if intent == "labour_employment_inquiry" or "salary" in lower_q or "wage" in lower_q:
                conditions = (
                    "Wages must be disbursed within 7 to 10 days after the wage period depending on enterprise size. "
                    "Deductions are strictly limited to statutory heads (PF, ESI, authorized recovery) and cannot exceed 50% of wages in total."
                )
                rights = (
                    "• Right to receive earned wages without unauthorized deductions or unreasonable delay.\n"
                    "• Right to claim delayed wages plus statutory compensation up to ten times the deduction before the Authority.\n"
                    "• Right to protection against wrongful termination for claiming statutory wages."
                )
                remedies = (
                    "• Issue a formal Legal Notice to the employer demanding disbursement of outstanding wages.\n"
                    "• File an application before the Authority appointed under Section 15 of the Payment of Wages Act, 1936.\n"
                    "• Lodge a grievance before the State Labour Commissioner or on the Ministry's SAMADHAN portal.\n"
                    "• File a claim in the Labour Court / Industrial Tribunal."
                )
                next_steps = (
                    "1. Collate employment contract, appointment letter, salary slips, attendance records, and bank statements.\n"
                    "2. Serve a written demand / formal legal notice to the employer giving 15 days to disburse dues.\n"
                    "3. If unpaid, file an application before the Authority under Section 15 Payment of Wages Act or contact Labour Commissioner."
                )

            elif intent == "bailable_offence_rights" or ("bail" in lower_q and "bailable" in lower_q):
                conditions = (
                    "In bailable offences, bail is an absolute statutory right. The accused cannot be detained if they "
                    "are prepared to furnish solvent bail bonds or surety as ordered by the police officer or court."
                )
                rights = (
                    "• Mandatory right to be informed that the offence is bailable (Section 47 BNSS).\n"
                    "• Absolute statutory right to be released on bail by the Police Station House Officer or Magistrate.\n"
                    "• Right to free legal aid through NALSA (helpline 15100) if indigent."
                )
                remedies = (
                    "• Submit bail application and surety bond directly before the Station House Officer (SHO) under Section 478 BNSS.\n"
                    "• Apply for bail before the jurisdictional Judicial Magistrate under Section 478 BNSS (formerly Section 436 CrPC).\n"
                    "• Approach Sessions Court or High Court if unreasonable or onerous bail conditions are imposed."
                )
                next_steps = (
                    "1. Verify whether the offence charged is classified as bailable in the First Schedule of BNSS.\n"
                    "2. Arrange local solvent sureties or personal bond required for release.\n"
                    "3. Present the bail bond to the investigating officer or Judicial Magistrate; contact NALSA at 15100 for free legal assistance."
                )

            elif intent == "consumer_grievance" or "consumer" in lower_q or "defect" in lower_q:
                conditions = (
                    "The complainant must qualify as a 'consumer' under Section 2(7) of the Consumer Protection Act, 2019 "
                    "(purchased goods or hired services for consideration, not for commercial resale) and establish defect or deficiency."
                )
                rights = (
                    "• Right to safety, information, choice, and seeking redressal against unfair trade practices.\n"
                    "• Right to claim full refund, replacement, damages, and litigation expenses.\n"
                    "• Right to file complaints electronically from any location via e-Daakhil."
                )
                remedies = (
                    "• Issue a formal written notice or email to the seller / manufacturer giving 15–30 days for resolution.\n"
                    "• Call the National Consumer Helpline at 1915 or lodge a grievance on consumerhelpline.gov.in.\n"
                    "• File an online consumer complaint via e-Daakhil (edaakhil.nic.in) before the District Consumer Commission."
                )
                next_steps = (
                    "1. Preserve tax invoice, payment receipts, warranty cards, and communication records.\n"
                    "2. Register a complaint with National Consumer Helpline (1915 or consumerhelpline.gov.in).\n"
                    "3. If unresolved, file an e-Daakhil complaint before the District Consumer Commission."
                )

            elif intent == "report_cybercrime" or "cyber" in lower_q or "otp" in lower_q:
                conditions = (
                    "Financial cyber fraud must be reported promptly within the 'golden hour' (first 2-3 hours) "
                    "to maximize the likelihood of inter-bank fund freezing."
                )
                rights = (
                    "• Right to immediate banking freeze assistance through National Cyber Crime Helpline (1930).\n"
                    "• Right to zero or limited liability for unauthorized banking transactions reported within 3 days as per RBI guidelines.\n"
                    "• Right to registration of FIR under IT Act and BNS."
                )
                remedies = (
                    "• Call 1930 immediately to alert Indian Cyber Crime Coordination Centre (I4C).\n"
                    "• Register an online complaint at cybercrime.gov.in.\n"
                    "• Lodge formal FIR at the local cyber crime police station."
                )
                next_steps = (
                    "1. Immediately call 1930 and inform your bank's fraud desk to block cards and freeze disputed accounts.\n"
                    "2. Preserve transaction IDs, SMS alerts, call logs, and fake website links.\n"
                    "3. File a formal cyber complaint on cybercrime.gov.in and obtain an acknowledgement number."
                )

            elif intent == "food_safety_inquiry" or "expired food" in lower_q or "adulterat" in lower_q:
                conditions = (
                    "Food business operators are strictly liable for selling unsafe, expired, or misbranded food. "
                    "Preservation of original packaging, batch number, bill, and food sample is essential for enforcement."
                )
                rights = (
                    "• Right to safe and hygienic food conforming to FSSAI quality standards.\n"
                    "• Right to claim compensation under Section 65 FSSA for injury or health hazards.\n"
                    "• Right to consumer redressal for unfair trade practices."
                )
                remedies = (
                    "• Lodge a complaint with the Designated Officer / Food Safety Officer under the FSSA.\n"
                    "• Submit a grievance on the FSSAI FoSCoS portal (foscos.fssai.gov.in).\n"
                    "• File a consumer complaint before the Consumer Commission for refund and compensation."
                )
                next_steps = (
                    "1. Retain purchase bill, packaging with expiry date/batch code, and photographs of the product.\n"
                    "2. Lodge a grievance on FSSAI FoSCoS portal and call National Consumer Helpline at 1915.\n"
                    "3. If health injury occurred, obtain medical certificates and seek compensation before Consumer Commission."
                )

            elif intent == "education_student_rights" or "mark sheet" in lower_q or "degree" in lower_q or "certificate" in lower_q:
                conditions = (
                    "Higher education institutions are legally prohibited by UGC notifications and contract law "
                    "from retaining original student certificates or degrees as security or for fee disputes."
                )
                rights = (
                    "• Right to unconditional custody of original academic certificates, marksheets, and degrees.\n"
                    "• Right to proportional fee refund upon timely cancellation of admission under UGC regulations.\n"
                    "• Right against harassment and withholding of educational credentials."
                )
                remedies = (
                    "• Submit written representation citing UGC Guidelines (F.No. 1-3/2007-CPP-II).\n"
                    "• Lodge a complaint on the UGC e-Samadhan portal (samadhan.ugc.ac.in).\n"
                    "• Approach the Consumer Commission or file a Writ Petition under Article 226 before the High Court."
                )
                next_steps = (
                    "1. Gather fee receipts, admission letters, written correspondence, and UGC notification copies.\n"
                    "2. Send a formal written representation and legal notice giving 7 days to release certificates.\n"
                    "3. If non-compliant, register a complaint on UGC e-Samadhan and approach the jurisdictional High Court."
                )

            elif intent == "traffic_licence_seizure" or "licence" in lower_q or "challan" in lower_q:
                conditions = (
                    "Police can only impound driving licences under specified statutory grounds (e.g. drunken driving, "
                    "jumping red light, overspeeding) and must provide an official temporary acknowledgement or receipt."
                )
                rights = (
                    "• Right to receive a valid statutory seizure receipt / challan (Section 206 MV Act).\n"
                    "• Right to fair adjudication before the Licensing Authority or Judicial Magistrate.\n"
                    "• Right to legal representation and appeal before the Motor Vehicles Appellate Tribunal."
                )
                remedies = (
                    "• Appear before the Virtual Court / Traffic Court to contest or compound the challan.\n"
                    "• Submit representation before the Regional Transport Office (RTO) / Licensing Authority.\n"
                    "• Appeal against suspension or revocation to the Appellate Tribunal or High Court."
                )
                next_steps = (
                    "1. Check the official Parivahan / e-Challan portal (echallan.parivahan.gov.in) using vehicle/challan number.\n"
                    "2. Verify statutory grounds and inspect the seizure receipt issued under Section 206 MV Act.\n"
                    "3. Appear before the Traffic Court / Licensing Authority or settle via Virtual Court."
                )

            elif any(w in lower_q for w in ["wife", "maintenance", "alimony", "spousal"]):
                direct_ans = (
                    "Yes, under Indian law, a working wife can legally claim maintenance from her husband if her own income "
                    "is insufficient to maintain the standard of living she enjoyed in the matrimonial home."
                )
                conditions = (
                    "Maintenance is not denied merely because the wife has an independent income or is capable of earning. "
                    "Under the landmark Supreme Court ruling in Rajnesh v. Neha (2020), the Family Court assesses the totality "
                    "of circumstances, including the husband's actual earning capacity, social status, necessary expenses, "
                    "and the net deficit between the wife's personal income and her reasonable living expenses."
                )
                rights = (
                    "• Right to claim interim maintenance and legal expenses during proceedings (Section 24 Hindu Marriage Act, 1955).\n"
                    "• Right to claim speedy monthly maintenance under Section 144 BNSS (former Section 125 CrPC).\n"
                    "• Right to seek residence rights and additional monetary relief under Sections 12 and 20 of PWDVA, 2005.\n"
                    "• Mandatory disclosure of assets and liabilities by both spouses via affidavits under Supreme Court directives."
                )
                remedies = (
                    "• File an application for interim maintenance under Section 24 HMA before the Family Court.\n"
                    "• File a petition for monthly maintenance before the Judicial Magistrate or Family Court under Section 144 BNSS.\n"
                    "• Seek monetary relief and residence orders under Section 12/20 of the Domestic Violence Act, 2005.\n"
                    "• Petition for permanent alimony and maintenance under Section 25 HMA upon passing of a matrimonial decree."
                )
                next_steps = (
                    "1. Collate income proofs: salary slips, Form 16, income tax returns (ITR), bank statements, and monthly expenditure records.\n"
                    "2. File a formal maintenance petition along with the mandatory Affidavit of Disclosure of Assets and Liabilities.\n"
                    "3. Approach the Family Court or contact the District Legal Services Authority (DLSA) / dial 15100 for free legal representation if eligible."
                )

            elif any(w in lower_q for w in ["landlord", "tenant", "tenancy", "eviction", "evict"]):
                is_tn = "tamil nadu" in lower_q or "chennai" in lower_q
                direct_ans = (
                    "Under Indian tenancy law, a landlord cannot unilaterally or forcibly evict a tenant without notice. "
                    + ("In Tamil Nadu, eviction is strictly governed by the Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017 (TNRRRLT Act). " if is_tn else "Eviction is strictly governed by State tenancy legislation. ")
                    + "A landlord must issue formal statutory notice and obtain an eviction decree from the Rent Court."
                )
                conditions = (
                    "Extra-judicial eviction, changing locks, throwing out tenant belongings, or disconnecting essential utilities "
                    "is illegal and penal. Eviction can only be sought on specified statutory grounds: (i) failure to pay agreed rent "
                    "after statutory notice; (ii) unauthorized subletting; (iii) misuse or substantial damage to property; "
                    "or (iv) bona fide requirement of the landlord for personal occupation or major repairs."
                )
                rights = (
                    "• Statutory right against arbitrary or forcible eviction without due process and a decree from the Rent Court.\n"
                    "• Absolute right to uninterrupted essential amenities (water, electricity, access) under Section 19 of the TN Tenancy Act / State Rent Control Act.\n"
                    "• Right to statutory notice period before any repossession proceedings can be initiated.\n"
                    "• Right to contest landlord claims before the specialized Rent Court."
                )
                remedies = (
                    "• File an urgent petition before the Rent Court / Rent Authority for an injunction against illegal eviction.\n"
                    "• Seek immediate mandatory interim restoration of disconnected water or electricity under Section 19(2) TN Tenancy Act.\n"
                    "• Lodge a police complaint or dial 112 if the landlord attempts physical intimidation, trespass, or criminal force.\n"
                    "• File a civil suit for permanent injunction under Section 38 of the Specific Relief Act, 1963."
                )
                next_steps = (
                    "1. Collate the written rental agreement, rent payment receipts, bank transfer records, and security deposit acknowledgement.\n"
                    "2. Preserve any written notices, WhatsApp messages, or emails sent by the landlord.\n"
                    "3. If utilities are cut off or eviction is threatened, immediately file an urgent application before the jurisdictional Rent Court or dial 112."
                )

            elif any(w in lower_q for w in ["arrest", "warrant", "can police arrest", "detention", "detained"]):
                direct_ans = (
                    "Under Indian law, police can arrest a person without a warrant only in cognizable offences, "
                    "strictly subject to statutory safeguards under Section 35 of the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) "
                    "and Article 22 of the Constitution of India. Arbitrary or mechanical arrest is illegal."
                )
                conditions = (
                    "For offences punishable with imprisonment for 7 years or less, arrest is NOT mandatory. The police officer "
                    "must first serve a Notice of Appearance under Section 35(3) BNSS (formerly Section 41A CrPC). Arrest can only be made "
                    "if the person fails to comply with the notice, or if the officer records specific written reasons that arrest is "
                    "necessary to prevent evidence tampering, witness intimidation, or further offences."
                )
                rights = (
                    "• Right to be informed immediately of the exact grounds of arrest and whether the offence is bailable (Article 22(1) Constitution & Sec 35 BNSS).\n"
                    "• Right to have an arrest memo prepared with exact time, location, and countersigned by at least one family member or respectable local witness.\n"
                    "• Right of the arrested person to have one friend, relative, or person of choice informed of the arrest and place of detention (Section 48 BNSS).\n"
                    "• Right to consult and be defended by a legal practitioner of choice during interrogation (Article 22(1) & Sec 48 BNSS).\n"
                    "• Female arrestees: search must be made by a female officer with strict decency (Sec 47 BNSS), and arrest before sunrise or after sunset requires prior Judicial Magistrate permission.\n"
                    "• Mandatory production before the nearest Judicial Magistrate within 24 hours of arrest (Article 22(2) & Sec 58 BNSS)."
                )
                remedies = (
                    "• Request immediate legal assistance by contacting an advocate or the National Legal Aid Helpline at 15100 (DLSA).\n"
                    "• Inform the Duty Magistrate of any procedural non-compliance or custodial mistreatment during the mandatory 24-hour production.\n"
                    "• File an application for bail under Section 478 BNSS (if bailable) or Section 480 BNSS (if non-bailable).\n"
                    "• Family can file a Habeas Corpus Writ Petition under Article 226 before the High Court if detention exceeds 24 hours without magistrate order.\n"
                    "• Lodge a complaint before the State Police Complaints Authority (SPCA) or National Human Rights Commission (NHRC) for custodial misconduct."
                )
                next_steps = (
                    "1. Request to see the officer's official identification tag and demand the written grounds of arrest and arrest memo.\n"
                    "2. Exercise your right to make a phone call to immediately inform a family member, friend, or advocate of your location.\n"
                    "3. Insist on undergoing a medical examination upon arrest and contact the District Legal Services Authority (DLSA) at 15100 for free legal counsel."
                )

            else:
                conditions = (
                    "Statutory procedures, evidentiary standards, and limitation periods prescribed under Indian law must be observed. "
                    "All legal claims require substantiation through verifiable documentation and adherence to jurisdictional rules."
                )
                rights = (
                    "• Right to fair procedure, natural justice, and access to competent legal institutions.\n"
                    "• Right to seek statutory remedies before competent administrative authorities and courts.\n"
                    "• Right to free legal aid under the Legal Services Authorities Act, 1987 (15100) for eligible persons."
                )
                remedies = (
                    "• Serve a formal Legal Notice demanding statutory compliance or dispute resolution.\n"
                    "• Approach the relevant regulatory commission, authority, or ombudsman.\n"
                    "• Institute proceedings in the competent civil court, tribunal, or magistrate court."
                )
                next_steps = (
                    "1. Collate all written agreements, receipts, emails, and official records.\n"
                    "2. Seek free legal guidance from the District Legal Services Authority (DLSA) or dial 15100.\n"
                    "3. Issue a formal legal notice or approach the competent statutory forum."
                )

        # =========================================================================
        # General / Ambiguous Inquiries Fallback
        # =========================================================================
        else:
            direct_ans = (
                "Under Indian law, rights, duties, and remedies depend upon specific statutory enactments of Parliament "
                "and State Legislatures. Please provide specific factual context (such as the nature of the dispute, parties, "
                "or location) for precise statutory provisions."
            )
            rel_law = [
                "• Constitution of India, 1950 — Fundamental Rights & Directive Principles [Current Law | Source: India Code]",
                "• Relevant Central and State Enactments published on official government digital repositories."
            ]
            explanation = (
                "The Indian legal framework distinguishes between civil disputes, criminal offences, regulatory compliances, "
                "and constitutional rights. Every claim requires establishing a recognized cause of action, territorial "
                "jurisdiction, and adherence to statutory limitation periods."
            )
            conditions = (
                "Legal proceedings must be initiated within the time limits prescribed by the Limitation Act, 1963, "
                "and must satisfy procedural requirements under the Code of Civil Procedure or Bharatiya Nagarik Suraksha Sanhita."
            )
            rights = (
                "• Right to due process of law, natural justice, and a fair hearing before any adverse action.\n"
                "• Right to free legal aid under Section 12 of the Legal Services Authorities Act, 1987 for eligible citizens.\n"
                "• Right to information under the RTI Act, 2005 for records held by public authorities."
            )
            remedies = (
                "• Issue a formal Legal Notice through an advocate.\n"
                "• Approach the competent regulatory authority, tribunal, or civil/criminal court.\n"
                "• Contact the District Legal Services Authority (DLSA) or dial 15100 for free legal assistance."
            )
            next_steps = (
                "1. Clarify the specific legal issue, parties involved, and transaction or dispute dates.\n"
                "2. Preserve all written communication, contracts, notices, and payment proofs.\n"
                "3. Contact the National Legal Aid Helpline at 15100 or consult an advocate in your jurisdiction."
            )

        # =========================================================================
        # Assemble 8 Standardized Markdown Sections
        # =========================================================================
        parts.append(f"### Direct Answer\n{direct_ans}\n")

        parts.append("### Relevant Law")
        for rl in rel_law:
            parts.append(rl)
        parts.append("")

        parts.append(f"### Explanation in Simple English\n{explanation}\n")

        parts.append(f"### Conditions and Exceptions\n{conditions}\n")

        parts.append(f"### Rights of the Person\n{rights}\n")

        parts.append(f"### Available Remedies\n{remedies}\n")

        parts.append(f"### Practical Next Steps\n{next_steps}\n")

        # Judicial Decisions Section
        parts.append("### Relevant Judicial Decisions")
        if judgments:
            for j in judgments[:2]:
                j_title = j.get("title", "Court Judgment")
                j_court = j.get("court", "Supreme Court of India")
                j_cit = str(j.get("citation", "")).strip()
                j_sum = str(j.get("summary", "")).strip()
                cit_text = f" — Citation: {j_cit}" if j_cit and j_cit.lower() not in ("none", "null") else ""
                sum_text = f". {j_sum}" if j_sum else ""
                parts.append(f"• **{j_title}** ({j_court}){cit_text}{sum_text}")
        else:
            parts.append("No verified judicial decisions were found for this query.")
        parts.append("")

        # Sources Section
        parts.append("### Sources")
        for s in sources:
            s_type = f" [{s.get('type')}]" if s.get("type") else ""
            parts.append(f"• {s.get('title')}{s_type}: {s.get('url')}")

        # Emergency & High-Risk Helplines
        if intent == "report_cybercrime" or "cyber" in lower_q:
            parts.append("\n**Emergency Helpline:** Dial **1930** (National Cyber Crime Helpline) or report online at [cybercrime.gov.in](https://cybercrime.gov.in/).")
        elif intent == "consumer_grievance" or "consumer" in lower_q:
            parts.append("\n**Consumer Grievance:** Dial **1915** (National Consumer Helpline) or visit [consumerhelpline.gov.in](https://consumerhelpline.gov.in/).")
        elif intent == "find_legal_aid":
            parts.append("\n**Free Legal Aid:** Call NALSA helpline **15100** or visit [nalsa.gov.in](https://nalsa.gov.in/).")
        elif intent == "women_protection":
            parts.append("\n**Women's Helplines:** Dial **1091** (Women in Distress), **181** (Domestic Abuse), or **112** (Pan-India Emergency).")
        elif intent == "child_protection_pocso":
            parts.append("\n**Child Protection:** Dial **1098** (Childline) or **112** (Pan-India Emergency).")
        elif intent == "senior_citizen_welfare":
            parts.append("\n**Senior Citizen Helpline:** Dial **14567** (Elderline) for welfare assistance.")
        elif intent == "education_student_rights" and "ragging" in lower_q:
            parts.append("\n**Anti-Ragging Helpline:** Call **1800-180-5522** or report online at [antiragging.in](https://www.antiragging.in/).")

        # Citizen Awareness Note & Disclaimer
        parts.append("\n*(Notice: Public legal awareness response synthesized from verified Indian statutory provisions and authoritative government records.)*")
        parts.append(f"\n*Note: {Config.LEGAL_DISCLAIMER}*")

        return {
            "success": False,
            "answer": "\n".join(parts),
            "sources": sources,
            "model": self.model_name,
            "fallback_used": True,
            "error": error_msg or "AI service unavailable; local verified fallback provided."
        }


# Global singleton service instance and convenience function
_GEMINI_SERVICE_INSTANCE: Optional[GeminiService] = None

def get_gemini_service() -> GeminiService:
    """Retrieve or initialize the global GeminiService singleton."""
    global _GEMINI_SERVICE_INSTANCE
    if _GEMINI_SERVICE_INSTANCE is None:
        _GEMINI_SERVICE_INSTANCE = GeminiService()
    return _GEMINI_SERVICE_INSTANCE

def generate_legal_answer(
    user_question: str,
    legal_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Convenience module function for generating grounded legal answers."""
    return get_gemini_service().generate_legal_answer(
        user_question=user_question,
        legal_context=legal_context,
        conversation_history=conversation_history
    )
