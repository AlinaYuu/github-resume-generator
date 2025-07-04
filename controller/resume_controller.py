from flask import request, jsonify, Blueprint
from service.github_service import fetch_github_data, fetch_github_profile, fetch_readme, enrich_repos_with_details
from service.llm_service import ask_llm
from service.repo_filter_service import filter_repos
from util.prompt_utils import build_prompt
from flask import make_response
from fpdf import FPDF
import io
resume_controller = Blueprint("resume_controller", __name__)


@resume_controller.route("/repos", methods=["GET"])
def repos():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username not found"}), 400

    repos = fetch_github_data(username)
    return jsonify(repos)


@resume_controller.route("/filter_repos", methods=["GET"])
def filtered_repos():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username not found"}), 400

    repos = fetch_github_data(username)
    filtered = filter_repos(repos)
    print(f"После фильтрации: {len(filtered)}")
    return jsonify(filtered)

@resume_controller.route("/generate_resume", methods=["GET"])
def generate_resume():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "username not found"}), 400

    profile = fetch_github_profile(username)
    all_repos = fetch_github_data(username)
    enriched_repos = enrich_repos_with_details(username, all_repos)
    print(f"После обогащения: {len(enriched_repos)}")
    top_repos = filter_repos(enriched_repos)

    prompt = build_prompt(username=username, repos=top_repos, profile=profile, all_repos=enriched_repos)

    result = ask_llm(prompt)

    return jsonify({"resume": result})


@resume_controller.route("/to_pdf", methods=["POST"])
def to_pdf():
    data = request.get_json()
    resume_text = data.get("resume")

    if not resume_text:
        return jsonify({"error": "No resume text provided"}), 400

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("ArialUnicode", "", fname="arial.ttf", uni=True)
    pdf.set_font("ArialUnicode", size=12)

    for line in resume_text.splitlines():
        pdf.multi_cell(0, 10, line)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers.set("Content-Type", "application/pdf")
    response.headers.set("Content-Disposition", "attachment", filename="resume.pdf")
    return response


