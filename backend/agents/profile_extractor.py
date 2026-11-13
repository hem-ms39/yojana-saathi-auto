from __future__ import annotations

import re

from backend.agents.prompts import PROFILE_EXTRACTION_SYSTEM
from backend.models.schemas import UserProfile
from backend.services.llm_service import LLMService


class ProfileExtractorAgent:
    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or LLMService()

    def run(self, user_message: str) -> UserProfile:
        llm_json = self.llm_service.generate_json(PROFILE_EXTRACTION_SYSTEM, user_message)
        fallback_profile = self._fallback_extract(user_message)
        if llm_json:
            llm_profile = UserProfile(**llm_json)
            merged = self._merge_profiles(llm_profile, fallback_profile, user_message)
            return self._normalize_profile(merged)
        return self._normalize_profile(fallback_profile)

    def _fallback_extract(self, text: str) -> UserProfile:
        normalized = self._normalize_digits(text)
        lowered = normalized.lower()
        age = self._extract_age(lowered)
        income = self._extract_income(lowered)
        state, district = self._extract_location(lowered)
        occupation = self._extract_occupation(lowered)
        gender = self._extract_gender(lowered)
        business_intent = "business" if self._has_any(lowered, ["business", "startup", "loan", "व्यवसाय", "उद्यम", "दुकान"]) else None

        return UserProfile(
            age=age,
            gender=gender,
            state=state,
            district=district,
            income_annual=income,
            occupation=occupation,
            business_intent=business_intent,
            has_bank_account=True if self._has_any(lowered, ["bank", "बैंक"]) else None,
            existing_business=True if self._has_any(lowered, ["existing business", "already running", "पहले से व्यवसाय"]) else None,
        )

    @staticmethod
    def _merge_profiles(primary: UserProfile, fallback: UserProfile, source_text: str) -> UserProfile:
        merged = {}
        lowered = source_text.lower()
        boolean_fields = {"existing_business", "has_bank_account", "disabilities", "minority"}
        for field_name in primary.model_fields.keys():
            primary_value = getattr(primary, field_name)
            fallback_value = getattr(fallback, field_name)
            if field_name in boolean_fields:
                merged[field_name] = ProfileExtractorAgent._resolve_boolean_field(
                    field_name=field_name,
                    llm_value=primary_value,
                    fallback_value=fallback_value,
                    source_text=lowered,
                )
            else:
                merged[field_name] = primary_value if primary_value is not None else fallback_value
        return UserProfile(**merged)

    @staticmethod
    def _resolve_boolean_field(
        field_name: str,
        llm_value: bool | None,
        fallback_value: bool | None,
        source_text: str,
    ) -> bool | None:
        # Deterministic extractor has explicit keyword evidence; trust it first.
        if fallback_value is not None:
            return fallback_value
        if llm_value is None:
            return None
        # Prevent over-confident LLM defaults ("false") when text has no evidence.
        if ProfileExtractorAgent._has_boolean_evidence(field_name, source_text):
            return llm_value
        return None

    @staticmethod
    def _has_boolean_evidence(field_name: str, source_text: str) -> bool:
        evidence_terms: dict[str, list[str]] = {
            "existing_business": ["existing business", "already running", "पहले से व्यवसाय", "पहले से बिजनेस"],
            "has_bank_account": ["bank account", "बैंक खाता", "bank"],
            "disabilities": ["disability", "disabled", "विकलांग", "दिव्यांग"],
            "minority": ["minority", "अल्पसंख्यक"],
        }
        return any(term in source_text for term in evidence_terms.get(field_name, []))

    @staticmethod
    def _has_any(text: str, terms: list[str]) -> bool:
        return any(term in text for term in terms)

    @staticmethod
    def _normalize_digits(text: str) -> str:
        devanagari_digits = str.maketrans("०१२३४५६७८९", "0123456789")
        return text.translate(devanagari_digits)

    @staticmethod
    def _normalize_profile(profile: UserProfile) -> UserProfile:
        state_aliases = {
            # Hindi state names
            "कर्नाटक": "Karnataka",
            "महाराष्ट्र": "Maharashtra",
            "उत्तर प्रदेश": "Uttar Pradesh",
            "उ.प्र.": "Uttar Pradesh",
            "तमिलनाडु": "Tamil Nadu",
            "दिल्ली": "Delhi",
            "बिहार": "Bihar",
            "राजस्थान": "Rajasthan",
            "मध्य प्रदेश": "Madhya Pradesh",
            "म.प्र.": "Madhya Pradesh",
            "गुजरात": "Gujarat",
            "पश्चिम बंगाल": "West Bengal",
            "आंध्र प्रदेश": "Andhra Pradesh",
            "तेलंगाना": "Telangana",
            "केरल": "Kerala",
            "ओडिशा": "Odisha",
            "उड़ीसा": "Odisha",
            "असम": "Assam",
            "पंजाब": "Punjab",
            "हरियाणा": "Haryana",
            "झारखंड": "Jharkhand",
            "उत्तराखंड": "Uttarakhand",
            "छत्तीसगढ़": "Chhattisgarh",
            "हिमाचल प्रदेश": "Himachal Pradesh",
            "जम्मू और कश्मीर": "Jammu and Kashmir",
            "गोवा": "Goa",
            "मणिपुर": "Manipur",
            "मेघालय": "Meghalaya",
            "त्रिपुरा": "Tripura",
            "मिज़ोरम": "Mizoram",
            "नागालैंड": "Nagaland",
            "सिक्किम": "Sikkim",
            "अरुणाचल प्रदेश": "Arunachal Pradesh",
        }
        district_aliases = {
            "bangalore": "Bengaluru",
            "bengaluru": "Bengaluru",
            "बैंगलोर": "Bengaluru",
            "बेंगलुरु": "Bengaluru",
            "mysore": "Mysuru",
            "mysuru": "Mysuru",
            "मैसूर": "Mysuru",
            "पटना": "Patna",
            "जयपुर": "Jaipur",
            "लखनऊ": "Lucknow",
            "भोपाल": "Bhopal",
            "इंदौर": "Indore",
            "अहमदाबाद": "Ahmedabad",
            "सूरत": "Surat",
            "कोलकाता": "Kolkata",
            "हैदराबाद": "Hyderabad",
            "चेन्नई": "Chennai",
            "पुणे": "Pune",
            "मुंबई": "Mumbai",
            "दिल्ली": "New Delhi",
            "गुरुग्राम": "Gurugram",
            "नोएडा": "Noida",
            "वाराणसी": "Varanasi",
            "कानपुर": "Kanpur",
            "नागपुर": "Nagpur",
            "भुवनेश्वर": "Bhubaneswar",
            "रांची": "Ranchi",
            "देहरादून": "Dehradun",
            "रायपुर": "Raipur",
            "शिमला": "Shimla",
            "चंडीगढ़": "Chandigarh",
            "गुवाहाटी": "Guwahati",
        }
        occupation_aliases = {
            # Hindi
            "किसान": "farmer",
            "खेतिहर": "farmer",
            "छात्र": "student",
            "विद्यार्थी": "student",
            "दर्जी": "tailor",
            "उद्यमी": "entrepreneur",
            "दुकानदार": "shop owner",
            "व्यवसायी": "business owner",
            "बेरोजगार": "unemployed",
            "नौकरीपेशा": "salaried",
            "सरकारी कर्मचारी": "government employee",
            "मजदूर": "laborer",
            "श्रमिक": "laborer",
            "कारीगर": "artisan",
            "बुनकर": "weaver",
            # English
            "student": "student",
            "Student": "student",
            "scholar": "student",
            "tailor": "tailor",
            "entrepreneur": "entrepreneur",
            "shop owner": "shop owner",
            "farmer": "farmer",
            "vendor": "vendor",
            "laborer": "laborer",
            "artisan": "artisan",
            "unemployed": "unemployed",
            "salaried": "salaried",
        }
        gender_aliases = {
            "female": "female",
            "woman": "female",
            "women": "female",
            "girl": "female",
            "महिला": "female",
            "औरत": "female",
            "लड़की": "female",
            "स्त्री": "female",
            "male": "male",
            "man": "male",
            "पुरुष": "male",
            "लड़का": "male",
            "आदमी": "male",
        }

        state = profile.state
        if state:
            state = state_aliases.get(state.strip(), state.strip().title())

        district = profile.district
        if district:
            district_key = district.strip().lower()
            district = district_aliases.get(district_key, district.strip().title())

        occupation = profile.occupation
        if occupation:
            occupation = occupation_aliases.get(occupation.strip(), occupation_aliases.get(occupation.strip().lower(), occupation.strip().lower()))

        gender = profile.gender
        if gender:
            gender = gender_aliases.get(gender.strip(), gender_aliases.get(gender.strip().lower(), gender.strip().lower()))

        business_intent = profile.business_intent
        if business_intent:
            normalized_intent = business_intent.strip().lower()
            if normalized_intent in {"business", "tailoring", "tailoring unit"}:
                business_intent = "business"

        return UserProfile(
            age=profile.age,
            gender=gender,
            state=state,
            district=district,
            income_annual=profile.income_annual,
            caste_category=profile.caste_category,
            occupation=occupation,
            education=profile.education,
            business_intent=business_intent,
            existing_business=profile.existing_business,
            has_bank_account=profile.has_bank_account,
            disabilities=profile.disabilities,
            minority=profile.minority,
        )

    def _extract_age(self, text: str) -> int | None:
        age_patterns = [
            r"(\d{1,2})\s*(?:year|yr)s?\s*old",
            r"age\s*(?:is|:)?\s*(\d{1,2})",
            r"(\d{1,2})\s*(?:साल|वर्ष)\s*(?:का|की|की हूँ|का हूँ|का हूं|की हूं)?",
        ]
        for pattern in age_patterns:
            match = re.search(pattern, text)
            if match:
                age = int(match.group(1))
                if 15 <= age <= 100:
                    return age
        return None

    def _extract_income(self, text: str) -> int | None:
        income_patterns = [
            r"(?:income|salary|earn(?:ing)?|annual)\D*(\d{4,9})",
            r"(?:आय|सालाना आय|कमाई)\D*(\d{4,9})",
            r"(\d+(?:\.\d+)?)\s*(lakh|lac|लाख)",
            r"(\d+(?:\.\d+)?)\s*(crore|करोड़)",
        ]
        for pattern in income_patterns:
            match = re.search(pattern, text)
            if not match:
                continue
            value = float(match.group(1))
            unit = match.group(2) if len(match.groups()) > 1 else None
            if unit:
                unit = unit.lower()
                if unit in {"lakh", "lac", "लाख"}:
                    return int(value * 100000)
                if unit in {"crore", "करोड़"}:
                    return int(value * 10000000)
            return int(value)
        return None

    def _extract_location(self, text: str) -> tuple[str | None, str | None]:
        state_map = {
            "karnataka": "Karnataka",
            "कर्नाटक": "Karnataka",
            "maharashtra": "Maharashtra",
            "महाराष्ट्र": "Maharashtra",
            "uttar pradesh": "Uttar Pradesh",
            "उत्तर प्रदेश": "Uttar Pradesh",
            "tamil nadu": "Tamil Nadu",
            "तमिलनाडु": "Tamil Nadu",
            "delhi": "Delhi",
            "दिल्ली": "Delhi",
            "bihar": "Bihar",
            "बिहार": "Bihar",
            "rajasthan": "Rajasthan",
            "राजस्थान": "Rajasthan",
            "madhya pradesh": "Madhya Pradesh",
            "मध्य प्रदेश": "Madhya Pradesh",
            "gujarat": "Gujarat",
            "गुजरात": "Gujarat",
            "west bengal": "West Bengal",
            "पश्चिम बंगाल": "West Bengal",
            "andhra pradesh": "Andhra Pradesh",
            "आंध्र प्रदेश": "Andhra Pradesh",
            "telangana": "Telangana",
            "तेलंगाना": "Telangana",
            "kerala": "Kerala",
            "केरल": "Kerala",
            "odisha": "Odisha",
            "orissa": "Odisha",
            "ओडिशा": "Odisha",
            "assam": "Assam",
            "असम": "Assam",
            "punjab": "Punjab",
            "पंजाब": "Punjab",
            "haryana": "Haryana",
            "हरियाणा": "Haryana",
            "jharkhand": "Jharkhand",
            "झारखंड": "Jharkhand",
            "uttarakhand": "Uttarakhand",
            "उत्तराखंड": "Uttarakhand",
            "chhattisgarh": "Chhattisgarh",
            "छत्तीसगढ़": "Chhattisgarh",
            "himachal pradesh": "Himachal Pradesh",
            "हिमाचल प्रदेश": "Himachal Pradesh",
            "goa": "Goa",
            "गोवा": "Goa",
        }
        district_map = {
            "bangalore": "Bengaluru",
            "bengaluru": "Bengaluru",
            "बैंगलोर": "Bengaluru",
            "बेंगलुरु": "Bengaluru",
            "mysuru": "Mysuru",
            "mysore": "Mysuru",
            "मैसूर": "Mysuru",
            "patna": "Patna",
            "पटना": "Patna",
            "jaipur": "Jaipur",
            "जयपुर": "Jaipur",
            "lucknow": "Lucknow",
            "लखनऊ": "Lucknow",
            "bhopal": "Bhopal",
            "भोपाल": "Bhopal",
            "indore": "Indore",
            "इंदौर": "Indore",
            "ahmedabad": "Ahmedabad",
            "अहमदाबाद": "Ahmedabad",
            "kolkata": "Kolkata",
            "कोलकाता": "Kolkata",
            "hyderabad": "Hyderabad",
            "हैदराबाद": "Hyderabad",
            "chennai": "Chennai",
            "चेन्नई": "Chennai",
            "pune": "Pune",
            "पुणे": "Pune",
            "mumbai": "Mumbai",
            "मुंबई": "Mumbai",
            "varanasi": "Varanasi",
            "वाराणसी": "Varanasi",
            "kanpur": "Kanpur",
            "कानपुर": "Kanpur",
            "nagpur": "Nagpur",
            "नागपुर": "Nagpur",
            "ranchi": "Ranchi",
            "रांची": "Ranchi",
            "dehradun": "Dehradun",
            "देहरादून": "Dehradun",
            "raipur": "Raipur",
            "रायपुर": "Raipur",
            "chandigarh": "Chandigarh",
            "चंडीगढ़": "Chandigarh",
            "guwahati": "Guwahati",
            "गुवाहाटी": "Guwahati",
        }

        state = next((v for k, v in state_map.items() if k in text), None)
        district = next((v for k, v in district_map.items() if k in text), None)
        if not state and district in {"Bengaluru", "Mysuru"}:
            state = "Karnataka"
        if not state and district in {"Patna"}:
            state = "Bihar"
        if not state and district in {"Jaipur"}:
            state = "Rajasthan"
        if not state and district in {"Lucknow", "Kanpur", "Varanasi"}:
            state = "Uttar Pradesh"
        if not state and district in {"Bhopal", "Indore"}:
            state = "Madhya Pradesh"
        if not state and district in {"Ahmedabad", "Surat"}:
            state = "Gujarat"
        return state, district

    def _extract_occupation(self, text: str) -> str | None:
        occupation_map = {
            "farmer": "farmer",
            "किसान": "farmer",
            "खेतिहर": "farmer",
            "student": "student",
            "छात्र": "student",
            "विद्यार्थी": "student",
            "दर्जी": "tailor",
            "tailor": "tailor",
            "vendor": "vendor",
            "दुकानदार": "shop owner",
            "shop owner": "shop owner",
            "entrepreneur": "entrepreneur",
            "उद्यमी": "entrepreneur",
            "बेरोजगार": "unemployed",
            "unemployed": "unemployed",
            "मजदूर": "laborer",
            "श्रमिक": "laborer",
            "कारीगर": "artisan",
            "बुनकर": "weaver",
            "नौकरीपेशा": "salaried",
            "salaried": "salaried",
        }
        return next((v for k, v in occupation_map.items() if k in text), None)

    def _extract_gender(self, text: str) -> str | None:
        if self._has_any(text, ["female", "woman", "women", "girl", "महिला", "औरत", "लड़की", "स्त्री"]):
            return "female"
        if self._has_any(text, ["male", "man", "पुरुष", "लड़का", "आदमी"]):
            return "male"
        return None

