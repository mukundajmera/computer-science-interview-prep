# 📝 Templates

Blank templates for practice. Use these to structure your interview answers.

---

## 📚 Available Templates

| Template | Purpose | Link |
|----------|---------|------|
| 📋 **LLD Template** | Low-Level Design practice | [lld-template.md](lld-template.md) |
| 🏗️ **HLD Template** | High-Level Design practice | [hld-template.md](hld-template.md) |
| 🧠 **Behavioral Story Template** | Structured worksheet for Decode→Select→CARL story prep | [behavioral-story-template.md](behavioral-story-template.md) |
| ✅ **Topic Review Rubric** | Five-read-check review scorecard for any learner-facing topic | [topic-review-rubric.md](topic-review-rubric.md) |

### 🎯 Interview Practice Templates (with Rubrics)

| Template | Purpose | Link |
|----------|---------|------|
| 🏗️ **LLD Practice** | Time-boxed rubric, scoring, and checklist for LLD interviews | [practice-lld.md](practice-lld.md) |
| 🌐 **HLD Practice** | Time-boxed rubric, scoring, and checklist for HLD interviews | [practice-hld.md](practice-hld.md) |
| 🧱 **HLD Concept Pack** | Canonical structure for distributed-systems concept pages | [hld-concept-template.md](hld-concept-template.md) |
| 🌐 **HLD Project Pack** | Required files and sections for full HLD case studies | [hld-project-pack-template.md](hld-project-pack-template.md) |
| 🏗️ **LLD Project Pack** | Required files and sections for LLD project packs | [lld-project-pack-template.md](lld-project-pack-template.md) |
| 🔁 **Coding Pattern Pack** | Required structure for algorithm pattern packs | [coding-pattern-pack-template.md](coding-pattern-pack-template.md) |
| 🤖 **GenAI Concept Pack** | Required structure for GenAI concept docs | [genai-concept-template.md](genai-concept-template.md) |
| 🧩 **GenAI LLD Project Pack** | Required structure for GenAI LLD project packs | [genai-lld-project-template.md](genai-lld-project-template.md) |
| 🧠 **GenAI HLD Project Pack** | Required structure for GenAI HLD project packs | [genai-hld-project-template.md](genai-hld-project-template.md) |
| 💬 **Salary Negotiation Practice** | Time-boxed rubric, scoring, and checklist for offer-stage negotiation drills | [practice-salary-negotiation.md](practice-salary-negotiation.md) |
| 🧾 **Salary Negotiation Mock Scorecard** | Structured worksheet for logging rounds, risks, and debrief actions | [salary-negotiation-mock-scorecard.md](salary-negotiation-mock-scorecard.md) |
| 🧠 **HLD Core Concepts Practice** | Time-boxed rubric for CAP/sharding/hashing/capacity judgment drills | [practice-hld-core-concepts.md](practice-hld-core-concepts.md) |
| 🤖 **GenAI HLD Practice** | Time-boxed rubric, scoring, and checklist for GenAI SD interviews | [practice-genai-hld.md](practice-genai-hld.md) |

### 🏆 Coach Answers

Example "strong answer" outlines for flagship problems — hidden by default in the portal:

| Solution | Problem Type | Link |
|----------|-------------|------|
| Parking Lot | LLD | [solutions/lld-parking-lot.md](../../solutions/lld-parking-lot.md) |
| Behavioral Big Three | Behavioral | [solutions/behavioral-big-three.md](../../solutions/behavioral-big-three.md) |
| Salary Negotiation Coach Answer | Interview Prep | [solutions/salary-negotiation-coach-answer.md](../../solutions/salary-negotiation-coach-answer.md) |
| URL Shortener | HLD | [solutions/hld-url-shortener.md](../../solutions/hld-url-shortener.md) |
| Core Concepts Scaling Judgment | HLD Concept Drill | [solutions/hld-core-concepts-scaling-judgment.md](../../solutions/hld-core-concepts-scaling-judgment.md) |
| Document Q&A (RAG) | GenAI HLD | [solutions/genai-hld-document-qa-rag.md](../../solutions/genai-hld-document-qa-rag.md) |

---

## 🎯 How to Use Templates

### For Practice

1. **Copy the template** to a new file
2. **Name it** after the problem (e.g., `parking-lot.md`)
3. **Set a timer** (45-60 minutes)
4. **Fill in each section** as you design
5. **Compare** with provided solutions in the repo
6. **Note differences** and areas for improvement

### For Real Interviews

1. **Internalize the structure** - Know the phases by heart
2. **Use as mental framework** - Guide your thinking
3. **Cover each section systematically** - Don't skip steps
4. **Adapt as needed** - Not all sections apply to all problems

---

## 📋 Template Structure

### LLD Template Covers:

| Section | Purpose |
|---------|---------|
| Requirements | Clarify scope and constraints |
| Core Entities | Identify classes/objects |
| Relationships | Map how entities connect |
| Design Patterns | Choose applicable patterns |
| Class Design | Attributes, methods, responsibilities |
| Edge Cases | Validation, errors, concurrency |
| Optimization | Time/space complexity |
| Class Diagram | Visual representation |

### HLD Template Covers:

| Section | Purpose |
|---------|---------|
| Requirements | Functional + non-functional |
| Estimation | QPS, storage, bandwidth |
| API Design | Core endpoints |
| Data Model | Schema and database choice |
| Architecture | Components and data flow |
| Deep Dives | Scaling, caching, key algorithms |
| Trade-offs | Design decisions and alternatives |
| Follow-up | Handle common questions |

---

## 📌 Tips for Using Templates

### Do's ✅

- **Understand the flow** - Know why each section exists
- **Practice with timing** - Use templates under time pressure
- **Fill completely** - Don't skip sections during practice
- **Review after** - Compare with solutions and note gaps
- **Customize** - Adapt sections for specific problems

### Don'ts ❌

- **Don't memorize blindly** - Understand the purpose
- **Don't be rigid** - Adapt to the problem and interviewer
- **Don't skip sections** - Each section is there for a reason
- **Don't rush** - Quality over quantity

---

## 🔄 Practice Workflow

```
1. Choose a problem from repo
   ├── LLD: [02-lld-projects/](../../02-lld-projects/)
   └── HLD: [04-hld-projects/](../../04-hld-projects/)

2. Copy appropriate template

3. Set timer (45-60 min)

4. Fill out template sections

5. Compare with solution

6. Note improvements for next time
```

---

## 📈 Track Your Progress

After each practice session, note:

- [ ] Time spent on each section
- [ ] Sections that were difficult
- [ ] Concepts to review
- [ ] Patterns used correctly/incorrectly
- [ ] Trade-offs discussed

---

## 🔗 Related Resources

- [HOW-TO-APPROACH.md](../../02-lld-projects/HOW-TO-APPROACH.md) - LLD methodology
- [DESIGN-TEMPLATE.md](../../04-hld-projects/DESIGN-TEMPLATE.md) - HLD methodology
- [lld-checklist.md](../interview-tips/lld-checklist.md) - LLD interview checklist
- [hld-checklist.md](../interview-tips/hld-checklist.md) - HLD interview checklist

---

*Use these templates to build muscle memory for interviews! 💪*
