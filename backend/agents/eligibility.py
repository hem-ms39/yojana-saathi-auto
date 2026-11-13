from __future__ import annotations

from backend.models.schemas import Scheme, SchemeResult, UserProfile


class EligibilityAgent:
    def run(self, profile: UserProfile, schemes: list[Scheme]) -> list[SchemeResult]:
        results: list[SchemeResult] = []
        for scheme in schemes:
            score, reason = self._score_scheme(profile, scheme)
            if score >= 70:
                eligibility = "yes"
            elif score >= 50:
                eligibility = "likely"
            else:
                eligibility = "no"

            results.append(
                SchemeResult(
                    scheme_id=scheme.scheme_id,
                    title=scheme.title,
                    funding_amount=scheme.funding_amount,
                    eligibility=eligibility,
                    confidence=score,
                    reasoning=reason,
                    category=scheme.category,
                    deadline=scheme.deadline,
                )
            )

        results.sort(key=lambda x: (x.confidence, x.funding_amount), reverse=True)
        return results

    def _score_scheme(self, profile: UserProfile, scheme: Scheme) -> tuple[int, str]:
        score = 30  # base score — scheme was already discovered via semantic search
        reasons: list[str] = []
        rules = scheme.eligibility_rules

        # ── Target group matching (high impact) ─────────────────────
        target_groups = [t.lower() for t in scheme.target_group]
        if target_groups:
            tg_matches = self._match_target_groups(profile, target_groups)
            if tg_matches:
                score += 5 * len(tg_matches)  # up to +25 for 5 matches
                reasons.extend(tg_matches)
            elif "all" not in target_groups:
                score -= 10
                reasons.append("target group mismatch")

        # ── Category matching ────────────────────────────────────────
        categories = [c.lower() for c in scheme.category]
        cat_matches = self._match_categories(profile, categories)
        if cat_matches:
            score += 5 * len(cat_matches)  # up to +15
            reasons.extend(cat_matches)

        # ── Age matching ─────────────────────────────────────────────
        min_age = rules.get("min_age") or scheme.min_age
        max_age = rules.get("max_age") or scheme.max_age
        if profile.age is not None:
            age_ok = True
            if min_age is not None and profile.age < min_age:
                age_ok = False
                score -= 15
                reasons.append(f"below min age ({min_age})")
            if max_age is not None and profile.age > max_age:
                age_ok = False
                score -= 15
                reasons.append(f"above max age ({max_age})")
            if age_ok:
                score += 10
                reasons.append("age eligible")
        else:
            # Don't penalize — user just didn't provide age
            score += 3

        # ── Income matching ──────────────────────────────────────────
        max_income = rules.get("max_income") or scheme.max_income
        if max_income and profile.income_annual is not None:
            if profile.income_annual <= max_income:
                score += 10
                reasons.append("income within limit")
            else:
                score -= 10
                reasons.append("income exceeds limit")
        elif max_income is None:
            # No income restriction — slight positive
            score += 3

        # ── Occupation matching ──────────────────────────────────────
        occupation = (profile.occupation or "").lower()
        occupations = [o.lower() for o in rules.get("occupations", [])]
        if occupations and occupation and occupation in occupations:
            score += 10
            reasons.append("occupation matches")

        # ── Business intent ──────────────────────────────────────────
        if profile.business_intent:
            biz_categories = {"entrepreneurship", "business_loan", "msme", "startup"}
            if biz_categories & set(categories):
                score += 12
                reasons.append("business intent matches scheme")
            if rules.get("requires_business_intent"):
                score += 8
                reasons.append("business intent required and present")

        # ── Gender matching ──────────────────────────────────────────
        gender = (profile.gender or "").lower()
        if gender:
            gender_targets = {"women", "female", "girl"}
            if gender in {"female", "woman"}:
                if gender_targets & set(target_groups):
                    score += 10
                    reasons.append("women-focused scheme")
            elif gender in {"male", "man"}:
                # Don't penalize, but no bonus for women-only schemes
                if gender_targets & set(target_groups) and "all" not in target_groups:
                    has_other_groups = set(target_groups) - gender_targets - {"all"}
                    if not has_other_groups:
                        score -= 5
                        reasons.append("scheme targets women only")

        # ── State matching ───────────────────────────────────────────
        scheme_state = (scheme.state or "all").lower()
        user_state = (profile.state or "").lower()
        if scheme_state != "all" and user_state:
            if user_state == scheme_state:
                score += 8
                reasons.append("state matches")
            else:
                score -= 5
                reasons.append("different state")

        # ── Clamp and return ─────────────────────────────────────────
        score = max(0, min(100, score))
        reason = ", ".join(reasons) if reasons else "general scheme match"
        return score, reason

    @staticmethod
    def _match_target_groups(profile: UserProfile, targets: list[str]) -> list[str]:
        """Match profile attributes against scheme's target_group list."""
        matches: list[str] = []
        gender = (profile.gender or "").lower()
        occupation = (profile.occupation or "").lower()

        if "all" in targets:
            matches.append("open to all")

        if gender in {"female", "woman"} and any(t in targets for t in ["women", "female", "girl"]):
            matches.append("targets women")
        # Student detection — occupation contains 'student', or education is set
        is_student = (
            "student" in occupation
            or "scholar" in occupation
            or profile.education is not None
        )
        if is_student and "student" in targets:
            matches.append("targets students")
        if is_student and profile.age is not None and profile.age <= 35 and "youth" in targets:
            matches.append("targets youth")
        if any(t in targets for t in ["sc", "st", "sc_st"]):
            caste = (profile.caste_category or "").lower()
            if caste and any(t in caste for t in ["sc", "st"]):
                matches.append(f"targets {caste.upper()} category")
        if "obc" in targets:
            caste = (profile.caste_category or "").lower()
            if "obc" in caste:
                matches.append("targets OBC category")
        if "minority" in targets:
            if profile.minority:
                matches.append("targets minority communities")
        if "bpl" in targets:
            if profile.income_annual is not None and profile.income_annual < 150000:
                matches.append("targets below poverty line")

        return matches

    @staticmethod
    def _match_categories(profile: UserProfile, categories: list[str]) -> list[str]:
        """Match profile intent against scheme categories."""
        matches: list[str] = []

        if profile.business_intent:
            biz_cats = {"entrepreneurship", "business_loan", "msme", "startup", "self_employment"}
            if biz_cats & set(categories):
                matches.append("business category match")

        occupation = (profile.occupation or "").lower()
        if occupation == "farmer" and any(c in categories for c in ["agriculture", "farming", "crop_insurance"]):
            matches.append("agriculture category match")

        # Student / scholarship detection — occupation OR education field
        is_student = (
            "student" in occupation
            or "scholar" in occupation
            or profile.education is not None
        )
        if is_student and any(c in categories for c in ["scholarship", "education"]):
            matches.append("education category match")

        return matches
