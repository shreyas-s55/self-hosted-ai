"""OpenAI Chat Completion request transformer."""

from __future__ import annotations

from lib.gateway.deployment import GatewayDeployment
from lib.openai.chat.models import ChatCompletionRequest


class ChatRequestTransformer:
    """Transforms OpenAI chat requests for the selected deployment."""

    def transform(
        self,
        request: ChatCompletionRequest,
        deployment: GatewayDeployment,
    ) -> ChatCompletionRequest:
        """Transform a request for the selected deployment."""

        return request.with_model(deployment.repository)