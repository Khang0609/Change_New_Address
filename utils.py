import unicodedata

def convert_to_filename(text: str) -> str:
    """Convert province/city name to ASCII filename (lowercase, underscores)."""
    nfkd_form = unicodedata.normalize('NFKD', text)
    only_ascii = nfkd_form.replace('đ', 'd').replace('Đ', 'D').encode('ASCII', 'ignore').decode('ASCII')
    return only_ascii.lower().replace(" ", "_")