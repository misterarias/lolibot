def escapeMarkdownCharacters(response: str) -> str:
    # Escapes Telegram MarkdownV2 special characters
    # See: https://core.telegram.org/bots/api#markdownv2-style
    for c in set(["_", "*", "[", "]", "(", ")", "~", "`", "#", "+", "-", "=", "|", "{", "}", ".", "!", "<", ">"]):
        response = response.replace(c, f"\\{c}")
    return response
