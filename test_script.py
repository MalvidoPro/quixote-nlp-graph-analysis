import spacy

# Load the small English model
try:
    nlp = spacy.load("en_core_web_trf")
    print("✅ Model loaded successfully!")
except OSError:
    print("❌ Model not found. Run: python -m spacy download en_core_web_sm")

# Test it on a simple sentence
text = "Gandalf and Frodo Baggins are traveling to Mordor."
doc = nlp(text)

# Print what it found
print("\nEntities found:")
for ent in doc.ents:
    print(f"{ent.text} ({ent.label_})")

# Expected Output:
# Gandalf (PERSON)
# Frodo Baggins (PERSON)
# Mordor (GPE) or (LOC)