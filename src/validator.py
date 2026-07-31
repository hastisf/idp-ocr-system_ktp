import re


def validate_nik(nik: str, gender: str) -> str:
  """Validates Indonesian NIK format and checks consistency with gender.

  Returns a clear validation status string.
  """
  if not nik:
    return "Invalid: Missing NIK"

  # Clean non-digit characters
  nik_clean = re.sub(r"\D", "", str(nik))

  # Check basic NIK length
  if len(nik_clean) != 16:
    return f"Invalid: Length is {len(nik_clean)} digits (Expected 16)"

  # Extract date digit from NIK (digits 7-8)
  try:
    day_digit = int(nik_clean[6:8])
  except ValueError:
    return "Invalid: NIK Date Format"

  # Determine gender derived from NIK
  # Female NIK days are offset by +40 (41 to 71)
  nik_gender = "Female" if day_digit > 40 else "Male"

  # Compare with extracted document gender if provided
  if gender and str(gender).strip().title() in ["Male", "Female"]:
    doc_gender = str(gender).strip().title()
    if nik_gender != doc_gender:
      return f"Mismatch: NIK indicates {nik_gender}, document states {doc_gender}"

  return "Valid NIK Structure"