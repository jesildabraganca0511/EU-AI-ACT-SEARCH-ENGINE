import json
import time 

from .retrieval_generation import ask



EVAL_QUESTIONS = [
    {
        "question": "What are the requirements for high-risk AI systems?",
        "ground_truth": (
            "High-risk AI systems must meet requirements including risk "
            "management (Article 9), data governance (Article 10), "
            "technical documentation (Article 11), transparency and "
            "provision of information to deployers (Article 13), human "
            "oversight (Article 14), and accuracy, robustness and "
            "cybersecurity (Article 15)."
        ),
    },
    {
        "question": "What AI systems are classified as high-risk under Annex III?",
        "ground_truth": (
            "Annex III lists high-risk use cases including biometric "
            "identification, management of critical infrastructure, "
            "education and vocational training, employment and worker "
            "management, access to essential services, law enforcement, "
            "migration and border control, and administration of justice."
        ),
    },
    {
        "question": "What penalties apply for non-compliance with the AI Act?",
        "ground_truth": (
            "Penalties vary by violation type, with the highest fines "
            "reaching up to 35 million EUR or 7% of global annual "
            "turnover for violations involving prohibited AI practices."
        ),
    },
    {
        "question": "What is required in the technical documentation for high-risk AI systems?",
        "ground_truth": (
            "Annex IV specifies the technical documentation requirements, "
            "including a general description of the system, detailed "
            "design specifications, and information on monitoring, "
            "functioning and control of the system."
        ),
    },
    {
        "question": "What obligations do providers of general-purpose AI models have?",
        "ground_truth": (
            "Providers of general-purpose AI models must maintain "
            "technical documentation, provide information to downstream "
            "providers, and comply with EU copyright law, among other "
            "obligations set out in the relevant articles."
        ),
    },
    {
        "question": "Are AI systems used for social scoring by governments allowed?",
        "ground_truth": (
            "No -- AI systems used for social scoring of natural persons "
            "by public authorities are listed among the prohibited AI "
            "practices under the Act."
        ),
    },
    {
        "question": "What AI practices are completely banned under the AI Act?",
        "ground_truth": (
            "Article 5 bans eight AI practices outright, including "
            "subliminal or manipulative techniques that cause significant "
            "harm, exploitation of vulnerabilities related to age, "
            "disability or social/economic situation, social scoring by "
            "public authorities, untargeted scraping of facial images to "
            "build recognition databases, emotion inference in workplaces "
            "or schools, and real-time remote biometric identification in "
            "public spaces for law enforcement (with narrow exceptions)."
        ),
    },
    {
        "question": "Can facial recognition data be scraped from the internet to build a database?",
        "ground_truth": (
            "No -- Article 5 prohibits the untargeted scraping of facial "
            "images from the internet or CCTV footage to create or expand "
            "facial recognition databases."
        ),
    },
    {
        "question": "Do chatbots need to disclose that users are talking to an AI?",
        "ground_truth": (
            "Yes -- under Article 50(1), providers of AI systems intended "
            "to interact directly with natural persons, including "
            "chatbots and virtual assistants, must design them so that "
            "users are informed they are interacting with an AI system, "
            "unless this is already obvious from the context."
        ),
    },
    {
        "question": "What are the obligations around AI-generated deepfakes?",
        "ground_truth": (
            "Under Article 50(4), deployers of AI systems that generate "
            "deepfakes must disclose that the content has been "
            "artificially generated or manipulated, with limited "
            "exceptions such as artistic or satirical works."
        ),
    },
    {
        "question": "Is emotion recognition allowed in the workplace?",
        "ground_truth": (
            "Generally no -- Article 5 prohibits AI systems that infer "
            "emotions in workplace or educational settings, except for "
            "narrow medical or safety-related reasons."
        ),
    },
    {
        "question": "What penalties apply for violating the transparency obligations in Article 50?",
        "ground_truth": (
            "Non-compliance with transparency obligations such as those "
            "in Article 50 can lead to fines of up to 15 million EUR or "
            "3% of global annual turnover, whichever is higher -- lower "
            "than the penalties for prohibited practices under Article 5."
        ),
    },
    {
        "question": "How does the AI Act define an AI system?",
        "ground_truth": (
            "Article 3 defines an AI system as a machine-based system "
            "designed to operate with varying levels of autonomy, that "
            "may exhibit adaptiveness after deployment, and that infers "
            "from input to generate outputs such as predictions, content, "
            "recommendations or decisions that can influence physical or "
            "virtual environments."
        ),
    },
    {
        "question": "What is a fundamental rights impact assessment and when is it required?",
        "ground_truth": (
            "A fundamental rights impact assessment, required under "
            "Article 27, must be carried out by certain deployers of "
            "high-risk AI systems (such as public bodies) before putting "
            "the system into use, to assess the impact on fundamental "
            "rights."
        ),
    },
    {
        "question": "What is a regulatory sandbox under the AI Act?",
        "ground_truth": (
            "AI regulatory sandboxes, addressed in Articles 57-58, are "
            "controlled environments established by national authorities "
            "that allow providers to develop, train, and test innovative "
            "AI systems under regulatory supervision before market "
            "placement."
        ),
    },
    {
        "question": "What additional obligations apply to general-purpose AI models with systemic risk?",
        "ground_truth": (
            "Under Article 51-55, general-purpose AI models classified as "
            "having systemic risk face additional obligations beyond "
            "standard GPAI requirements, including model evaluation, "
            "adversarial testing, tracking and reporting serious "
            "incidents, and ensuring adequate cybersecurity protection."
        ),
    },
    {
        "question": "Do providers need to monitor high-risk AI systems after they're placed on the market?",
        "ground_truth": (
            "Yes -- Article 72 requires providers to establish a "
            "post-market monitoring system to actively collect and "
            "analyse data on the performance of high-risk AI systems "
            "throughout their lifecycle."
        ),
    },
    {
        "question": "What is a conformity assessment and when do high-risk AI systems need one?",
        "ground_truth": (
            "A conformity assessment, addressed in Article 43, is the "
            "process by which a provider demonstrates a high-risk AI "
            "system meets the Act's requirements before it can be placed "
            "on the market -- either through internal control or "
            "involvement of a notified body, depending on the use case."
        ),
    },
]

EVAL_QUESTION_LIMIT = 5
 

def run_eval_set():
    results = []
    for item in EVAL_QUESTIONS[:EVAL_QUESTION_LIMIT]:
        print(f"Running: {item['question']}")
        try:
            result = ask(item["question"])
            results.append({
                "question": result["query"],
                "answer": result["answer"],
                "contexts": result["contexts"],
                "ground_truth": item["ground_truth"],
            })
        except Exception as e:
            print(f"  FAILED: {e}")

        time.sleep(13)   # 5 requests/minute = 1 every 12s minimum; 13s gives headroom

        with open("eval_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
 
 
if __name__ == "__main__":
    run_eval_set()    

