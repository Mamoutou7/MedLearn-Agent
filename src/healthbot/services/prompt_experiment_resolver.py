from __future__ import annotations

import hashlib
from dataclasses import dataclass

from healthbot.core.settings import settings


@dataclass(slots=True)
class PromptExperimentAssignment:
    prompt_name: str
    version: str
    experiment_enabled: bool
    bucket: int


class PromptExperimentResolver:
    """Deterministically assigns sessions/users to prompt versions."""

    def resolve(
        self,
        *,
        prompt_name: str,
        session_id: str,
        default_version: str,
        weights_raw: str,
    ) -> PromptExperimentAssignment:
        if not settings.prompt_ab_testing_enabled:
            return PromptExperimentAssignment(
                prompt_name=prompt_name,
                version=default_version,
                experiment_enabled=False,
                bucket=-1,
            )

        weights = self._parse_weights(weights_raw)
        bucket = self._stable_bucket(session_id, prompt_name)

        cumulative = 0
        for version, weight in weights:
            cumulative += weight
            if bucket < cumulative:
                return PromptExperimentAssignment(
                    prompt_name=prompt_name,
                    version=version,
                    experiment_enabled=True,
                    bucket=bucket,
                )

        return PromptExperimentAssignment(
            prompt_name=prompt_name,
            version=default_version,
            experiment_enabled=True,
            bucket=bucket,
        )

    def _stable_bucket(self, session_id: str, prompt_name: str) -> int:
        value = f"{session_id}:{prompt_name}".encode()
        digest = hashlib.sha256(value).hexdigest()
        return int(digest[:8], 16) % 100

    def _parse_weights(self, raw: str) -> list[tuple[str, int]]:
        result: list[tuple[str, int]] = []

        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue

            version, weight = item.split(":", 1)
            result.append((version.strip(), int(weight.strip())))

        total = sum(weight for _, weight in result)
        if total != 100:
            raise ValueError(f"Prompt A/B weights must sum to 100, got {total}")

        return result
