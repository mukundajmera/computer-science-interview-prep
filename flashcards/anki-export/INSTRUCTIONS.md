# 📱 Anki Export & Import Guide

> **Instructions for exporting flashcards from this repository and importing them into Anki for spaced repetition study**

---

## 🚀 Generating Anki Export Files

Before importing, you can automatically generate ready-to-import TSV files from the markdown flashcard decks using the provided Python script.

1. **Open your terminal** at the root of this repository.
2. **Run the export script**:
   ```bash
   python3 scripts/export_anki_decks.py
   ```
   This will read all `.md` files in the `flashcards/` directory and generate a corresponding `.tsv` (Tab-Separated Values) file in the `flashcards/anki-export/decks/` directory.

   *Optional flags:*
   - `--dry-run`: View what would be generated without writing any files.
   - `--deck <name>`: Generate export for a specific deck (e.g., `--deck hld-concepts`).

---

## 📥 How to Import to Anki

### Bulk Import (Recommended)

After generating the `.tsv` files with the script, you can easily import them into Anki.

1. **Open Anki** on your computer.
2. **Create a new deck** or select an existing one (e.g., `File > Create Deck > "System Design"`).
3. **Import to Anki**:
   - `File > Import`
   - Select the `.tsv` file generated in `flashcards/anki-export/decks/`
   - Set "Fields separated by: Tab"
   - Set "Import as: Basic" (or any note type with at least Front and Back fields)
   - Ensure the fields are mapped correctly:
     - **Field 1** mapped to **Front**
     - **Field 2** mapped to **Back**
     - **Field 3** mapped to **Tags**
   - Check the option "Allow HTML in fields" (this is important because the export script converts formatting to HTML).
   - Click `Import`.

### Manual Import

1. **Open Anki** on your computer
2. **Create a new deck**: `File > Create Deck > "Design Patterns & LLD"`
3. **Add cards manually**:
   - Click `Add` button
   - Copy question to `Front` field
   - Copy the provided answer or notes to the `Back` field
   - Click `Add` to save

### Using Markdown Import Plugin

1. **Install plugin**: `Tools > Add-ons > Get Add-ons`
2. **Enter code**: `1788670778` (Markdown Import)
3. **Restart Anki**
4. **Import**: `File > Import > Select .md file`

---

## ⚙️ Recommended Settings

### New Cards Per Day
```
Beginner:     10-15 cards/day
Intermediate: 20-25 cards/day
Advanced:     30-40 cards/day
```

### Interval Settings (Options > New Cards)
```
Learning steps:     1m 10m 1d   (1 minute, 10 minutes, 1 day)
Graduating interval: 3 days
Easy interval:      7 days
```

### Review Settings (Options > Reviews)
```
Maximum reviews/day: 100-200
Easy bonus:         150%
Interval modifier:  100%
```

---

## 📖 Study Tips for Anki

### Daily Workflow
1. **Morning session** (15-20 min): New cards + due reviews
2. **Evening session** (10 min): Quick review of "Again" cards

### Effective Review Habits
- ✅ **Be honest** with ratings - don't mark "Easy" if you hesitated
- ✅ **Review daily** - even 5 minutes maintains momentum
- ✅ **Use tags** - organize cards by topic for focused study
- ✅ **Add context** - include examples in your answers

### What to Avoid
- ❌ Skipping days (breaks the algorithm)
- ❌ Reviewing when exhausted (poor retention)
- ❌ Over-customizing intervals (trust the algorithm)

---

## 📲 Mobile Sync Guide

### iOS (AnkiMobile)
1. Create **AnkiWeb account** at [ankiweb.net](https://ankiweb.net)
2. **Desktop**: `Tools > Preferences > Network > Sync on startup`
3. Click `Sync` button (circular arrows)
4. **iOS**: Open AnkiMobile > Tap `Sync`
5. Login with AnkiWeb credentials

### Android (AnkiDroid)
1. Create **AnkiWeb account** at [ankiweb.net](https://ankiweb.net)
2. **Desktop**: Click `Sync` button
3. **Android**: Open AnkiDroid > Menu > `Sync`
4. Login with AnkiWeb credentials

### Sync Best Practices
- Always sync **before** and **after** studying
- Sync on Wi-Fi to avoid data charges
- Resolve conflicts by choosing "Upload to AnkiWeb" if desktop is primary

---

## 🏷️ Suggested Tags

Organize your cards with these tags:

```
#design-patterns
  #creational
  #structural
  #behavioral
  
#lld-concepts
  #oop
  #solid
  #composition
  #design-principles
  #uml
  #code-smells
  
#difficulty
  #easy
  #medium
  #hard
  
#status
  #mastered
  #review-needed
  #struggling
```

---

## 🔧 Troubleshooting

### Cards Not Syncing
1. Check internet connection
2. Verify AnkiWeb login credentials
3. Force full sync: `Tools > Preferences > Network > Full sync on next sync`

### Import Errors
1. Check file encoding (UTF-8 recommended)
2. Remove special characters from questions
3. Ensure consistent formatting

### Scheduling Issues
1. Reset card: `Browse > Select card > Cards > Reschedule`
2. Check deck options for correct intervals

---

## 📚 Additional Resources

- [Anki Manual](https://docs.ankiweb.net/)
- [Anki Shared Decks](https://ankiweb.net/shared/decks/)
- [Spaced Repetition Guide](https://ncase.me/remember/)

---

<p align="center">
  <b>Happy Studying! 🎓</b><br>
  <i>Spaced repetition is proven to be the most effective learning technique.</i>
</p>
